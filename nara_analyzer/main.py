"""나라장터 용역 투찰률 분석 - 메인 실행 모듈

사용법:
    python -m nara_analyzer.main --reg-no 1234567890 --start 20250101 --end 20251231
    python -m nara_analyzer.main --reg-no 1234567890,9876543210 --start 20250101 --end 20251231 --output result.csv
"""

import argparse
import logging
import os
import sys

from dotenv import load_dotenv

from .api_client import NaraApiClient, ApiError
from .analyzer import ServiceBidAnalyzer

load_dotenv()


def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def parse_args():
    parser = argparse.ArgumentParser(
        description="나라장터 API 기반 사업자등록번호별 용역 투찰률 분석 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # 단일 업체 분석
  python -m nara_analyzer.main --reg-no 1234567890 --start 20250101 --end 20251231

  # 복수 업체 비교 분석
  python -m nara_analyzer.main --reg-no 1234567890,9876543210 --start 20250101 --end 20251231

  # CSV 파일로 결과 내보내기
  python -m nara_analyzer.main --reg-no 1234567890 --start 20250101 --end 20251231 --output result.csv

  # 요약 및 상세 데이터 모두 내보내기
  python -m nara_analyzer.main --reg-no 1234567890 --start 20250101 --end 20251231 --output result.csv --export-detail
        """,
    )

    parser.add_argument(
        "--reg-no",
        required=True,
        help="분석 대상 사업자등록번호 (콤마로 구분하여 복수 입력 가능, 예: 1234567890,9876543210)",
    )
    parser.add_argument(
        "--start",
        required=True,
        help="조회 시작일 (YYYYMMDD 형식, 예: 20250101)",
    )
    parser.add_argument(
        "--end",
        required=True,
        help="조회 종료일 (YYYYMMDD 형식, 예: 20251231)",
    )
    parser.add_argument(
        "--output",
        help="결과를 저장할 CSV 파일 경로 (미지정 시 콘솔 출력만)",
    )
    parser.add_argument(
        "--export-detail",
        action="store_true",
        help="상세 투찰 기록도 CSV로 내보내기 (--output 필요)",
    )
    parser.add_argument(
        "--api-key",
        help="공공데이터포털 API 키 (미지정 시 환경변수 NARA_API_KEY 사용)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="상세 로그 출력",
    )

    return parser.parse_args()


def main():
    args = parse_args()
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    # API 키 확인
    api_key = args.api_key or os.getenv("NARA_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("오류: API 키가 설정되지 않았습니다.")
        print("  --api-key 옵션 또는 환경변수 NARA_API_KEY를 설정해주세요.")
        print("  API 키는 https://www.data.go.kr 에서 발급받을 수 있습니다.")
        sys.exit(1)

    # 사업자등록번호 파싱
    reg_nos = [r.strip().replace("-", "") for r in args.reg_no.split(",")]
    for reg_no in reg_nos:
        if not reg_no.isdigit() or len(reg_no) != 10:
            print(f"오류: 올바르지 않은 사업자등록번호입니다: {reg_no}")
            print("  사업자등록번호는 10자리 숫자여야 합니다 (예: 1234567890 또는 123-45-67890)")
            sys.exit(1)

    # 날짜 검증
    for date_val, label in [(args.start, "시작일"), (args.end, "종료일")]:
        if not date_val.isdigit() or len(date_val) != 8:
            print(f"오류: 올바르지 않은 {label}입니다: {date_val}")
            print(f"  YYYYMMDD 형식으로 입력해주세요 (예: 20250101)")
            sys.exit(1)

    if args.start > args.end:
        print("오류: 시작일이 종료일보다 늦습니다.")
        sys.exit(1)

    # API 클라이언트 및 분석기 초기화
    client = NaraApiClient(api_key=api_key)
    analyzer = ServiceBidAnalyzer(api_client=client)

    print(f"\n나라장터 용역 투찰률 분석")
    print(f"분석 대상: {len(reg_nos)}개 업체")
    print(f"조회 기간: {args.start} ~ {args.end}")
    print(f"{'─' * 50}\n")

    try:
        # 분석 수행
        analyses = analyzer.fetch_and_analyze(
            bsns_reg_nos=reg_nos,
            start_date=args.start,
            end_date=args.end,
        )

        # 리포트 출력
        report = analyzer.generate_report(analyses)
        print(report)

        # CSV 내보내기
        if args.output:
            os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)

            # 요약 데이터
            summary_df = analyzer.export_summary_dataframe(analyses)
            summary_path = args.output
            summary_df.to_csv(summary_path, index=False, encoding="utf-8-sig")
            print(f"요약 결과 저장: {summary_path}")

            # 상세 데이터
            if args.export_detail:
                detail_df = analyzer.export_to_dataframe(analyses)
                base, ext = os.path.splitext(args.output)
                detail_path = f"{base}_detail{ext}"
                detail_df.to_csv(detail_path, index=False, encoding="utf-8-sig")
                print(f"상세 결과 저장: {detail_path}")

        print("\n분석 완료.")

    except ApiError as e:
        logger.error("API 호출 오류: %s", e)
        print(f"\nAPI 오류: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception("예상치 못한 오류 발생")
        print(f"\n오류: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
