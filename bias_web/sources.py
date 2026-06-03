"""커뮤니티 인기글 수집 어댑터.

각 커뮤니티는 RSS 피드가 있으면 실시간으로 최신/인기 글을 가져오고,
접속이 실패하면 번들된 샘플 인기글(sample_data)로 폴백한다.

주의: 상당수 커뮤니티는 RSS를 제공하지 않거나 봇 접근을 차단(403/Cloudflare)한다.
따라서 실제 운영 환경에서는 사이트별 파서를 추가하거나, 접근 가능한 피드 URL을
`COMMUNITIES`의 `rss` 항목에 채워 넣어야 한다. 네트워크가 막힌 환경에서는 항상
샘플로 폴백하며, 결과에 `source="sample"` 로 표시된다.
"""

from __future__ import annotations

import urllib.request
import xml.etree.ElementTree as ET
from typing import List, Tuple

from .sample_data import SAMPLE_POSTS

# id -> 메타데이터
#   rss: 접근 가능한 RSS 피드 URL (없으면 None -> 항상 샘플 사용)
COMMUNITIES = [
    {"id": "clien",      "name": "클리앙",            "rss": None},
    {"id": "todayhumor", "name": "오늘의유머",        "rss": None},
    {"id": "fmkorea",    "name": "에펨코리아",        "rss": None},
    {"id": "ilbe",       "name": "일베저장소",        "rss": None},
    {"id": "bobaedream", "name": "보배드림",          "rss": None},
    {"id": "ruliweb",    "name": "루리웹",            "rss": None},
    {"id": "mlbpark",    "name": "MLBPARK",           "rss": None},
    {"id": "theqoo",     "name": "더쿠",              "rss": None},
    {"id": "ppomppu",    "name": "뽐뿌",              "rss": None},
    {"id": "dcbest",     "name": "디시인사이드(실베)", "rss": None},
]

COMMUNITY_BY_ID = {c["id"]: c for c in COMMUNITIES}

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; BiasBot/1.0)"}
_TIMEOUT = 8


def _fetch_rss(url: str, limit: int = 15) -> List[str]:
    """RSS/Atom 피드에서 글 제목(+요약)을 추출한다."""
    req = urllib.request.Request(url, headers=_HEADERS)
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        raw = resp.read()
    root = ET.fromstring(raw)

    titles: List[str] = []
    # RSS 2.0: channel/item/title, Atom: entry/title
    for item in root.iter():
        tag = item.tag.split("}")[-1]
        if tag in ("item", "entry"):
            parts = []
            for child in item:
                ctag = child.tag.split("}")[-1]
                if ctag in ("title", "description", "summary") and child.text:
                    parts.append(child.text.strip())
            if parts:
                titles.append(" ".join(parts))
        if len(titles) >= limit:
            break
    return titles


def fetch_posts(community_id: str) -> Tuple[List[str], str]:
    """커뮤니티의 최근 인기글을 가져온다.

    Returns:
        (글 목록, source) — source 는 "live" 또는 "sample"
    """
    meta = COMMUNITY_BY_ID.get(community_id)
    if meta is None:
        raise KeyError(f"알 수 없는 커뮤니티: {community_id}")

    rss = meta.get("rss")
    if rss:
        try:
            posts = _fetch_rss(rss)
            if posts:
                return posts, "live"
        except Exception:
            # 네트워크 차단/파싱 실패 -> 샘플 폴백
            pass

    return list(SAMPLE_POSTS.get(community_id, [])), "sample"
