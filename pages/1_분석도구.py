"""나라장터 용역 투찰률 분석 - 분석 도구 페이지

기존 분석 기능을 그대로 유지합니다.
"""

import os
import io
from datetime import date, timedelta

import streamlit as st
import pandas as pd
import altair as alt

from dotenv import load_dotenv

from nara_analyzer.api_client import NaraApiClient, ApiError
from nara_analyzer.analyzer import ServiceBidAnalyzer
from nara_analyzer.cache import save_cache, load_cache, clear_cache, get_cache_info

load_dotenv()

# ──────────────────────────────────────────────
# 페이지 설정
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="투찰률 분석 도구 | Hank",
    page_icon="📊",
    layout="wide",
)

# 분석 페이지 상단 스타일
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0a0a 0%, #1a1a2e 100%);
    }
    [data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }
    [data-testid="stSidebar"] .stTextInput label,
    [data-testid="stSidebar"] .stTextArea label,
    [data-testid="stSidebar"] .stDateInput label,
    [data-testid="stSidebar"] .stCheckbox label {
        color: #b0b0b0 !important;
        font-weight: 500;
    }
    .stMetric {
        background: #fafafa;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #eee;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 투찰률 분석 도구")
st.caption("사업자등록번호 기반 용역 입찰 투찰률 · 낙찰률 · 순위 분석")

# ──────────────────────────────────────────────
# 사이드바 입력
# ──────────────────────────────────────────────
with st.sidebar:
    st.header("분석 설정")

    api_key = st.text_input(
        "공공데이터포털 API 키 (Encoding)",
        value=os.getenv("NARA_API_KEY", ""),
        type="password",
        help="https://www.data.go.kr 에서 발급받은 인증키 (Encoding)",
    )

    st.divider()

    reg_no_input = st.text_area(
        "사업자등록번호",
        placeholder="123-45-67890\n987-65-43210",
        help="한 줄에 하나씩 입력 (하이픈 포함/미포함 모두 가능)",
        height=120,
    )

    st.divider()

    col_start, col_end = st.columns(2)
    with col_start:
        start_date = st.date_input(
            "시작일",
            value=date.today() - timedelta(days=365),
        )
    with col_end:
        end_date = st.date_input(
            "종료일",
            value=date.today(),
        )

    st.divider()

    use_demo = st.checkbox("데모 모드 (샘플 데이터)", value=False)
    use_cache = st.checkbox("캐시 사용 (저장된 결과 재활용)", value=True)

    run_btn = st.button("🔍 분석 시작", use_container_width=True, type="primary")

    st.divider()

    # 캐시 관리
    with st.expander("캐시 관리"):
        cache_items = get_cache_info()
        if cache_items:
            st.caption(f"저장된 캐시: {len(cache_items)}건")
            for item in cache_items:
                st.text(
                    f"  {item['사업자등록번호']} | "
                    f"{item['조회기간']} | "
                    f"{item['건수']}건 | {item['저장일']}"
                )
            if st.button("🗑️ 캐시 초기화", use_container_width=True):
                cleared = clear_cache()
                st.success(f"{cleared}개 캐시 삭제 완료")
                st.rerun()
        else:
            st.caption("저장된 캐시가 없습니다.")


# ──────────────────────────────────────────────
# 헬퍼 함수
# ──────────────────────────────────────────────
def parse_reg_nos(text: str) -> list[str]:
    lines = text.strip().splitlines()
    result = []
    for line in lines:
        cleaned = line.strip().replace("-", "")
        if cleaned:
            result.append(cleaned)
    return result


def format_reg_no(reg_no: str) -> str:
    clean = reg_no.replace("-", "")
    if len(clean) == 10:
        return f"{clean[:3]}-{clean[3:5]}-{clean[5:]}"
    return clean


def generate_demo_data(reg_nos: list[str]) -> list[dict]:
    import random
    random.seed(42)

    company_names = {}
    default_names = ["(주)한국정보기술", "(주)대한소프트", "(주)서울시스템", "(주)미래IT", "(주)코리아넷"]
    for i, rno in enumerate(reg_nos):
        company_names[rno] = default_names[i] if i < len(default_names) else f"(주)테스트_{rno[-4:]}"

    notice_names = [
        "2025년 정보시스템 유지관리 용역", "클라우드 전환 컨설팅 용역",
        "빅데이터 분석 플랫폼 구축 용역", "정보보안 관제 용역",
        "전자정부 시스템 고도화 용역", "AI 기반 민원 분석 시스템 개발",
        "스마트시티 통합플랫폼 운영 용역", "공공데이터 개방 시스템 구축",
        "재해복구시스템 구축 용역", "차세대 전산시스템 ISP 수립",
        "네트워크 인프라 유지보수 용역", "홈페이지 재구축 및 운영 용역",
        "모바일 앱 개발 용역", "통합 보안관제센터 운영", "데이터센터 이전 용역",
    ]
    institutions = [
        "조달청", "행정안전부", "과학기술정보통신부", "서울특별시",
        "경기도청", "한국정보화진흥원", "국민건강보험공단", "한국전력공사", "인천광역시",
    ]

    data = []
    for reg_no in reg_nos:
        comp_nm = company_names[reg_no]
        num_bids = random.randint(8, 20)
        for i in range(num_bids):
            base_price = random.randint(50_000_000, 2_000_000_000)
            bid_rate_pct = random.uniform(85.0, 99.5)
            bid_amt = int(base_price * bid_rate_pct / 100)
            rank = random.choices([1, 2, 3, 4, 5, 6, 7, 8], weights=[15, 20, 18, 15, 12, 8, 7, 5])[0]
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            data.append({
                "bidNtceNo": f"2025{random.randint(1000, 9999):04d}{i+1:03d}",
                "bidNtceNm": random.choice(notice_names),
                "bidNtceOrd": "00",
                "bsnsBzoperRegNo": reg_no,
                "prcbdrBizNm": comp_nm,
                "bidprcAmt": str(bid_amt),
                "presmptPrce": str(base_price),
                "bssamt": str(int(base_price * 1.05)),
                "rnk": str(rank),
                "sucsfbidYn": "Y" if rank == 1 else "N",
                "opengDt": f"2025{month:02d}{day:02d}1000",
                "dminsttNm": random.choice(institutions),
            })
    return data


def format_krw(value: float) -> str:
    if value >= 1_0000_0000:
        return f"{value / 1_0000_0000:,.1f}억원"
    elif value >= 1_0000:
        return f"{value / 1_0000:,.0f}만원"
    return f"{value:,.0f}원"


# ──────────────────────────────────────────────
# 분석 실행
# ──────────────────────────────────────────────
if run_btn:
    reg_nos = parse_reg_nos(reg_no_input)
    if not reg_nos:
        st.error("사업자등록번호를 입력해주세요.")
        st.stop()

    for rno in reg_nos:
        if not rno.isdigit() or len(rno) != 10:
            st.error(f"올바르지 않은 사업자등록번호: {rno} (10자리 숫자)")
            st.stop()

    if start_date > end_date:
        st.error("시작일이 종료일보다 늦습니다.")
        st.stop()

    if not use_demo and (not api_key or api_key == "your_api_key_here"):
        st.error("API 키를 입력하거나 데모 모드를 사용해주세요.")
        st.stop()

    start_str = start_date.strftime("%Y%m%d")
    end_str = end_date.strftime("%Y%m%d")

    with st.spinner("분석 중..."):
        try:
            analyzer = ServiceBidAnalyzer(api_client=None)

            if use_demo:
                raw_data = generate_demo_data(reg_nos)
                analyses = analyzer.analyze_from_data(raw_data, reg_nos)
                st.info("데모 모드: 샘플 데이터로 분석 결과를 표시합니다.")
            else:
                client = NaraApiClient(api_key=api_key)
                analyzer = ServiceBidAnalyzer(api_client=client)

                all_raw_data = []
                cached_count = 0
                api_count = 0

                for rno in reg_nos:
                    cached = None
                    if use_cache:
                        cached = load_cache(rno, start_str, end_str)

                    if cached is not None:
                        all_raw_data.extend(cached)
                        cached_count += 1
                    else:
                        results = client.get_service_bid_results(
                            start_date=start_str,
                            end_date=end_str,
                            bsns_reg_no=rno,
                        )
                        all_raw_data.extend(results)
                        api_count += 1
                        save_cache(rno, start_str, end_str, results)

                analyses = analyzer.analyze_from_data(all_raw_data, reg_nos)

                if cached_count > 0:
                    st.success(
                        f"캐시에서 {cached_count}개 업체 로드 완료"
                        + (f", API에서 {api_count}개 업체 신규 조회" if api_count > 0 else "")
                    )
                elif api_count > 0:
                    st.info(f"API에서 {api_count}개 업체 조회 완료 (결과 캐시 저장됨)")

        except ApiError as e:
            st.error(f"API 오류: {e}")
            st.markdown("""
            **해결 방법:**
            1. [공공데이터포털](https://www.data.go.kr)에서 아래 서비스 활용신청 확인
               - 조달청_나라장터 낙찰정보서비스
               - 조달청_나라장터 입찰공고정보서비스
            2. API 키는 **Encoding** 키를 사용하세요
            3. 활용신청 후 승인까지 1~2시간 소요될 수 있습니다
            """)
            st.stop()
        except Exception as e:
            st.error(f"오류 발생: {e}")
            st.stop()

    # ──────────────────────────────────────────
    # 결과 표시
    # ──────────────────────────────────────────
    st.header("업체별 분석 결과")

    for reg_no, analysis in analyses.items():
        with st.container(border=True):
            st.subheader(f"{analysis.comp_nm} ({format_reg_no(reg_no)})")

            if analysis.total_bids == 0:
                st.warning("해당 기간 내 투찰 데이터가 없습니다.")
                continue

            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("총 투찰건수", f"{analysis.total_bids:,}건")
            col2.metric("낙찰건수", f"{analysis.total_wins:,}건")
            col3.metric("낙찰률", f"{analysis.win_rate:.1f}%")
            col4.metric("평균 투찰률", f"{analysis.avg_bid_rate:.2f}%")
            col5.metric("평균 순위", f"{analysis.avg_rank:.1f}위")

            col_a, col_b = st.columns(2)
            col_a.metric("총 투찰금액", format_krw(analysis.total_bid_amt))
            col_b.metric("총 낙찰금액", format_krw(analysis.total_win_amt))

            st.markdown("**투찰률 상세**")
            stat_col1, stat_col2, stat_col3 = st.columns(3)
            stat_col1.metric("최저 투찰률", f"{analysis.min_bid_rate:.2f}%")
            stat_col2.metric("최고 투찰률", f"{analysis.max_bid_rate:.2f}%")
            stat_col3.metric("표준편차", f"{analysis.std_bid_rate:.4f}")

            if analysis.bid_rate_distribution:
                st.markdown("**투찰률 구간별 분포**")
                dist_df = pd.DataFrame(
                    list(analysis.bid_rate_distribution.items()),
                    columns=["구간", "건수"],
                )
                st.bar_chart(dist_df.set_index("구간"))

            if analysis.bid_records:
                records_sorted = sorted(analysis.bid_records, key=lambda r: r.bid_date)
                trend_df = pd.DataFrame({
                    "개찰일": [r.bid_date[:8] for r in records_sorted],
                    "투찰률(%)": [r.bid_rate for r in records_sorted],
                    "공고명": [r.bid_ntce_nm for r in records_sorted],
                    "낙찰": ["낙찰" if r.is_winner else "미낙찰" for r in records_sorted],
                })
                trend_df["순번"] = range(len(trend_df))

                st.markdown("**투찰률 추이**")

                line = alt.Chart(trend_df).mark_line(
                    color="#4A90D9", strokeWidth=2
                ).encode(
                    x=alt.X("순번:Q", title="투찰 순서", axis=alt.Axis(labelAngle=0)),
                    y=alt.Y("투찰률(%):Q", scale=alt.Scale(zero=False), title="투찰률 (%)"),
                    tooltip=["개찰일", "공고명", "투찰률(%)", "낙찰"],
                )

                points_all = alt.Chart(trend_df).mark_circle(
                    size=40, color="#4A90D9"
                ).encode(
                    x="순번:Q",
                    y="투찰률(%):Q",
                    tooltip=["개찰일", "공고명", "투찰률(%)", "낙찰"],
                )

                win_df = trend_df[trend_df["낙찰"] == "낙찰"]
                points_win = alt.Chart(win_df).mark_circle(
                    size=200, color="#FF4B4B"
                ).encode(
                    x="순번:Q",
                    y="투찰률(%):Q",
                    tooltip=["개찰일", "공고명", "투찰률(%)", "낙찰"],
                )

                chart = (line + points_all + points_win).properties(height=350)
                st.altair_chart(chart, use_container_width=True)

    if len(analyses) > 1:
        st.header("업체간 비교")

        compare_data = []
        for analysis in analyses.values():
            compare_data.append({
                "업체명": analysis.comp_nm,
                "사업자등록번호": format_reg_no(analysis.bsns_reg_no),
                "투찰건수": analysis.total_bids,
                "낙찰건수": analysis.total_wins,
                "낙찰률(%)": analysis.win_rate,
                "평균투찰률(%)": analysis.avg_bid_rate,
                "평균순위": analysis.avg_rank,
                "총투찰금액": analysis.total_bid_amt,
            })
        compare_df = pd.DataFrame(compare_data)
        st.dataframe(compare_df, use_container_width=True, hide_index=True)

        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.markdown("**평균 투찰률 비교**")
            chart_df = compare_df[["업체명", "평균투찰률(%)"]].set_index("업체명")
            st.bar_chart(chart_df)
        with chart_col2:
            st.markdown("**낙찰률 비교**")
            chart_df2 = compare_df[["업체명", "낙찰률(%)"]].set_index("업체명")
            st.bar_chart(chart_df2)

    st.header("상세 투찰 기록")
    detail_df = analyzer.export_to_dataframe(analyses)

    if not detail_df.empty:
        st.dataframe(
            detail_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "투찰금액": st.column_config.NumberColumn(format="₩%d"),
                "예정가격": st.column_config.NumberColumn(format="₩%d"),
                "기초금액": st.column_config.NumberColumn(format="₩%d"),
                "투찰률(%)": st.column_config.NumberColumn(format="%.2f%%"),
            },
        )

        st.header("데이터 다운로드")
        dl_col1, dl_col2 = st.columns(2)

        with dl_col1:
            summary_df = analyzer.export_summary_dataframe(analyses)
            csv_summary = summary_df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                label="요약 결과 다운로드 (CSV)",
                data=csv_summary,
                file_name="투찰률분석_요약.csv",
                mime="text/csv",
                use_container_width=True,
            )

        with dl_col2:
            csv_detail = detail_df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                label="상세 기록 다운로드 (CSV)",
                data=csv_detail,
                file_name="투찰률분석_상세.csv",
                mime="text/csv",
                use_container_width=True,
            )
    else:
        st.info("표시할 투찰 기록이 없습니다.")

else:
    st.markdown("""
    ### 사용 방법

    1. **사이드바**에서 공공데이터포털 API 키를 입력하세요
    2. 분석할 **사업자등록번호**를 한 줄에 하나씩 입력
    3. **조회 기간**을 설정하세요
    4. **분석 시작** 버튼 클릭

    > API 키가 없으면 **데모 모드**를 체크하여 샘플 데이터로 테스트할 수 있습니다.

    ---

    ### 분석 항목

    | 지표 | 설명 |
    |------|------|
    | **투찰률** | 투찰금액 / 예정가격 x 100 |
    | **낙찰률** | 낙찰건수 / 투찰건수 x 100 |
    | **평균 순위** | 입찰 순위 평균 |
    | **구간별 분포** | 투찰률 5% 단위 히스토그램 |
    | **투찰률 추이** | 시간순 투찰률 변화 |
    """)
