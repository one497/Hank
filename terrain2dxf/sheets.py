"""도곽 분할과 표제란.

한 현장을 축척과 용지에 맞춰 여러 매로 나눈다. 기존 도면이
`C-01-02-001~008.현황측량도` 처럼 8매로 되어 있는 그 분할을 자동으로 계산하고,
매 장마다 페이퍼공간 레이아웃과 표제란을 만든다.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math

# 용지 규격 (mm). 가로 방향 기준.
PAPER_SIZES = {
    "A0": (1189.0, 841.0),
    "A1": (841.0, 594.0),
    "A2": (594.0, 420.0),
    "A3": (420.0, 297.0),
}

# 여백 (mm). 왼쪽은 철하는 자리라 넓게 잡는다.
MARGIN_BIND = 25.0
MARGIN_EDGE = 10.0

# 표제란 크기 (mm). 오른쪽 아래에 놓는다.
TITLEBLOCK_W = 180.0
TITLEBLOCK_H = 60.0


@dataclass
class Sheet:
    """도곽 한 장."""

    index: int          # 1부터
    row: int
    col: int
    e0: float
    n0: float
    e1: float
    n1: float
    name: str = ""

    @property
    def width(self) -> float:
        return self.e1 - self.e0

    @property
    def height(self) -> float:
        return self.n1 - self.n0

    @property
    def center(self) -> tuple[float, float]:
        return ((self.e0 + self.e1) / 2.0, (self.n0 + self.n1) / 2.0)

    def corners(self) -> list[tuple[float, float]]:
        return [
            (self.e0, self.n0), (self.e1, self.n0),
            (self.e1, self.n1), (self.e0, self.n1),
        ]


@dataclass
class SheetLayout:
    """현장 전체를 덮는 도곽 배치."""

    sheets: list[Sheet]
    paper: str
    scale_denominator: float
    cover_e: float       # 한 장이 덮는 실제 폭 (m)
    cover_n: float       # 한 장이 덮는 실제 높이 (m)
    draw_w_mm: float     # 도면상 작도 영역 (mm)
    draw_h_mm: float

    @property
    def rows(self) -> int:
        return max((s.row for s in self.sheets), default=0) + 1

    @property
    def cols(self) -> int:
        return max((s.col for s in self.sheets), default=0) + 1

    def describe(self) -> str:
        return (
            f"{self.paper} 1/{self.scale_denominator:g} → "
            f"{len(self.sheets)}매 ({self.cols}열 × {self.rows}행), "
            f"한 장이 {self.cover_e:.0f} × {self.cover_n:.0f} m"
        )


def _scale_denominator(scale: str) -> float:
    """'1/1000' → 1000.0"""
    try:
        left, right = scale.split("/")
        if left.strip() != "1":
            raise ValueError
        return float(right)
    except (ValueError, AttributeError):
        raise ValueError(f"축척 표기를 읽을 수 없습니다: {scale!r} (예: '1/1000')")


def drawable_area(paper: str, reserve_titleblock: bool = True) -> tuple[float, float]:
    """용지에서 여백과 표제란을 뺀 작도 영역 (mm)."""
    if paper not in PAPER_SIZES:
        raise ValueError(f"모르는 용지 규격 {paper!r}. 사용 가능: {', '.join(PAPER_SIZES)}")
    w, h = PAPER_SIZES[paper]
    w -= MARGIN_BIND + MARGIN_EDGE
    h -= MARGIN_EDGE * 2
    if reserve_titleblock:
        # 표제란은 도곽 오른쪽 아래를 차지하므로 가로 폭에서 뺀다.
        w -= TITLEBLOCK_W
    if w <= 0 or h <= 0:
        raise ValueError(f"{paper} 용지는 표제란을 두기에 너무 작습니다.")
    return w, h


def plan(
    bounds: tuple[float, float, float, float],
    scale: str,
    paper: str = "A1",
    overlap: float = 0.0,
    prefix: str = "",
    reserve_titleblock: bool = True,
) -> SheetLayout:
    """전체 범위를 덮는 도곽을 계산한다.

    도곽은 남서쪽에서 시작해 서→동, 남→북 순으로 번호를 매긴다.
    overlap을 주면 인접 도면이 그만큼(m) 겹쳐 경계에서 선이 끊겨 보이지 않는다.
    """
    e0, n0, e1, n1 = bounds
    if e1 <= e0 or n1 <= n0:
        raise ValueError("도곽을 계산할 범위가 비어 있습니다.")

    denom = _scale_denominator(scale)
    draw_w, draw_h = drawable_area(paper, reserve_titleblock)

    # 도면 1 mm = 실제 denom mm = denom/1000 m
    cover_e = draw_w * denom / 1000.0
    cover_n = draw_h * denom / 1000.0

    step_e = cover_e - overlap
    step_n = cover_n - overlap
    if step_e <= 0 or step_n <= 0:
        raise ValueError("겹침이 도곽 크기보다 커서 도면이 무한히 늘어납니다.")

    cols = max(1, math.ceil((e1 - e0) / step_e))
    rows = max(1, math.ceil((n1 - n0) / step_n))

    # 도곽 격자를 현장 중앙에 맞춘다. 그러지 않으면 남는 폭이 모두 북동쪽으로
    # 몰려 마지막 열·행이 거의 빈 도면이 된다.
    span_e = cover_e + (cols - 1) * step_e
    span_n = cover_n + (rows - 1) * step_n
    origin_e = e0 - (span_e - (e1 - e0)) / 2.0
    origin_n = n0 - (span_n - (n1 - n0)) / 2.0

    sheets: list[Sheet] = []
    index = 1
    # 남쪽 행부터 위로 올라가며 번호를 매긴다.
    for row in range(rows):
        for col in range(cols):
            s_e0 = origin_e + col * step_e
            s_n0 = origin_n + row * step_n
            sheet = Sheet(
                index=index, row=row, col=col,
                e0=s_e0, n0=s_n0, e1=s_e0 + cover_e, n1=s_n0 + cover_n,
                name=f"{prefix}{index:03d}" if prefix else f"{index:03d}",
            )
            sheets.append(sheet)
            index += 1

    return SheetLayout(
        sheets=sheets, paper=paper, scale_denominator=denom,
        cover_e=cover_e, cover_n=cover_n, draw_w_mm=draw_w, draw_h_mm=draw_h,
    )


def sheet_range_label(layout: SheetLayout, prefix: str = "") -> str:
    """기존 명명 규칙에 맞춘 파일명 조각.

    도곽이 8매면 '001~008' 처럼, 한 매면 '001' 처럼 돌려준다.
    """
    n = len(layout.sheets)
    if n == 1:
        return f"{prefix}001"
    # 기존 도면이 'C-01-02-001~008' 형식이므로 접두사는 앞쪽에만 붙인다.
    return f"{prefix}001~{n:03d}"
