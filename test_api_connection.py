#!/usr/bin/env python3
"""나라장터 API 연결 테스트 스크립트

로컬 환경에서 실행하여 API 키 및 엔드포인트 정상 동작 여부를 확인합니다.

사용법:
    python test_api_connection.py
"""

import os
import sys
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NARA_API_KEY")
if not API_KEY:
    print("오류: .env 파일에 NARA_API_KEY를 설정해주세요.")
    sys.exit(1)

BASE_URL = "https://apis.data.go.kr/1230000"

# 테스트할 엔드포인트 목록
TESTS = [
    {
        "name": "용역 개찰결과 (신규 /as/ 경로)",
        "endpoint": "/as/ScsbidInfoService/getOpengResultListInfoServcPPSSrch",
        "params": {
            "type": "json",
            "numOfRows": "3",
            "pageNo": "1",
            "inqryDiv": "1",
            "inqryBgnDt": "202503010000",
            "inqryEndDt": "202503252359",
        },
    },
    {
        "name": "용역 개찰결과 (구버전 경로)",
        "endpoint": "/ScsbidInfoService/getScsbidListSttusServc",
        "params": {
            "type": "json",
            "numOfRows": "3",
            "pageNo": "1",
            "inqryDiv": "1",
            "inqryBgnDt": "202503010000",
            "inqryEndDt": "202503252359",
        },
    },
    {
        "name": "용역 입찰공고 (신규 /as/ 경로)",
        "endpoint": "/as/BidPublicInfoInfoService04/getBidPblancListInfoServc01",
        "params": {
            "type": "json",
            "numOfRows": "3",
            "pageNo": "1",
            "inqryDiv": "1",
            "inqryBgnDt": "202503010000",
            "inqryEndDt": "202503252359",
        },
    },
    {
        "name": "공공데이터개방표준서비스 - 용역 낙찰",
        "endpoint": "/BidPublicInfoInfoService04/getBidPblancListInfoServc01",
        "params": {
            "type": "json",
            "numOfRows": "3",
            "pageNo": "1",
            "inqryDiv": "1",
            "inqryBgnDt": "202503010000",
            "inqryEndDt": "202503252359",
        },
    },
]


def test_endpoint(name: str, endpoint: str, params: dict):
    """단일 엔드포인트를 테스트합니다."""
    query_string = urlencode(params) + "&ServiceKey=" + API_KEY
    url = BASE_URL + endpoint + "?" + query_string

    print(f"\n{'='*60}")
    print(f"테스트: {name}")
    print(f"URL: {BASE_URL}{endpoint}")
    print(f"{'─'*60}")

    try:
        resp = requests.get(url, timeout=15)
        print(f"HTTP 상태코드: {resp.status_code}")

        if resp.status_code == 200:
            try:
                data = resp.json()
                header = data.get("response", {}).get("header", {})
                result_code = header.get("resultCode", "?")
                result_msg = header.get("resultMsg", "?")
                print(f"결과코드: {result_code} ({result_msg})")

                if result_code == "00":
                    body = data.get("response", {}).get("body", {})
                    total = body.get("totalCount", 0)
                    items = body.get("items", [])
                    print(f"총 건수: {total}")
                    print(f"조회된 항목: {len(items) if isinstance(items, list) else '1 (dict)'}건")
                    if items:
                        first = items[0] if isinstance(items, list) else items
                        print(f"첫 번째 항목 키: {list(first.keys())[:10]}")
                    print(">>> 성공!")
                    return True
                else:
                    print(f">>> API 오류 - {result_msg}")
            except ValueError:
                print(f"응답 (텍스트): {resp.text[:500]}")
        else:
            print(f"응답: {resp.text[:300]}")

    except requests.exceptions.RequestException as e:
        print(f"요청 실패: {e}")

    print(">>> 실패")
    return False


def main():
    print("나라장터 API 연결 테스트")
    print(f"API 키: {API_KEY[:10]}...{API_KEY[-10:]}")
    print(f"테스트 대상: {len(TESTS)}개 엔드포인트")

    results = {}
    for test in TESTS:
        ok = test_endpoint(test["name"], test["endpoint"], test["params"])
        results[test["name"]] = ok

    print(f"\n{'='*60}")
    print("테스트 결과 요약")
    print(f"{'─'*60}")
    for name, ok in results.items():
        status = "성공" if ok else "실패"
        print(f"  {'[O]' if ok else '[X]'} {name}: {status}")

    success_count = sum(1 for v in results.values() if v)
    print(f"\n{success_count}/{len(results)}개 성공")

    if success_count == 0:
        print("\n모든 테스트가 실패했습니다. 확인 사항:")
        print("  1. 공공데이터포털에서 아래 서비스의 활용신청이 승인되었는지 확인")
        print("     - 조달청_나라장터 낙찰정보서비스 (15129397)")
        print("     - 조달청_나라장터 입찰공고정보서비스 (15129394)")
        print("  2. API 키가 올바른지 확인 (Encoding 키 사용)")
        print("  3. 활용신청 후 승인까지 1~2시간 소요될 수 있음")


if __name__ == "__main__":
    main()
