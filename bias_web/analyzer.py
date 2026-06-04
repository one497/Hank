"""커뮤니티 인기글 수집 + 좌우·정파 분석 결합."""

from __future__ import annotations

from typing import List

from . import lexicon
from .sources import COMMUNITIES, fetch_posts


def analyze_community(community_id: str, name: str | None = None) -> dict:
    """한 커뮤니티의 최근 인기글을 분석한다."""
    posts, source = fetch_posts(community_id)
    text = "\n".join(posts)
    result = lexicon.analyze_text(text)

    return {
        "id": community_id,
        "name": name,
        "source": source,            # "live" | "sample"
        "post_count": len(posts),
        "posts": posts[:10],
        "leftright": result["leftright"],
        "factions": result["factions"],
    }


def analyze_all() -> List[dict]:
    """등록된 모든 커뮤니티를 분석한다."""
    results = []
    for c in COMMUNITIES:
        results.append(analyze_community(c["id"], c["name"]))
    # 진보(좌) -> 보수(우) 순 정렬
    results.sort(key=lambda r: r["leftright"]["score"])
    return results
