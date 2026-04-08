"""슬라이드 데이터(slides_data.SLIDES)를 PowerPoint(.pptx) 파일로 변환합니다.

사용법:
    python build_pptx.py                           # 기본 출력: 용인반도체_용수계획.pptx
    python build_pptx.py output/슬라이드.pptx       # 출력 경로 지정

요구 패키지:
    pip install python-pptx
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Inches, Pt

from slides_data import SLIDES

# ──────────────────────────────────────────────
# 색상 / 폰트 / 레이아웃 상수
# ──────────────────────────────────────────────
BRAND_BLUE = RGBColor(0x1F, 0x6F, 0xB5)
ACCENT_BLUE = RGBColor(0x4A, 0x90, 0xD9)
TEXT_DARK = RGBColor(0x22, 0x22, 0x22)
TEXT_MUTED = RGBColor(0x88, 0x88, 0x88)
CALLOUT_BG = RGBColor(0xE8, 0xF1, 0xFA)
CALLOUT_BORDER = RGBColor(0x4A, 0x90, 0xD9)
TABLE_HEADER_BG = RGBColor(0x1F, 0x6F, 0xB5)
TABLE_HEADER_FG = RGBColor(0xFF, 0xFF, 0xFF)
TABLE_ROW_BG = RGBColor(0xF5, 0xF8, 0xFC)

KO_FONT = "맑은 고딕"  # macOS·Windows·Keynote 모두 한글 잘 표시되는 폰트


# ──────────────────────────────────────────────
# 마크다운 처리 헬퍼 (**bold** 만 지원)
# ──────────────────────────────────────────────
_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")


def _split_runs(text: str) -> list[tuple[str, bool]]:
    """`**굵게**` 패턴을 (텍스트, bold) 튜플 리스트로 변환합니다."""
    runs: list[tuple[str, bool]] = []
    pos = 0
    for m in _BOLD_RE.finditer(text):
        if m.start() > pos:
            runs.append((text[pos : m.start()], False))
        runs.append((m.group(1), True))
        pos = m.end()
    if pos < len(text):
        runs.append((text[pos:], False))
    return runs or [("", False)]


def _apply_runs(
    paragraph,
    text: str,
    *,
    size: int = 18,
    color: RGBColor = TEXT_DARK,
    bold_default: bool = False,
):
    """텍스트를 마크다운 굵게 처리하여 paragraph에 추가합니다."""
    paragraph.clear()
    for run_text, is_bold in _split_runs(text):
        run = paragraph.add_run()
        run.text = run_text
        run.font.size = Pt(size)
        run.font.color.rgb = color
        run.font.bold = bold_default or is_bold
        run.font.name = KO_FONT


def _add_textbox(slide, left, top, width, height) -> object:
    """텍스트박스 shape를 추가하고 text_frame을 반환합니다."""
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    return box, tf


def _set_bg(slide, color: RGBColor) -> None:
    """슬라이드 배경색 설정."""
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color


# ──────────────────────────────────────────────
# 슬라이드 빌더
# ──────────────────────────────────────────────
SLIDE_W = Inches(13.333)  # 16:9
SLIDE_H = Inches(7.5)
MARGIN_X = Inches(0.7)
HEADER_TOP = Inches(0.5)
BODY_TOP = Inches(1.6)
BODY_W = SLIDE_W - 2 * MARGIN_X
BODY_H = SLIDE_H - BODY_TOP - Inches(0.5)


def _add_header_bar(slide) -> None:
    """슬라이드 상단에 브랜드 색상 바를 추가합니다."""
    bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, Inches(0.25)
    )
    bar.fill.solid()
    bar.fill.fore_color.rgb = BRAND_BLUE
    bar.line.fill.background()


def _add_footer(slide, page_num: int, total: int) -> None:
    """슬라이드 푸터: 발표 제목 + 페이지 번호."""
    box, tf = _add_textbox(
        slide,
        MARGIN_X,
        SLIDE_H - Inches(0.45),
        BODY_W,
        Inches(0.35),
    )
    p = tf.paragraphs[0]
    _apply_runs(
        p,
        f"용인반도체클러스터 용수계획 · 재처리수 필요성     |     {page_num} / {total}",
        size=10,
        color=TEXT_MUTED,
    )
    p.alignment = PP_ALIGN.RIGHT


def _add_heading(slide, text: str) -> None:
    """본문 슬라이드 상단의 큰 제목."""
    box, tf = _add_textbox(slide, MARGIN_X, HEADER_TOP, BODY_W, Inches(0.9))
    p = tf.paragraphs[0]
    _apply_runs(p, text, size=28, color=BRAND_BLUE, bold_default=True)
    # 제목 밑줄 라인
    line = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, MARGIN_X, Inches(1.4), Inches(1.0), Emu(28575)
    )
    line.fill.solid()
    line.fill.fore_color.rgb = ACCENT_BLUE
    line.line.fill.background()


def build_cover_slide(prs: Presentation, slide_data: dict, page_num: int, total: int):
    blank = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank)
    _set_bg(slide, RGBColor(0xFA, 0xFC, 0xFF))

    # 좌측 컬러 바
    bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.4), SLIDE_H
    )
    bar.fill.solid()
    bar.fill.fore_color.rgb = BRAND_BLUE
    bar.line.fill.background()

    # 헤드라인
    box, tf = _add_textbox(
        slide, Inches(1.0), Inches(2.4), Inches(11.5), Inches(1.5)
    )
    p = tf.paragraphs[0]
    _apply_runs(
        p,
        slide_data["headline"],
        size=44,
        color=BRAND_BLUE,
        bold_default=True,
    )

    # 서브헤드
    box2, tf2 = _add_textbox(
        slide, Inches(1.0), Inches(3.7), Inches(11.5), Inches(0.8)
    )
    p2 = tf2.paragraphs[0]
    _apply_runs(p2, slide_data["subhead"], size=24, color=ACCENT_BLUE)

    # 구분선
    line = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(4.7), Inches(2.0), Emu(28575)
    )
    line.fill.solid()
    line.fill.fore_color.rgb = ACCENT_BLUE
    line.line.fill.background()

    # 메타
    box3, tf3 = _add_textbox(
        slide, Inches(1.0), Inches(4.9), Inches(11.5), Inches(0.5)
    )
    p3 = tf3.paragraphs[0]
    _apply_runs(p3, slide_data["meta"], size=14, color=TEXT_MUTED)


def build_toc_slide(prs: Presentation, slide_data: dict, page_num: int, total: int):
    blank = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank)
    _add_header_bar(slide)
    _add_heading(slide, "목차")

    box, tf = _add_textbox(slide, MARGIN_X + Inches(0.3), BODY_TOP, BODY_W, BODY_H)
    for i, item in enumerate(slide_data["items"]):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        _apply_runs(p, item, size=22, color=TEXT_DARK)
        p.space_after = Pt(14)

    _add_footer(slide, page_num, total)


def build_content_slide(prs: Presentation, slide_data: dict, page_num: int, total: int):
    blank = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank)
    _add_header_bar(slide)
    _add_heading(slide, slide_data["heading"])

    cursor_top = BODY_TOP

    # 2단 컬럼 레이아웃
    if "columns" in slide_data:
        col_w = (BODY_W - Inches(0.5)) // 2
        for i, col in enumerate(slide_data["columns"]):
            left = MARGIN_X + (col_w + Inches(0.5)) * i
            # 컬럼 제목 박스
            head = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE, left, cursor_top, col_w, Inches(0.55)
            )
            head.fill.solid()
            head.fill.fore_color.rgb = BRAND_BLUE
            head.line.fill.background()
            tf_head = head.text_frame
            tf_head.margin_left = Inches(0.2)
            tf_head.margin_top = Inches(0.05)
            p = tf_head.paragraphs[0]
            _apply_runs(p, col["title"], size=16, color=RGBColor(255, 255, 255), bold_default=True)

            # 컬럼 본문
            body_box, body_tf = _add_textbox(
                slide,
                left + Inches(0.1),
                cursor_top + Inches(0.7),
                col_w - Inches(0.2),
                Inches(4.5),
            )
            for j, item in enumerate(col["items"]):
                p = body_tf.paragraphs[0] if j == 0 else body_tf.add_paragraph()
                _apply_runs(p, "• " + item, size=16, color=TEXT_DARK)
                p.space_after = Pt(10)

        _add_footer(slide, page_num, total)
        return

    # bullets
    body_height = Inches(4.0)
    if "bullets" in slide_data:
        box, tf = _add_textbox(
            slide, MARGIN_X + Inches(0.2), cursor_top, BODY_W - Inches(0.4), body_height
        )
        for i, bullet in enumerate(slide_data["bullets"]):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            stripped = bullet.lstrip()
            indent = bullet.startswith("  ")
            display = stripped if indent else "• " + stripped
            _apply_runs(
                p,
                display,
                size=16 if indent else 17,
                color=TEXT_DARK,
            )
            if indent:
                p.level = 1
            p.space_after = Pt(8)
        cursor_top += body_height

    # 표
    if "table" in slide_data:
        table_data = slide_data["table"]
        rows = len(table_data["rows"]) + 1
        cols = len(table_data["columns"])
        tbl_top = cursor_top - Inches(0.3) if "bullets" in slide_data else cursor_top
        tbl_h = Inches(0.45 * rows + 0.1)
        shape = slide.shapes.add_table(
            rows, cols, MARGIN_X + Inches(0.5), tbl_top, BODY_W - Inches(1.0), tbl_h
        )
        table = shape.table
        # 헤더
        for c, col_name in enumerate(table_data["columns"]):
            cell = table.cell(0, c)
            cell.fill.solid()
            cell.fill.fore_color.rgb = TABLE_HEADER_BG
            tf = cell.text_frame
            tf.paragraphs[0].clear()
            _apply_runs(
                tf.paragraphs[0],
                col_name,
                size=14,
                color=TABLE_HEADER_FG,
                bold_default=True,
            )
            tf.paragraphs[0].alignment = PP_ALIGN.CENTER
        # 데이터 행
        for r, row in enumerate(table_data["rows"], start=1):
            for c, val in enumerate(row):
                cell = table.cell(r, c)
                if r % 2 == 1:
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = TABLE_ROW_BG
                tf = cell.text_frame
                tf.paragraphs[0].clear()
                _apply_runs(tf.paragraphs[0], val, size=13, color=TEXT_DARK)
        cursor_top = tbl_top + tbl_h + Inches(0.15)

    # callout
    if "callout" in slide_data:
        callout_top = SLIDE_H - Inches(1.55)
        callout = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            MARGIN_X,
            callout_top,
            BODY_W,
            Inches(0.95),
        )
        callout.fill.solid()
        callout.fill.fore_color.rgb = CALLOUT_BG
        callout.line.color.rgb = CALLOUT_BORDER
        callout.line.width = Pt(1.5)
        tf = callout.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.25)
        tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.15)
        p = tf.paragraphs[0]
        _apply_runs(p, slide_data["callout"], size=14, color=BRAND_BLUE)

    _add_footer(slide, page_num, total)


def build_closing_slide(prs: Presentation, slide_data: dict, page_num: int, total: int):
    blank = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank)
    _add_header_bar(slide)
    _add_heading(slide, slide_data["heading"])

    # 좌측: 핵심 요약
    half_w = (BODY_W - Inches(0.5)) // 2
    head1 = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, MARGIN_X, BODY_TOP, half_w, Inches(0.5)
    )
    head1.fill.solid()
    head1.fill.fore_color.rgb = BRAND_BLUE
    head1.line.fill.background()
    p = head1.text_frame.paragraphs[0]
    _apply_runs(p, "  핵심 요약", size=14, color=RGBColor(255, 255, 255), bold_default=True)

    box, tf = _add_textbox(
        slide,
        MARGIN_X + Inches(0.1),
        BODY_TOP + Inches(0.65),
        half_w - Inches(0.2),
        Inches(4.0),
    )
    for i, line in enumerate(slide_data["summary"]):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        _apply_runs(p, "• " + line, size=14, color=TEXT_DARK)
        p.space_after = Pt(10)

    # 우측: 제언
    right_left = MARGIN_X + half_w + Inches(0.5)
    head2 = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, right_left, BODY_TOP, half_w, Inches(0.5)
    )
    head2.fill.solid()
    head2.fill.fore_color.rgb = ACCENT_BLUE
    head2.line.fill.background()
    p2 = head2.text_frame.paragraphs[0]
    _apply_runs(p2, "  제언", size=14, color=RGBColor(255, 255, 255), bold_default=True)

    box2, tf2 = _add_textbox(
        slide,
        right_left + Inches(0.1),
        BODY_TOP + Inches(0.65),
        half_w - Inches(0.2),
        Inches(4.0),
    )
    for i, line in enumerate(slide_data["recommendations"]):
        p = tf2.paragraphs[0] if i == 0 else tf2.add_paragraph()
        _apply_runs(p, "• " + line, size=14, color=TEXT_DARK)
        p.space_after = Pt(10)

    # 마무리 메시지 박스
    closing_top = SLIDE_H - Inches(1.5)
    closing = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, MARGIN_X, closing_top, BODY_W, Inches(0.9)
    )
    closing.fill.solid()
    closing.fill.fore_color.rgb = BRAND_BLUE
    closing.line.fill.background()
    tf_c = closing.text_frame
    tf_c.word_wrap = True
    p_c = tf_c.paragraphs[0]
    _apply_runs(
        p_c,
        slide_data["closing"],
        size=18,
        color=RGBColor(255, 255, 255),
        bold_default=True,
    )
    p_c.alignment = PP_ALIGN.CENTER

    _add_footer(slide, page_num, total)


BUILDERS = {
    "cover": build_cover_slide,
    "toc": build_toc_slide,
    "content": build_content_slide,
    "closing": build_closing_slide,
}


def build_presentation(output_path: Path) -> None:
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    total = len(SLIDES)
    for i, slide_data in enumerate(SLIDES, start=1):
        builder = BUILDERS[slide_data["kind"]]
        builder(prs, slide_data, i, total)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(output_path))
    print(f"✓ {total}장 슬라이드 생성 완료: {output_path}")


def main(argv: list[str]) -> None:
    if len(argv) > 1:
        out = Path(argv[1])
    else:
        out = Path("용인반도체_용수계획.pptx")
    build_presentation(out)


if __name__ == "__main__":
    main(sys.argv)
