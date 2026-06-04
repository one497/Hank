"""API 응답 캐시 모듈

API 호출 결과를 로컬 JSON 파일로 저장하여
동일한 조건의 재조회를 방지합니다.
"""

import hashlib
import json
import os
import time
import logging

logger = logging.getLogger(__name__)

DEFAULT_CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
CACHE_EXPIRY_DAYS = 7  # 캐시 유효기간 (일)


def _cache_key(reg_no: str, start_date: str, end_date: str) -> str:
    """캐시 키 생성 (사업자번호 + 조회기간)"""
    raw = f"{reg_no}_{start_date}_{end_date}"
    return hashlib.md5(raw.encode()).hexdigest()


def _ensure_cache_dir(cache_dir: str = DEFAULT_CACHE_DIR):
    os.makedirs(cache_dir, exist_ok=True)


def save_cache(
    reg_no: str,
    start_date: str,
    end_date: str,
    data: list[dict],
    cache_dir: str = DEFAULT_CACHE_DIR,
):
    """API 응답 데이터를 캐시 파일로 저장합니다."""
    _ensure_cache_dir(cache_dir)
    key = _cache_key(reg_no, start_date, end_date)
    filepath = os.path.join(cache_dir, f"{key}.json")
    payload = {
        "reg_no": reg_no,
        "start_date": start_date,
        "end_date": end_date,
        "saved_at": time.time(),
        "count": len(data),
        "data": data,
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    logger.info("캐시 저장: %s (%d건) -> %s", reg_no, len(data), filepath)


def load_cache(
    reg_no: str,
    start_date: str,
    end_date: str,
    cache_dir: str = DEFAULT_CACHE_DIR,
    max_age_days: int = CACHE_EXPIRY_DAYS,
) -> list[dict] | None:
    """캐시된 데이터를 불러옵니다. 없거나 만료되면 None 반환."""
    key = _cache_key(reg_no, start_date, end_date)
    filepath = os.path.join(cache_dir, f"{key}.json")

    if not os.path.exists(filepath):
        return None

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            payload = json.load(f)

        # 만료 확인
        saved_at = payload.get("saved_at", 0)
        age_days = (time.time() - saved_at) / 86400
        if age_days > max_age_days:
            logger.info("캐시 만료: %s (%.1f일 경과)", reg_no, age_days)
            os.remove(filepath)
            return None

        logger.info(
            "캐시 적중: %s (%d건, %.1f일 전 저장)",
            reg_no, payload.get("count", 0), age_days,
        )
        return payload.get("data", [])
    except (json.JSONDecodeError, KeyError) as e:
        logger.warning("캐시 파일 손상: %s - %s", filepath, e)
        return None


def clear_cache(cache_dir: str = DEFAULT_CACHE_DIR):
    """모든 캐시 파일을 삭제합니다."""
    if not os.path.exists(cache_dir):
        return 0
    count = 0
    for fname in os.listdir(cache_dir):
        if fname.endswith(".json"):
            os.remove(os.path.join(cache_dir, fname))
            count += 1
    logger.info("캐시 초기화: %d개 파일 삭제", count)
    return count


def get_cache_info(cache_dir: str = DEFAULT_CACHE_DIR) -> list[dict]:
    """캐시 현황 정보를 반환합니다."""
    if not os.path.exists(cache_dir):
        return []
    info = []
    for fname in os.listdir(cache_dir):
        if not fname.endswith(".json"):
            continue
        filepath = os.path.join(cache_dir, fname)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                payload = json.load(f)
            age_days = (time.time() - payload.get("saved_at", 0)) / 86400
            info.append({
                "사업자등록번호": payload.get("reg_no", ""),
                "조회기간": f"{payload.get('start_date', '')} ~ {payload.get('end_date', '')}",
                "건수": payload.get("count", 0),
                "저장일": f"{age_days:.1f}일 전",
            })
        except (json.JSONDecodeError, KeyError):
            continue
    return info
