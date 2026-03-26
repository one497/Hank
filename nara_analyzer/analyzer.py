"""용역 투찰률 분석 모듈

사업자등록번호별 용역 입찰 참여 현황과 투찰률을 분석합니다.

투찰률 = (투찰금액 / 예정가격) × 100
- 투찰금액: 업체가 제출한 입찰 금액
- 예정가격: 발주기관이 설정한 예정가격 (또는 기초금액)
"""

import logging
from dataclasses import dataclass, field
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class BidRecord:
    """개별 투찰 기록"""
    bid_ntce_no: str           # 입찰공고번호
    bid_ntce_nm: str           # 공고명
    bid_ntce_ord: str          # 입찰공고차수
    bsns_reg_no: str           # 사업자등록번호
    comp_nm: str               # 업체명
    bid_amt: float             # 투찰금액
    presmpt_price: float       # 예정가격 (추정가격)
    base_amt: float            # 기초금액
    bid_rate: float            # 투찰률 (%)
    rank: int                  # 순위
    is_winner: bool            # 낙찰 여부
    bid_date: str              # 투찰일시
    dmnd_instt_nm: str         # 수요기관명


@dataclass
class CompanyAnalysis:
    """업체별 분석 결과"""
    bsns_reg_no: str                            # 사업자등록번호
    comp_nm: str                                # 업체명
    total_bids: int = 0                         # 총 투찰 건수
    total_wins: int = 0                         # 낙찰 건수
    win_rate: float = 0.0                       # 낙찰률 (%)
    avg_bid_rate: float = 0.0                   # 평균 투찰률 (%)
    min_bid_rate: float = 0.0                   # 최저 투찰률 (%)
    max_bid_rate: float = 0.0                   # 최고 투찰률 (%)
    std_bid_rate: float = 0.0                   # 투찰률 표준편차
    avg_rank: float = 0.0                       # 평균 순위
    total_bid_amt: float = 0.0                  # 총 투찰금액
    total_win_amt: float = 0.0                  # 총 낙찰금액
    bid_records: list = field(default_factory=list)  # 상세 투찰 기록
    bid_rate_distribution: dict = field(default_factory=dict)  # 투찰률 구간별 분포


class ServiceBidAnalyzer:
    """용역 투찰률 분석기"""

    def __init__(self, api_client):
        self.api_client = api_client

    def fetch_and_analyze(
        self,
        bsns_reg_nos: list[str],
        start_date: str,
        end_date: str,
    ) -> dict[str, CompanyAnalysis]:
        """사업자등록번호 목록에 대해 투찰 데이터를 조회하고 분석합니다.

        Args:
            bsns_reg_nos: 분석 대상 사업자등록번호 목록
            start_date: 조회 시작일 (YYYYMMDD)
            end_date: 조회 종료일 (YYYYMMDD)

        Returns:
            사업자등록번호별 CompanyAnalysis 딕셔너리
        """
        logger.info(
            "분석 시작: %d개 업체, 기간 %s ~ %s",
            len(bsns_reg_nos), start_date, end_date,
        )

        # 1단계: 기간 내 용역 개찰 결과 조회
        all_results = self._fetch_bid_results(start_date, end_date)
        logger.info("총 %d건의 개찰 결과 조회 완료", len(all_results))

        # 2단계: 사업자등록번호별 데이터 필터링 및 파싱
        bid_records = self._parse_bid_records(all_results, bsns_reg_nos)
        logger.info("대상 업체 투찰 기록: %d건", len(bid_records))

        # 3단계: 업체별 분석
        analyses = self._analyze_by_company(bid_records, bsns_reg_nos)

        return analyses

    def analyze_from_data(
        self,
        raw_data: list[dict],
        bsns_reg_nos: list[str],
    ) -> dict[str, CompanyAnalysis]:
        """이미 조회된 원시 데이터로부터 분석을 수행합니다."""
        bid_records = self._parse_bid_records(raw_data, bsns_reg_nos)
        return self._analyze_by_company(bid_records, bsns_reg_nos)

    def _fetch_bid_results(self, start_date: str, end_date: str) -> list:
        """기간 내 용역 개찰 결과를 조회합니다."""
        return self.api_client.get_service_bid_results(
            start_date=start_date,
            end_date=end_date,
        )

    def _parse_bid_records(
        self, raw_results: list, target_reg_nos: list[str]
    ) -> list[BidRecord]:
        """원시 API 응답 데이터를 BidRecord로 파싱합니다."""
        records = []
        target_set = set(self._normalize_reg_no(r) for r in target_reg_nos)

        for item in raw_results:
            reg_no = self._normalize_reg_no(
                str(item.get("bsnsBzoperRegNo", item.get("dminsttBizrno", "")))
            )

            # 대상 업체가 아니면 건너뜀
            if target_set and reg_no not in target_set:
                continue

            try:
                bid_amt = self._safe_float(item.get("bidprcAmt", 0))
                presmpt_price = self._safe_float(
                    item.get("presmptPrce", item.get("plnprc", 0))
                )
                base_amt = self._safe_float(item.get("bssamt", 0))

                # 투찰률 계산: 투찰금액 / 예정가격 × 100
                reference_price = presmpt_price if presmpt_price > 0 else base_amt
                bid_rate = (bid_amt / reference_price * 100) if reference_price > 0 else 0.0

                rank_val = item.get("rnk", item.get("prcbdrRnk", 0))
                is_winner = str(item.get("sucsfbidYn", "N")).upper() == "Y" or int(rank_val or 0) == 1

                record = BidRecord(
                    bid_ntce_no=str(item.get("bidNtceNo", "")),
                    bid_ntce_nm=str(item.get("bidNtceNm", "")),
                    bid_ntce_ord=str(item.get("bidNtceOrd", "")),
                    bsns_reg_no=reg_no,
                    comp_nm=str(item.get("prcbdrBizNm", item.get("bidwinnrNm", ""))),
                    bid_amt=bid_amt,
                    presmpt_price=presmpt_price,
                    base_amt=base_amt,
                    bid_rate=round(bid_rate, 4),
                    rank=int(rank_val or 0),
                    is_winner=is_winner,
                    bid_date=str(item.get("opengDt", item.get("bidClseDt", ""))),
                    dmnd_instt_nm=str(item.get("dminsttNm", "")),
                )
                records.append(record)
            except (ValueError, TypeError) as e:
                logger.warning("레코드 파싱 실패: %s - %s", item.get("bidNtceNo"), e)
                continue

        return records

    def _analyze_by_company(
        self, records: list[BidRecord], bsns_reg_nos: list[str]
    ) -> dict[str, CompanyAnalysis]:
        """업체별 투찰률 분석을 수행합니다."""
        # 사업자등록번호별 그룹핑
        company_records: dict[str, list[BidRecord]] = {}
        for record in records:
            key = record.bsns_reg_no
            if key not in company_records:
                company_records[key] = []
            company_records[key].append(record)

        analyses = {}

        for reg_no in bsns_reg_nos:
            norm_reg_no = self._normalize_reg_no(reg_no)
            recs = company_records.get(norm_reg_no, [])

            if not recs:
                analyses[norm_reg_no] = CompanyAnalysis(
                    bsns_reg_no=norm_reg_no,
                    comp_nm="(데이터 없음)",
                )
                continue

            bid_rates = [r.bid_rate for r in recs if r.bid_rate > 0]
            wins = [r for r in recs if r.is_winner]

            df_rates = pd.Series(bid_rates) if bid_rates else pd.Series([0.0])

            # 투찰률 구간별 분포 (5% 단위)
            distribution = {}
            for rate in bid_rates:
                bucket = f"{int(rate // 5) * 5}-{int(rate // 5) * 5 + 5}%"
                distribution[bucket] = distribution.get(bucket, 0) + 1

            analysis = CompanyAnalysis(
                bsns_reg_no=norm_reg_no,
                comp_nm=recs[0].comp_nm,
                total_bids=len(recs),
                total_wins=len(wins),
                win_rate=round(len(wins) / len(recs) * 100, 2) if recs else 0.0,
                avg_bid_rate=round(df_rates.mean(), 4),
                min_bid_rate=round(df_rates.min(), 4),
                max_bid_rate=round(df_rates.max(), 4),
                std_bid_rate=round(df_rates.std(), 4) if len(df_rates) > 1 else 0.0,
                avg_rank=round(
                    sum(r.rank for r in recs if r.rank > 0)
                    / max(len([r for r in recs if r.rank > 0]), 1),
                    2,
                ),
                total_bid_amt=sum(r.bid_amt for r in recs),
                total_win_amt=sum(r.bid_amt for r in wins),
                bid_records=recs,
                bid_rate_distribution=dict(sorted(distribution.items())),
            )
            analyses[norm_reg_no] = analysis

        return analyses

    def generate_report(self, analyses: dict[str, CompanyAnalysis]) -> str:
        """분석 결과를 텍스트 리포트로 생성합니다."""
        lines = []
        lines.append("=" * 80)
        lines.append("  나라장터 용역 투찰률 분석 리포트")
        lines.append("=" * 80)
        lines.append("")

        for reg_no, analysis in analyses.items():
            lines.append(f"■ 업체명: {analysis.comp_nm}")
            lines.append(f"  사업자등록번호: {self._format_reg_no(reg_no)}")
            lines.append(f"  ─────────────────────────────────────────")
            lines.append(f"  총 투찰 건수:     {analysis.total_bids:>8,}건")
            lines.append(f"  낙찰 건수:        {analysis.total_wins:>8,}건")
            lines.append(f"  낙찰률:           {analysis.win_rate:>8.2f}%")
            lines.append(f"  ─────────────────────────────────────────")
            lines.append(f"  평균 투찰률:      {analysis.avg_bid_rate:>8.2f}%")
            lines.append(f"  최저 투찰률:      {analysis.min_bid_rate:>8.2f}%")
            lines.append(f"  최고 투찰률:      {analysis.max_bid_rate:>8.2f}%")
            lines.append(f"  투찰률 표준편차:  {analysis.std_bid_rate:>8.4f}")
            lines.append(f"  평균 순위:        {analysis.avg_rank:>8.1f}위")
            lines.append(f"  ─────────────────────────────────────────")
            lines.append(f"  총 투찰금액:  {analysis.total_bid_amt:>15,.0f}원")
            lines.append(f"  총 낙찰금액:  {analysis.total_win_amt:>15,.0f}원")

            if analysis.bid_rate_distribution:
                lines.append(f"  ─────────────────────────────────────────")
                lines.append(f"  [투찰률 구간별 분포]")
                for bucket, count in analysis.bid_rate_distribution.items():
                    bar = "█" * count
                    lines.append(f"    {bucket:>10s}: {count:>3d}건 {bar}")

            lines.append("")

        # 업체간 비교 요약
        if len(analyses) > 1:
            lines.append("=" * 80)
            lines.append("  업체간 비교 요약")
            lines.append("=" * 80)
            lines.append("")
            lines.append(
                f"  {'업체명':<20s} {'투찰건수':>8s} {'낙찰건수':>8s} "
                f"{'낙찰률':>8s} {'평균투찰률':>10s} {'평균순위':>8s}"
            )
            lines.append(f"  {'─' * 70}")
            for analysis in analyses.values():
                lines.append(
                    f"  {analysis.comp_nm:<20s} {analysis.total_bids:>8,d} "
                    f"{analysis.total_wins:>8,d} {analysis.win_rate:>7.2f}% "
                    f"{analysis.avg_bid_rate:>9.2f}% {analysis.avg_rank:>7.1f}"
                )
            lines.append("")

        return "\n".join(lines)

    def export_to_dataframe(self, analyses: dict[str, CompanyAnalysis]) -> pd.DataFrame:
        """분석 결과를 pandas DataFrame으로 변환합니다."""
        rows = []
        for analysis in analyses.values():
            for rec in analysis.bid_records:
                rows.append({
                    "사업자등록번호": self._format_reg_no(rec.bsns_reg_no),
                    "업체명": rec.comp_nm,
                    "입찰공고번호": rec.bid_ntce_no,
                    "공고명": rec.bid_ntce_nm,
                    "수요기관": rec.dmnd_instt_nm,
                    "투찰금액": rec.bid_amt,
                    "예정가격": rec.presmpt_price,
                    "기초금액": rec.base_amt,
                    "투찰률(%)": rec.bid_rate,
                    "순위": rec.rank,
                    "낙찰여부": "Y" if rec.is_winner else "N",
                    "개찰일시": rec.bid_date,
                })

        return pd.DataFrame(rows)

    def export_summary_dataframe(self, analyses: dict[str, CompanyAnalysis]) -> pd.DataFrame:
        """업체별 요약 분석 결과를 DataFrame으로 변환합니다."""
        rows = []
        for analysis in analyses.values():
            rows.append({
                "사업자등록번호": self._format_reg_no(analysis.bsns_reg_no),
                "업체명": analysis.comp_nm,
                "총투찰건수": analysis.total_bids,
                "낙찰건수": analysis.total_wins,
                "낙찰률(%)": analysis.win_rate,
                "평균투찰률(%)": analysis.avg_bid_rate,
                "최저투찰률(%)": analysis.min_bid_rate,
                "최고투찰률(%)": analysis.max_bid_rate,
                "투찰률표준편차": analysis.std_bid_rate,
                "평균순위": analysis.avg_rank,
                "총투찰금액": analysis.total_bid_amt,
                "총낙찰금액": analysis.total_win_amt,
            })

        return pd.DataFrame(rows)

    @staticmethod
    def _normalize_reg_no(reg_no: str) -> str:
        """사업자등록번호에서 하이픈을 제거합니다."""
        return reg_no.replace("-", "").strip()

    @staticmethod
    def _format_reg_no(reg_no: str) -> str:
        """사업자등록번호를 XXX-XX-XXXXX 형식으로 포맷합니다."""
        clean = reg_no.replace("-", "").strip()
        if len(clean) == 10:
            return f"{clean[:3]}-{clean[3:5]}-{clean[5:]}"
        return clean

    @staticmethod
    def _safe_float(value) -> float:
        """안전하게 float 변환합니다."""
        try:
            return float(value) if value else 0.0
        except (ValueError, TypeError):
            return 0.0
