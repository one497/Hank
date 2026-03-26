# 나라장터 용역 투찰률 분석 도구

나라장터(KONEPS) 공공데이터포털 API를 활용하여 **등록된 사업자등록번호별 용역 투찰률**을 분석하는 도구입니다.

## 기능

- 사업자등록번호 기반 용역 입찰 참여 내역 조회
- **투찰률 분석**: 투찰금액 / 예정가격 × 100
- 업체별 낙찰률, 평균 투찰률, 순위 통계
- 투찰률 구간별 분포 분석
- 복수 업체 비교 분석
- CSV 파일 내보내기 (요약 + 상세)

## 사전 준비

### 1. API 키 발급

[공공데이터포털](https://www.data.go.kr)에서 아래 API의 활용 신청이 필요합니다:

- **조달청 나라장터 입찰공고정보서비스** (용역)
- **조달청 나라장터 개찰결과정보서비스** (용역)

### 2. 환경 설정

```bash
# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일에 발급받은 API 키 입력
```

## 사용법

```bash
# 단일 업체 분석
python -m nara_analyzer.main --reg-no 1234567890 --start 20250101 --end 20251231

# 복수 업체 비교 분석
python -m nara_analyzer.main --reg-no 1234567890,9876543210 --start 20250101 --end 20251231

# CSV 파일로 결과 내보내기
python -m nara_analyzer.main --reg-no 1234567890 --start 20250101 --end 20251231 --output output/result.csv

# 상세 투찰 기록까지 내보내기
python -m nara_analyzer.main --reg-no 1234567890 --start 20250101 --end 20251231 --output output/result.csv --export-detail

# 상세 로그 출력
python -m nara_analyzer.main --reg-no 1234567890 --start 20250101 --end 20251231 -v
```

### 옵션

| 옵션 | 필수 | 설명 |
|------|------|------|
| `--reg-no` | O | 사업자등록번호 (콤마 구분 복수 입력 가능) |
| `--start` | O | 조회 시작일 (YYYYMMDD) |
| `--end` | O | 조회 종료일 (YYYYMMDD) |
| `--output` | X | 결과 CSV 파일 경로 |
| `--export-detail` | X | 상세 투찰 기록 CSV 내보내기 |
| `--api-key` | X | API 키 (미지정 시 환경변수 사용) |
| `-v` | X | 상세 로그 출력 |

## 분석 항목

### 업체별 분석

| 항목 | 설명 |
|------|------|
| 총 투찰 건수 | 해당 기간 내 입찰 참여 총 건수 |
| 낙찰 건수 | 낙찰(수주) 성공 건수 |
| 낙찰률 | 낙찰건수 / 투찰건수 × 100 |
| 평균 투찰률 | 투찰금액 / 예정가격의 평균 |
| 최저/최고 투찰률 | 투찰률 범위 |
| 투찰률 표준편차 | 투찰 전략의 일관성 지표 |
| 평균 순위 | 입찰 순위 평균 |
| 투찰률 구간별 분포 | 5% 단위 히스토그램 |

## 프로젝트 구조

```
Hank/
├── nara_analyzer/
│   ├── __init__.py         # 패키지 초기화
│   ├── api_client.py       # 나라장터 API 클라이언트
│   ├── analyzer.py         # 투찰률 분석 로직
│   └── main.py             # CLI 메인 실행 모듈
├── .env.example            # 환경변수 예시
├── .gitignore
├── requirements.txt
└── README.md
```
