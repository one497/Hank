"""정치 성향 판별용 키워드 사전과 점수 계산.

두 개의 축으로 분석한다.

1) 좌우 축 (leftright): -100(진보/좌) ~ 0(중도) ~ +100(보수/우)
2) 정파 축 (factions): 진보·보수 진영 안에서 어느 계파(친문/친명/친윤/친한 등)에
   우호적인지. 각 계파는 지지(pro) 표현과 적대(anti) 표현을 가지며
   순지지도 = pro - anti 로 계산한다.

모든 매칭은 단순 부분문자열 빈도 기반이므로 맥락을 고려하지 못하는 '대략적 추정'이다.
"""

from __future__ import annotations

import re
from typing import Dict, List

# ──────────────────────────────────────────────
# 좌우 축 키워드
# 각 진영에서 자주 쓰거나 그 진영을 옹호/대변하는 표현 위주
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

# ──────────────────────────────────────────────
# 정파(계파) 축
#   camp: "prog"(진보) | "cons"(보수)
#   pro : 지지/소속 정체성을 드러내는 표현
#   anti: 해당 계파를 비하/공격할 때 쓰이는 표현 (상대 진영/계파가 사용)
#   opposes: 같은 진영 안에서 대립하는 계파 id (분기점 판단용)
# ──────────────────────────────────────────────
FACTIONS: Dict[str, dict] = {
    # ── 진보 진영 ──────────────────────────────
    "chinmun": {
        "name": "친문 (문재인계)", "camp": "prog",
        "pro": [
            "친문", "문재인", "문통", "문심", "문파", "이니", "달님", "재인이형",
            "노무현정신", "깨시민", "양정철", "탁현민", "임종석", "김경수",
            "노짱", "부엉이바위", "친노", "친문계", "더문",
        ],
        "anti": ["대깨문", "문빠", "달창", "문죄인", "문재앙", "문크예거"],
        "opposes": ["chinmyung"],
    },
    "chinmyung": {
        "name": "친명·개딸 (이재명계)", "camp": "prog",
        "pro": [
            "친명", "이재명", "개딸", "명심", "뉴이재명", "잼잼", "이묘", "명룡",
            "재명이형", "정청래", "최강욱", "김어준", "양문석", "장경태", "친명계",
            "명팸", "이대명", "민주당원", "명나라",
        ],
        "anti": ["명팔이", "찢", "찢재명", "찢죄명", "대깨명", "혜경궁", "혜경궁김씨", "흉노"],
        "opposes": ["chinmun", "binmyung"],
    },
    "binmyung": {
        "name": "비명·반명", "camp": "prog",
        "pro": [
            "비명", "반명", "이낙연", "김부겸", "박지현", "원칙과상식", "이상민",
            "조응천", "이원욱", "김종민", "설훈", "홍영표", "새로운미래", "비명계",
            "낙연", "친낙",
        ],
        "anti": ["수박", "수박색출", "수박깨기", "수박파"],
        "opposes": ["chinmyung"],
    },
    "chocook": {
        "name": "친조국 (조국혁신당)", "camp": "prog",
        "pro": [
            "조국혁신당", "조국혁신", "조국", "조작가", "황운하", "차규근",
            "신장식", "조국당", "조국대표",
        ],
        "anti": ["조로남불", "조적조"],
        "opposes": [],
    },
    # ── 보수 진영 ──────────────────────────────
    "chinyoon": {
        "name": "친윤 (윤석열계)", "camp": "cons",
        "pro": [
            "친윤", "윤석열", "윤핵관", "윤심", "윤어게인", "권성동", "이철규",
            "장제원", "추경호", "윤상현", "친윤계", "윤짱", "석열이형",
        ],
        "anti": ["굥", "윤바보", "기미가요", "윤두창", "술석열", "쩍벌", "윤석열차", "도이치"],
        "opposes": ["chinhan"],
    },
    "chinhan": {
        "name": "친한 (한동훈계)", "camp": "cons",
        "pro": [
            "친한", "한동훈", "한동훈팬", "여의도사투리", "댕동훈", "장동혁",
            "김종혁", "박정훈", "친한계", "한판", "동훈이형", "한동프로",
        ],
        "anti": ["한심당", "배신자한동훈", "깐죽", "한칼"],
        "opposes": ["chinyoon"],
    },
    "chinpark": {
        "name": "친박 (박근혜계)", "camp": "cons",
        "pro": [
            "친박", "박근혜", "태극기", "탄핵무효", "박사모", "황교안", "조원진",
            "우리공화당", "진박", "근혜님", "탄기국",
        ],
        "anti": ["닭근혜", "박그네", "순실", "길라임"],
        "opposes": [],
    },
    "junseok": {
        "name": "이준석계 (개혁신당)", "camp": "cons",
        "pro": [
            "이준석", "개혁신당", "유승민", "천아용인", "허은아", "천하람",
            "양향자", "이준석계", "준스기", "준표형은아님",
        ],
        "anti": ["개쩌리", "이준상"],
        "opposes": ["chinyoon"],
    },
    "ahncs": {
        "name": "안철수계 (중도·보수)", "camp": "cons",
        "pro": ["안철수", "안랩", "철수형", "새정치", "안철수계"],
        "anti": ["간철수", "안찰스", "MB아바타"],
        "opposes": [],
    },
}

CAMP_LABEL = {"prog": "진보", "cons": "보수"}


def _count(keywords: List[str], text: str) -> Dict[str, int]:
    """키워드별 출현 횟수를 센다.

    긴 키워드부터 매칭하고 매칭된 구간을 소거하여, 짧은 키워드가
    긴 키워드 안에서 중복 집계되는 것을 막는다.
    (예: '조국혁신당'을 먼저 세면 그 안의 '조국'은 다시 세지 않는다)
    """
    found: Dict[str, int] = {}
    work = text
    for kw in sorted(keywords, key=len, reverse=True):
        matches = re.findall(re.escape(kw), work)
        if matches:
            found[kw] = len(matches)
            work = re.sub(re.escape(kw), "￿", work)  # 매칭 구간 소거
    return found


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

    # 2) 정파 축
    factions = []
    for fid, f in FACTIONS.items():
        pro = _count(f["pro"], text)
        anti = _count(f["anti"], text)
        pro_sum = sum(pro.values())
        anti_sum = sum(anti.values())
        net = pro_sum - anti_sum
        if pro_sum or anti_sum:
            factions.append({
                "id": fid,
                "name": f["name"],
                "camp": f["camp"],
                "pro": pro_sum,
                "anti": anti_sum,
                "net": net,
                "matched": {**{k: v for k, v in pro.items()},
                            **{f"{k}(비하)": -v for k, v in anti.items()}},
            })

    factions.sort(key=lambda x: x["net"], reverse=True)

    # 전체 좌우 성향과 일치하는 진영만 정파 판단에 사용한다.
    # (예: 보수 커뮤니티가 '이재명'을 비판하며 언급한 것을 친명 지지로 오인하지 않도록)
    camp = None
    if lr_score <= -10:
        camp = "prog"
    elif lr_score >= 10:
        camp = "cons"
    relevant = [f for f in factions if camp is None or f["camp"] == camp]

    # 진영 내 우세 계파 + 분기점(같은 진영 내 대립 계파가 동시에 강할 때)
    dominant = next((f for f in relevant if f["net"] > 0), None)
    divergence = _detect_divergence(relevant)

    return {
        "leftright": {
            "score": lr_score,
            "left": l_sum,
            "right": r_sum,
            "total": lr_total,
            "label": _leftright_label(lr_score, lr_total),
            "matched": {"left": left, "right": right},
        },
        "factions": {
            "list": relevant,
            "all": factions,
            "dominant": dominant,
            "divergence": divergence,
        },
    }


def _detect_divergence(factions: List[dict]) -> dict | None:
    """같은 진영 안에서 대립 계파가 동시에 두드러지면 '분기점'으로 표시."""
    by_id = {f["id"]: f for f in factions if f["net"] > 0}
    for fid, f in by_id.items():
        for opp_id in FACTIONS[fid].get("opposes", []):
            opp = by_id.get(opp_id)
            if not opp:
                continue
            weak, strong = sorted([f["net"], opp["net"]])
            # 약한 쪽이 강한 쪽의 50% 이상이면 의미 있는 갈라짐으로 판단
            if strong > 0 and weak >= strong * 0.5:
                pair = sorted([f, opp], key=lambda x: x["net"], reverse=True)
                return {
                    "camp": CAMP_LABEL[f["camp"]],
                    "factions": [pair[0]["name"], pair[1]["name"]],
                    "note": f"{CAMP_LABEL[f['camp']]} 진영 안에서 "
                            f"{pair[0]['name']} vs {pair[1]['name']} 로 갈라지는 분기점",
                }
    return None
