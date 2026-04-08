"""용인반도체클러스터 용수계획 - 재처리수 필요성 (프레젠테이션 슬라이드)

Streamlit multipage 앱의 서브 페이지.
메인 앱(app.py)과 같은 디렉토리에서 `streamlit run app.py` 실행 시
사이드바에서 자동으로 페이지로 선택 가능합니다.

frontend-slides 프레임워크(session_state 기반 슬라이드 네비게이션)를
재사용하여 구성되었습니다.
"""

from datetime import date

import pandas as pd
import streamlit as st

# ──────────────────────────────────────────────
# 페이지 설정
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="용인반도체클러스터 용수계획",
    page_icon="💧",
    layout="wide",
)

# ──────────────────────────────────────────────
# 슬라이드 콘텐츠 정의
#
# 각 슬라이드는 dict:
#   - title: 네비게이션 표시용 제목
#   - kind:  "cover" | "toc" | "content" | "closing"
#   - 기타 kind별 필드
# ──────────────────────────────────────────────
SLIDES: list[dict] = [
    {
        "title": "표지",
        "kind": "cover",
        "headline": "용인반도체클러스터 용수계획",
        "subhead": "재처리수(하수 재이용수)의 필요성",
        "meta": f"발표일: {date.today().strftime('%Y. %m. %d.')}",
    },
    {
        "title": "목차",
        "kind": "toc",
        "items": [
            "1. 용인반도체클러스터 개요",
            "2. 반도체 산업의 용수 수요 전망",
            "3. 기존 용수 공급 체계와 한계",
            "4. 재처리수란 무엇인가",
            "5. 재처리수 도입의 필요성",
            "6. 추진 방안 및 국내외 사례",
            "7. 기대효과와 과제",
            "8. 결론 및 제언",
        ],
    },
    {
        "title": "1. 클러스터 개요",
        "kind": "content",
        "heading": "1. 용인반도체클러스터 개요",
        "bullets": [
            "**위치**: 경기도 용인시 일원 (처인구·남사읍 등)",
            "**성격**: 국가첨단전략산업 특화단지 / 세계 최대 규모 반도체 메가 클러스터 목표",
            "**참여 기업**: 삼성전자 시스템반도체 단지, SK하이닉스 용인 클러스터 등",
            "**투자 규모**: 장기 수백조 원대 민간 투자 계획",
            "**가동 일정**: 2030년 전후 단계적 가동 예정",
        ],
        "callout": (
            "국가 경제 및 글로벌 반도체 공급망 관점에서 **안정적인 인프라 확보**, "
            "특히 **용수 공급**이 핵심 성공 조건입니다."
        ),
    },
    {
        "title": "2. 용수 수요",
        "kind": "content",
        "heading": "2. 반도체 산업의 용수 수요 전망",
        "bullets": [
            "반도체 공정은 **초순수(UPW)** 를 웨이퍼 세정·화학처리에 대량 사용",
            "최첨단 Fab 1기당 하루 수만 톤 규모의 공업용수 소모",
            "용인 클러스터 전체 가동 시 **일일 수요가 광역상수도 한 지자체 공급량에 필적**",
            "단계적 Fab 증설에 따라 수요는 **시간 경과에 따라 누적·급증**",
        ],
        "table": {
            "columns": ["구분", "설명"],
            "rows": [
                ["초순수(UPW)", "반도체 공정 전용 고순도 물 (불순물 ppt 단위 제어)"],
                ["공업용수", "냉각·세정·배관 등에 공급되는 일반 공업용 원수"],
                ["총 수요", "Fab 가동 단계에 따라 누적 증가 (수십만 톤/일 규모)"],
            ],
        },
    },
    {
        "title": "3. 공급 한계",
        "kind": "content",
        "heading": "3. 기존 용수 공급 체계와 한계",
        "bullets": [
            "한강수계 **팔당댐** 중심의 광역상수도 의존",
            "생활용수·농업용수 등 기존 수요와 **수자원 경합** 심화",
            "**기후변화**로 인한 가뭄 빈발 → 댐 저수율 변동성 확대",
            "신규 댐 건설·수계 전환은 **사회적 수용성과 사업 기간** 측면에서 한계",
            "기존 광역상수도만으로는 **단일 공급 리스크** 존재",
        ],
        "callout": (
            "⚠️ 단일 수원(水源) 의존 구조로는 **메가 팹의 안정 가동을 담보하기 어렵습니다**. "
            "공급원의 **다변화(Portfolio)** 가 필수입니다."
        ),
    },
    {
        "title": "4. 재처리수 정의",
        "kind": "content",
        "heading": "4. 재처리수란 무엇인가",
        "bullets": [
            "**정의**: 하수처리장 방류수를 고도처리(MBR·RO·UV 등)하여 재이용하는 물",
            "**용도**: 공업용수, 하천유지용수, 농업용수, 조경용수 등",
            "**특징**: 강수량·기온에 좌우되지 않는 **상시 공급 가능 수자원**",
            "**국내외 관례**: `재이용수`, `중수`, `NEWater` 등으로 불림",
        ],
        "table": {
            "columns": ["처리 단계", "기술", "목적"],
            "rows": [
                ["1차", "생물학적 처리 (MBR 등)", "유기물·부유물 제거"],
                ["2차", "막분리 (UF/RO)", "미세입자·염류 제거"],
                ["3차", "UV·오존 산화", "미생물·미량오염물 제거"],
            ],
        },
    },
    {
        "title": "5. 필요성",
        "kind": "content",
        "heading": "5. 재처리수 도입의 필요성",
        "bullets": [
            "**① 용수 다변화**: 팔당 의존도를 낮추고 공급 포트폴리오 구성",
            "**② 기후 리스크 대응**: 강수량과 무관하게 안정적 확보 가능",
            "**③ 수자원 경합 완화**: 생활·농업용수와의 갈등 최소화",
            "**④ 순환경제 기여**: 물 재이용을 통한 자원순환·탄소 저감",
            "**⑤ ESG 부합**: 반도체 기업의 Water Stewardship 경영 요구 충족",
            "**⑥ 인프라 확장성**: 하수처리장 증설·고도화로 점진적 증량 가능",
        ],
        "callout": (
            "💧 재처리수는 **\"날씨에 흔들리지 않는 물\"** 입니다. "
            "기후변화 시대의 반도체 산업에 가장 부합하는 보완 수원입니다."
        ),
    },
    {
        "title": "6. 추진 방안·사례",
        "kind": "content",
        "heading": "6. 추진 방안 및 국내외 사례",
        "bullets": [
            "**추진 방안**",
            "  • 인근 공공하수처리장(화성·용인 등)과 연계한 재이용 체계 구축",
            "  • 고도처리시설(MBR·RO 등) 증설 및 전용 공업용수 관로 건설",
            "  • 수질 안정화를 위한 **2중·3중 백업 체계**",
            "  • 민관 협력(PPP) 및 장기공급계약 체결",
            "**국내외 사례**",
            "  • 🇰🇷 포항·광양 등 산업단지: 공업용수용 재이용 수십 년 운영",
            "  • 🇸🇬 싱가포르 NEWater: 국가 용수 약 40% 이상 재이용수로 충당",
            "  • 🇺🇸 캘리포니아: 가뭄 대응을 위해 공업·농업 재이용 확대",
        ],
    },
    {
        "title": "7. 기대효과·과제",
        "kind": "content",
        "heading": "7. 기대효과와 주요 과제",
        "columns": [
            {
                "title": "✅ 기대효과",
                "items": [
                    "메가 팹의 **안정적 가동** 보장",
                    "광역상수도 부담 완화",
                    "지역 주민·농업과의 **수자원 갈등 최소화**",
                    "ESG·탄소중립 목표 기여",
                    "**물 산업 생태계** 육성",
                ],
            },
            {
                "title": "⚠️ 주요 과제",
                "items": [
                    "**초순수 수준 수질** 확보를 위한 기술 검증",
                    "처리·이송 과정의 **에너지 비용** 및 탄소 footprint",
                    "**요금 체계** 및 공급가격 산정",
                    "**주민 수용성** 및 인식 개선",
                    "**제도·규제** 정비 (재이용수 등급 기준 등)",
                ],
            },
        ],
    },
    {
        "title": "8. 결론",
        "kind": "closing",
        "heading": "8. 결론 및 제언",
        "summary": [
            "용인반도체클러스터의 성공은 **용수의 양(量)과 질(質)의 안정적 확보**에 달려 있습니다.",
            "팔당 중심의 단일 수원만으로는 기후변화·수요 급증 상황에서 리스크가 큽니다.",
            "**재처리수는 기존 광역상수도를 보완하는 핵심 수자원**으로 조속히 제도화·인프라화해야 합니다.",
        ],
        "recommendations": [
            "재처리수 **전용 공급망** 조기 구축 (2020년대 후반 목표)",
            "**고도처리 기술** 국산화 및 실증 지원",
            "**요금·제도** 정비 및 민관 협력 모델 확립",
            "**Water Stewardship** 관점의 거버넌스 수립",
        ],
        "closing": "반도체 강국의 미래는 **\"지속가능한 물\"** 위에 세워집니다. 💧",
    },
]


# ──────────────────────────────────────────────
# 렌더러
# ──────────────────────────────────────────────
def render_cover(slide: dict) -> None:
    st.markdown(
        f"""
        <div style='text-align:center; padding:80px 0 40px 0;'>
            <h1 style='font-size:2.6rem; margin-bottom:0.4em;'>💧 {slide['headline']}</h1>
            <h3 style='color:#4A90D9; font-weight:400; margin-top:0;'>{slide['subhead']}</h3>
            <p style='color:#888; margin-top:2.5em;'>{slide['meta']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_toc(slide: dict) -> None:
    st.markdown("## 📑 목차")
    st.markdown("")
    for item in slide["items"]:
        st.markdown(f"#### {item}")


def render_content(slide: dict) -> None:
    st.markdown(f"## {slide['heading']}")
    st.markdown("")

    # 2단 컬럼 레이아웃
    if "columns" in slide:
        cols = st.columns(len(slide["columns"]))
        for col, col_data in zip(cols, slide["columns"]):
            with col:
                st.markdown(f"### {col_data['title']}")
                for item in col_data["items"]:
                    st.markdown(f"- {item}")
        return

    # 기본 bullet 렌더
    if "bullets" in slide:
        for bullet in slide["bullets"]:
            if bullet.startswith("  •"):
                # 들여쓰기된 항목은 한 단계 들여서 표시
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{bullet.lstrip()}", unsafe_allow_html=True)
            else:
                st.markdown(f"- {bullet}")

    # 표
    if "table" in slide:
        st.markdown("")
        table = slide["table"]
        df = pd.DataFrame(table["rows"], columns=table["columns"])
        st.table(df)

    # 강조 박스
    if "callout" in slide:
        st.markdown("")
        st.info(slide["callout"])


def render_closing(slide: dict) -> None:
    st.markdown(f"## {slide['heading']}")
    st.markdown("")

    st.markdown("### 📌 핵심 요약")
    for line in slide["summary"]:
        st.markdown(f"- {line}")

    st.markdown("")
    st.markdown("### 🎯 제언")
    for rec in slide["recommendations"]:
        st.markdown(f"- {rec}")

    st.markdown("---")
    st.markdown(
        f"<div style='text-align:center; padding:30px 0;'>"
        f"<h3 style='color:#4A90D9;'>{slide['closing']}</h3>"
        f"</div>",
        unsafe_allow_html=True,
    )


RENDERERS = {
    "cover": render_cover,
    "toc": render_toc,
    "content": render_content,
    "closing": render_closing,
}


# ──────────────────────────────────────────────
# 슬라이드 네비게이션
# ──────────────────────────────────────────────
SLIDE_KEY = "yongin_slide_index"

if SLIDE_KEY not in st.session_state:
    st.session_state[SLIDE_KEY] = 0

total = len(SLIDES)
st.session_state[SLIDE_KEY] = max(0, min(st.session_state[SLIDE_KEY], total - 1))
idx = st.session_state[SLIDE_KEY]
current = SLIDES[idx]

# 상단 헤더/진행도
st.caption("프레젠테이션 · frontend-slides")
st.progress(
    (idx + 1) / total,
    text=f"슬라이드 {idx + 1} / {total} — {current['title']}",
)

# 슬라이드 본문
with st.container(border=True):
    RENDERERS[current["kind"]](current)

# 네비게이션 컨트롤
nav_prev, nav_center, nav_next = st.columns([1, 2, 1])

with nav_prev:
    if st.button(
        "⬅️ 이전",
        disabled=(idx == 0),
        use_container_width=True,
        key="yongin_prev",
    ):
        st.session_state[SLIDE_KEY] = max(0, idx - 1)
        st.rerun()

with nav_center:
    titles = [f"{i + 1}. {s['title']}" for i, s in enumerate(SLIDES)]
    selected = st.selectbox(
        "바로가기",
        options=list(range(total)),
        index=idx,
        format_func=lambda i: titles[i],
        key="yongin_jump",
        label_visibility="collapsed",
    )
    if selected != idx:
        st.session_state[SLIDE_KEY] = selected
        st.rerun()

with nav_next:
    if st.button(
        "다음 ➡️",
        disabled=(idx == total - 1),
        use_container_width=True,
        key="yongin_next",
    ):
        st.session_state[SLIDE_KEY] = min(total - 1, idx + 1)
        st.rerun()

# 사이드바 안내
with st.sidebar:
    st.markdown("### 🎞️ 프레젠테이션")
    st.caption(
        "용인반도체클러스터 용수계획의 재처리수 필요성에 대한 슬라이드 자료입니다. "
        "이전/다음 버튼 또는 바로가기로 슬라이드를 이동할 수 있습니다."
    )
    st.divider()
    st.markdown(f"**총 슬라이드**: {total}장")
    st.markdown(f"**현재**: {idx + 1}번 — {current['title']}")
