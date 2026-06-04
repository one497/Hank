"""정치 성향 판별용 키워드 사전과 점수 계산.

두 개의 축으로 분석한다.

1) 좌우 축 (leftright): -100(진보/좌) ~ 0(중도) ~ +100(보수/우)
2) 정파 축 (factions): 진보·보수 진영 안에서 어느 계파(친문/친명/친윤/친한 등)에
   우호적인지. 각 계파는 지지(pro)·적대(anti) 표현을 가지며 순지지도 = pro - anti.

정파는 트리(부모-자식) 구조다. `factions.json`에 노드를 추가하면 코드 수정 없이
새 갈래가 반영되며, 자식의 매칭은 부모로 자동 집계(roll-up)된다.
(예: '뉴이재명'은 '친명·개딸'의 하위 갈래 → 친명 집계에 더해진다)

모든 매칭은 단순 부분문자열 빈도 기반이므로 맥락을 고려하지 못하는 '대략적 추정'이다.
"""

from __future__ import annotations

import json
import os
import re
from typing import Dict, List, Optional

# ──────────────────────────────────────────────
# 좌우 축 키워드
# ──────────────────────────────────────────────
LEFT_KW: List[str] = [
    "적폐", "적폐청산", "토착왜구", "친일파", "친일", "수구", "검찰개혁", "언론개혁",
    "재벌개혁", "촛불", "촛불혁명", "국정농단", "민주주의", "진보", "노동자", "노조",
    "연대", "불평등", "양극화", "복지", "분배", "공정", "사회적약자", "소수자",
    "평화", "남북", "한반도평화", "기득권", "특권층", "검찰독재", "검찰공화국",
    "기레기", "극우", "태극기부대", "내란", "거부권남용",
]
RIGHT_KW: List[str] = [
    "종북", "빨갱이", "좌빨", "좌파", "주사파", "친북", "반국가", "간첩", "체제전복",
    "자유민주주의", "안보", "국가안보", "법치", "시장경제", "성장동력", "규제완화",
    "세금폭탄", "포퓰리즘", "퍼주기", "좌파독재", "선동", "괴담", "떼법",
    "공산주의", "사회주의", "귀족노조", "강성노조", "불법파업", "민노총", "전교조",
    "운동권", "친중", "이적단체", "방탄국회",
]

CAMP_LABEL = {"prog": "진보", "cons": "보수"}

# ──────────────────────────────────────────────
# 정파 트리 로드 (factions.json)
# ──────────────────────────────────────────────
_FACTIONS_PATH = os.path.join(os.path.dirname(__file__), "factions.json")


def _load_factions() -> Dict[str, dict]:
    with open(_FACTIONS_PATH, encoding="utf-8") as f:
        data = json.load(f)
    factions: Dict[str, dict] = {}
    for node in data["factions"]:
        factions[node["id"]] = {
            "name": node["name"],
            "camp": node["camp"],
            "parent": node.get("parent"),
            "pro": node.get("pro", []),
            "anti": node.get("anti", []),
            "opposes": node.get("opposes", []),
        }
    return factions


FACTIONS: Dict[str, dict] = _load_factions()

# 부모 -> 자식 id 목록
CHILDREN: Dict[str, List[str]] = {}
for _fid, _f in FACTIONS.items():
    if _f["parent"]:
        CHILDREN.setdefault(_f["parent"], []).append(_fid)


def _count(keywords: List[str], text: str) -> Dict[str, int]:
    """단일 키워드 목록에 대해 출현 횟수를 센다(긴 키워드 우선, 중복 구간 소거)."""
    found: Dict[str, int] = {}
    work = text
    for kw in sorted(keywords, key=len, reverse=True):
        if re.search(re.escape(kw), work):
            found[kw] = len(re.findall(re.escape(kw), work))
            work = re.sub(re.escape(kw), "￿", work)
    return found


def _scan_factions(text: str) -> Dict[str, Dict[str, Dict[str, int]]]:
    """모든 정파 키워드를 전역적으로 한 번에 스캔한다.

    긴 키워드부터 매칭해 구간을 소거하므로, 자식의 긴 표현('뉴이재명')이
    부모의 짧은 표현('이재명')에 중복 집계되지 않는다.
    """
    entries = []  # (keyword, faction_id, polarity)
    for fid, f in FACTIONS.items():
        for kw in f["pro"]:
            entries.append((kw, fid, "pro"))
        for kw in f["anti"]:
            entries.append((kw, fid, "anti"))
    entries.sort(key=lambda e: len(e[0]), reverse=True)

    res: Dict[str, Dict[str, Dict[str, int]]] = {
        fid: {"pro": {}, "anti": {}} for fid in FACTIONS
    }
    work = text
    for kw, fid, pol in entries:
        if re.search(re.escape(kw), work):
            res[fid][pol][kw] = len(re.findall(re.escape(kw), work))
            work = re.sub(re.escape(kw), "￿", work)
    return res


def _leftright_label(score: int, total: int) -> str:
    if total == 0:
        return "판단 보류"
    a = abs(score)
    side = "진보/좌" if score < 0 else "보수/우"
    if a >= 60:
        return f"뚜렷한 {side}"
    if a >= 25:
        return f"약한 {side}"
    return "중도/혼재"


def _rolled_net(fid: str, own_net: Dict[str, int]) -> int:
    """자신 + 모든 하위 갈래의 순지지도를 합산(roll-up)."""
    total = own_net.get(fid, 0)
    for child in CHILDREN.get(fid, []):
        total += _rolled_net(child, own_net)
    return total


def analyze_text(text: str) -> dict:
    """텍스트의 좌우·정파 성향을 분석한다."""
    text = text or ""

    # 1) 좌우 축
    left = _count(LEFT_KW, text)
    right = _count(RIGHT_KW, text)
    l_sum = sum(left.values())
    r_sum = sum(right.values())
    lr_total = l_sum + r_sum
    lr_score = 0 if lr_total == 0 else round((r_sum - l_sum) / lr_total * 100)

    # 2) 정파 축 (전역 스캔 후 노드별 집계)
    scan = _scan_factions(text)
    own_net: Dict[str, int] = {}
    nodes: Dict[str, dict] = {}
    for fid, f in FACTIONS.items():
        pro = scan[fid]["pro"]
        anti = scan[fid]["anti"]
        pro_sum, anti_sum = sum(pro.values()), sum(anti.values())
        net = pro_sum - anti_sum
        own_net[fid] = net
        nodes[fid] = {
            "id": fid, "name": f["name"], "camp": f["camp"], "parent": f["parent"],
            "pro": pro_sum, "anti": anti_sum, "net": net,
            "matched": {**{k: v for k, v in pro.items()},
                        **{f"{k}(비하)": -v for k, v in anti.items()}},
        }

    # roll-up 순지지도
    for fid, node in nodes.items():
        node["rolled"] = _rolled_net(fid, own_net)
        node["parent_name"] = FACTIONS[node["parent"]]["name"] if node["parent"] else None

    # 좌우 성향과 일치하는 진영만 정파 판단에 사용
    camp = None
    if lr_score <= -10:
        camp = "prog"
    elif lr_score >= 10:
        camp = "cons"

    def in_camp(n):
        return camp is None or n["camp"] == camp

    # 키워드가 검출된 노드(진영 일치)만 노출
    detected = [n for n in nodes.values()
                if in_camp(n) and (n["pro"] or n["anti"])]
    detected.sort(key=lambda n: (n["parent"] is not None, -n["net"]))

    # 우세 가문(top-level) = roll-up 순지지도 최대, 그 안의 활성 하위 갈래
    families = [n for n in nodes.values()
                if n["parent"] is None and in_camp(n) and n["rolled"] > 0]
    families.sort(key=lambda n: n["rolled"], reverse=True)
    dominant = families[0] if families else None
    subbranch = None
    if dominant:
        subs = [nodes[c] for c in CHILDREN.get(dominant["id"], [])
                if nodes[c]["net"] > 0]
        subs.sort(key=lambda n: n["net"], reverse=True)
        subbranch = subs[0] if subs else None

    divergence = _detect_divergence(nodes, in_camp)

    return {
        "leftright": {
            "score": lr_score, "left": l_sum, "right": r_sum, "total": lr_total,
            "label": _leftright_label(lr_score, lr_total),
            "matched": {"left": left, "right": right},
        },
        "factions": {
            "list": detected,
            "dominant": dominant,
            "subbranch": subbranch,
            "divergence": divergence,
        },
    }


def _detect_divergence(nodes: Dict[str, dict], in_camp) -> Optional[dict]:
    """같은 진영 안에서 대립 정파가 동시에 두드러지면 '분기점'으로 표시.

    상위 가문 간 대립은 roll-up 순지지도로 판단한다.
    """
    positive = {fid: n for fid, n in nodes.items()
                if in_camp(n) and n["parent"] is None and n["rolled"] > 0}
    for fid, n in positive.items():
        for opp_id in FACTIONS[fid].get("opposes", []):
            opp = positive.get(opp_id)
            if not opp:
                continue
            weak, strong = sorted([n["rolled"], opp["rolled"]])
            if strong > 0 and weak >= strong * 0.5:
                pair = sorted([n, opp], key=lambda x: x["rolled"], reverse=True)
                return {
                    "camp": CAMP_LABEL[n["camp"]],
                    "factions": [pair[0]["name"], pair[1]["name"]],
                    "note": f"{CAMP_LABEL[n['camp']]} 진영 안에서 "
                            f"{pair[0]['name']} vs {pair[1]['name']} 로 갈라지는 분기점",
                }
    return None
