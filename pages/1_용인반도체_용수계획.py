"""용인반도체클러스터 용수계획 - 재처리수 필요성 (프레젠테이션 슬라이드)

Streamlit multipage 앱의 서브 페이지.
메인 앱(app.py)과 같은 디렉토리에서 `streamlit run app.py` 실행 시
사이드바에서 자동으로 페이지로 선택 가능합니다.

frontend-slides 프레임워크(session_state 기반 슬라이드 네비게이션)를
재사용하여 구성되었습니다.
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# 상위 디렉토리(앱 루트)를 import 경로에 추가하여 slides_data 공유 모듈 사용
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from slides_data import SLIDES  # noqa: E402

# ──────────────────────────────────────────────
# 페이지 설정
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="용인반도체클러스터 용수계획",
    page_icon="💧",
    layout="wide",
)

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
