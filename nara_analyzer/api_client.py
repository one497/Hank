"""나라장터 공공데이터포털 API 클라이언트

공공데이터포털(data.go.kr)의 조달청 나라장터 API를 호출하여
용역 입찰 공고, 개찰 결과 데이터를 조회합니다.

주요 API:
- 나라장터 입찰공고정보 (용역)
- 나라장터 개찰결과정보 (용역)
"""

import time
import logging
from urllib.parse import urlencode

import requests

logger = logging.getLogger(__name__)

# 공공데이터포털 나라장터 API 기본 URL
BASE_URL = "http://apis.data.go.kr/1230000"

# API 엔드포인트
ENDPOINTS = {
    # 용역 입찰공고 목록 조회
    "bid_notice_service": "/BidPublicInfoInfoService04/getBidPblancListInfoServc01",
    # 용역 개찰결과 목록 조회
    "bid_result_service": "/ScsbidInfoService/getScsbidListSttusServc",
}

# 기본 요청 파라미터
DEFAULT_PARAMS = {
    "type": "json",
    "numOfRows": "100",
    "pageNo": "1",
}


class NaraApiClient:
    """나라장터 공공데이터포털 API 클라이언트"""

    def __init__(self, api_key: str, timeout: int = 30, max_retries: int = 3):
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()

    def _request(self, endpoint: str, params: dict) -> dict:
        """API 요청을 수행하고 JSON 응답을 반환합니다.

        공공데이터포털 API의 ServiceKey는 이미 URL 인코딩된 상태로 제공되므로,
        requests의 params 자동 인코딩을 사용하면 이중 인코딩이 발생합니다.
        따라서 ServiceKey는 URL에 직접 붙이고, 나머지 파라미터만 인코딩합니다.
        """
        request_params = {**DEFAULT_PARAMS, **params}

        # ServiceKey는 이미 인코딩된 상태이므로 URL에 직접 삽입
        query_string = urlencode(request_params) + "&ServiceKey=" + self.api_key
        url = BASE_URL + endpoint + "?" + query_string

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.debug("API 요청: %s (시도 %d/%d)", endpoint, attempt, self.max_retries)
                resp = self.session.get(url, timeout=self.timeout)
                resp.raise_for_status()

                data = resp.json()

                # 공공데이터포털 응답 구조 파싱
                response = data.get("response", {})
                header = response.get("header", {})
                result_code = header.get("resultCode", "")

                if result_code != "00":
                    result_msg = header.get("resultMsg", "Unknown error")
                    logger.error("API 오류: [%s] %s", result_code, result_msg)
                    raise ApiError(f"API 오류: [{result_code}] {result_msg}")

                body = response.get("body", {})
                return body

            except requests.exceptions.RequestException as e:
                logger.warning("요청 실패 (시도 %d/%d): %s", attempt, self.max_retries, e)
                if attempt < self.max_retries:
                    wait = 2 ** attempt
                    logger.info("%d초 후 재시도...", wait)
                    time.sleep(wait)
                else:
                    raise ApiError(f"API 요청 실패 (최대 재시도 초과): {e}") from e

    def _fetch_all_pages(self, endpoint: str, params: dict) -> list:
        """모든 페이지의 데이터를 수집합니다."""
        all_items = []
        page = 1
        num_of_rows = int(params.get("numOfRows", 100))

        while True:
            params["pageNo"] = str(page)
            body = self._request(endpoint, params)

            total_count = int(body.get("totalCount", 0))
            items = body.get("items", [])

            if not items:
                break

            # items가 단일 객체일 수 있음
            if isinstance(items, dict):
                items = [items]

            all_items.extend(items)
            logger.info("페이지 %d 조회 완료 (누적: %d/%d건)", page, len(all_items), total_count)

            if len(all_items) >= total_count:
                break

            page += 1
            time.sleep(0.5)  # API 호출 간격 제한

        return all_items

    def get_service_bid_notices(
        self,
        start_date: str,
        end_date: str,
        bsns_reg_no: str = None,
    ) -> list:
        """용역 입찰공고 목록을 조회합니다.

        Args:
            start_date: 검색 시작일 (YYYYMMDD)
            end_date: 검색 종료일 (YYYYMMDD)
            bsns_reg_no: 사업자등록번호 (선택)

        Returns:
            입찰공고 목록
        """
        params = {
            "inqryDiv": "1",  # 검색구분: 공고일
            "inqryBgnDt": start_date + "0000",
            "inqryEndDt": end_date + "2359",
            "numOfRows": "100",
        }

        endpoint = ENDPOINTS["bid_notice_service"]
        return self._fetch_all_pages(endpoint, params)

    def get_service_bid_results(
        self,
        bid_ntce_no: str = None,
        start_date: str = None,
        end_date: str = None,
        bsns_reg_no: str = None,
    ) -> list:
        """용역 개찰(투찰) 결과를 조회합니다.

        Args:
            bid_ntce_no: 입찰공고번호 (선택)
            start_date: 검색 시작일 (YYYYMMDD, 선택)
            end_date: 검색 종료일 (YYYYMMDD, 선택)
            bsns_reg_no: 사업자등록번호 (선택)

        Returns:
            개찰결과 목록
        """
        params = {
            "numOfRows": "100",
        }

        if bid_ntce_no:
            params["bidNtceNo"] = bid_ntce_no
        if start_date and end_date:
            params["inqryDiv"] = "1"
            params["inqryBgnDt"] = start_date + "0000"
            params["inqryEndDt"] = end_date + "2359"
        if bsns_reg_no:
            params["bsnsDivCd"] = bsns_reg_no

        endpoint = ENDPOINTS["bid_result_service"]
        return self._fetch_all_pages(endpoint, params)


class ApiError(Exception):
    """나라장터 API 호출 오류"""
    pass
