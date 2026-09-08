"""등고선을 CAD가 바로 읽는 DXF로 쓴다."""

from __future__ import annotations

from pathlib import Path

import logging

import ezdxf
from ezdxf.enums import TextEntityAlignment

from .config import LayerScheme, Settings
from .contours import Contour, label_positions
from .dem import Dem

log = logging.getLogger(__name__)

# DXF 헤더의 단위 코드. 6 = 미터
INSUNITS_METERS = 6


def _setup_layers(doc, scheme: LayerScheme) -> None:
    for spec in scheme.all_specs():
        if spec.name in doc.layers:
            continue
        doc.layers.add(spec.name, color=spec.color, lineweight=spec.lineweight)


def write(
    contours: list[Contour],
    dem: Dem,
    settings: Settings,
    out_path: str | Path,
    scheme: LayerScheme | None = None,
    flatten: bool = False,
    spots=None,
    sheet_layout=None,
    overlays: list[str] | None = None,
) -> Path:
    """등고선 목록을 DXF 파일로 저장하고 그 경로를 돌려준다.

    flatten=True면 모든 등고선의 Z를 0으로 눕힌다. 평면도에 참조도면으로
    끼워 넣을 때 쓰는, 손으로 만들던 'z값0' 사본에 해당한다.
    """
    scheme = scheme or LayerScheme()
    preset = settings.preset()
    out_path = Path(out_path)

    doc = ezdxf.new("R2010", setup=True)
    doc.header["$INSUNITS"] = INSUNITS_METERS
    _setup_layers(doc, scheme)
    msp = doc.modelspace()

    for c in contours:
        spec = scheme.major if c.is_major else scheme.minor
        msp.add_lwpolyline(
            c.points,
            format="xy",
            dxfattribs={
                "layer": spec.name,
                "elevation": 0.0 if flatten else c.elevation,
                "closed": c.closed,
            },
        )

    for elevation, pos, angle in label_positions(contours, settings):
        text = msp.add_text(
            f"{elevation:g}",
            height=preset.text_height,
            rotation=angle,
            dxfattribs={"layer": scheme.label.name},
        )
        text.set_placement(
            (float(pos[0]), float(pos[1]), 0.0 if flatten else elevation),
            align=TextEntityAlignment.MIDDLE_CENTER,
        )

    if spots:
        add_spot_heights(msp, spots, settings, scheme)

    if overlays:
        from .overlay import merge

        for path in overlays:
            merge(doc, path, scheme.overlay.name)

    if sheet_layout is not None:
        add_sheet_borders(msp, sheet_layout, scheme)
        add_paper_layouts(doc, sheet_layout, settings, scheme)
    else:
        _add_extent_box(msp, dem, scheme, flatten)

    _stamp_metadata(doc, dem, settings)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.saveas(out_path)
    return out_path


def _add_extent_box(msp, dem: Dem, scheme: LayerScheme, flatten: bool) -> None:
    """DEM의 유효 범위를 사각형으로 남겨 정합 확인을 쉽게 한다."""
    e0, n0, e1, n1 = dem.bounds
    msp.add_lwpolyline(
        [(e0, n0), (e1, n0), (e1, n1), (e0, n1)],
        format="xy",
        dxfattribs={"layer": scheme.border.name, "elevation": 0.0, "closed": True},
    )


def _stamp_metadata(doc, dem: Dem, settings: Settings) -> None:
    """어떤 원본에서 어떤 설정으로 만든 도면인지 파일 안에 남긴다.

    무인 실행에서는 나중에 도면만 보고 출처를 되짚을 수 있어야 한다.
    """
    e0, n0, e1, n1 = dem.bounds
    zmin, zmax = dem.zrange
    preset = settings.preset()

    lines = [
        f"원본 DEM: {dem.path.name if dem.path else '미상'}",
        f"좌표계: EPSG:{dem.crs_epsg or settings.epsg}",
        f"격자: {dem.cell:g} m",
        f"범위: E {e0:.1f}~{e1:.1f} / N {n0:.1f}~{n1:.1f}",
        f"표고: {zmin:.2f}~{zmax:.2f} m",
        f"축척: {preset.name} (주곡선 {preset.minor_interval:g} m / 계곡선 {preset.major_interval:g} m)",
        f"지면필터: {'적용' if settings.ground_filter else '미적용'}",
        f"평활 sigma: {settings.smooth_sigma:g}",
    ]
    doc.appids.add("TERRAIN2DXF")
    # 사용자 좌표/설명 필드는 DXF 어디서나 읽히는 곳에 둔다.
    doc.header.custom_vars.append("TERRAIN2DXF", " | ".join(lines))


# ── 표고점 ────────────────────────────────────────────────────────────────

def add_spot_heights(msp, spots, settings: Settings, scheme: LayerScheme) -> int:
    """표고점을 십자 마커와 표고 문자로 기입한다."""
    preset = settings.preset()
    h = preset.text_height
    marker = h * 0.6  # 십자 팔 길이

    for p in spots:
        msp.add_line(
            (p.e - marker, p.n), (p.e + marker, p.n),
            dxfattribs={"layer": scheme.spot.name},
        )
        msp.add_line(
            (p.e, p.n - marker), (p.e, p.n + marker),
            dxfattribs={"layer": scheme.spot.name},
        )

        if settings.spot_coords:
            text = msp.add_mtext(
                p.coord_label.replace("\n", r"\P"),
                dxfattribs={"layer": scheme.spot_text.name, "char_height": h * 0.8},
            )
            text.set_location((p.e + marker * 1.5, p.n + marker * 1.5))
        else:
            text = msp.add_text(
                p.label,
                height=h * 0.8,
                dxfattribs={"layer": scheme.spot_text.name},
            )
            text.set_placement(
                (p.e + marker * 1.5, p.n + marker * 1.5),
                align=TextEntityAlignment.BOTTOM_LEFT,
            )

    return len(spots)


# ── 도곽 ──────────────────────────────────────────────────────────────────

def add_sheet_borders(msp, layout, scheme: LayerScheme) -> None:
    """모델공간에 도곽 경계와 도면번호를 남긴다. 색인도 역할을 한다."""
    for sheet in layout.sheets:
        msp.add_lwpolyline(
            sheet.corners(),
            format="xy",
            dxfattribs={"layer": scheme.border.name, "elevation": 0.0, "closed": True},
        )
        cx, cy = sheet.center
        # 도면번호는 도곽 좌상단 안쪽에 크게 적어 색인도에서 바로 읽히게 한다.
        text = msp.add_text(
            sheet.name,
            height=sheet.height * 0.05,
            dxfattribs={"layer": scheme.border.name},
        )
        text.set_placement(
            (sheet.e0 + sheet.width * 0.05, sheet.n1 - sheet.height * 0.05),
            align=TextEntityAlignment.TOP_LEFT,
        )


def add_paper_layouts(doc, layout, settings: Settings, scheme: LayerScheme) -> int:
    """도곽마다 페이퍼공간 레이아웃과 표제란을 만든다.

    각 레이아웃에는 해당 도곽 범위만 비추는 뷰포트가 하나 놓인다. 모델공간의
    등고선은 실좌표 그대로 두므로, 도면을 나눠도 원본 좌표계가 유지된다.
    """
    from .sheets import MARGIN_BIND, MARGIN_EDGE, PAPER_SIZES, TITLEBLOCK_H, TITLEBLOCK_W

    paper_w, paper_h = PAPER_SIZES[layout.paper]

    existing = [n for n in doc.layouts.names() if n.lower() != "model"]

    for sheet in layout.sheets:
        psp = doc.layouts.new(sheet.name)
        psp.page_setup(size=(paper_w, paper_h), margins=(0, 0, 0, 0), units="mm")

        # 도곽선
        bx0, by0 = MARGIN_BIND, MARGIN_EDGE
        bx1, by1 = paper_w - MARGIN_EDGE, paper_h - MARGIN_EDGE
        psp.add_lwpolyline(
            [(bx0, by0), (bx1, by0), (bx1, by1), (bx0, by1)],
            format="xy",
            dxfattribs={"layer": scheme.border.name, "closed": True},
        )

        # 뷰포트 — 표제란을 뺀 자리에 도곽 범위를 그대로 비춘다.
        vp_w, vp_h = layout.draw_w_mm, layout.draw_h_mm
        vp_cx = bx0 + vp_w / 2.0
        vp_cy = by0 + vp_h / 2.0
        psp.add_viewport(
            center=(vp_cx, vp_cy),
            size=(vp_w, vp_h),
            view_center_point=sheet.center,
            view_height=layout.cover_n,
        )

        _draw_titleblock(psp, sheet, layout, settings, scheme,
                         x1=bx1, y0=by0, w=TITLEBLOCK_W, h=TITLEBLOCK_H)

    # 도곽을 다 만든 뒤에야 기본 레이아웃을 지운다.
    # ezdxf는 페이퍼공간 레이아웃이 최소 하나 남아 있어야 하므로 순서가 중요하다.
    for name in existing:
        try:
            doc.layouts.delete(name)
        except Exception:  # ezdxf 버전에 따라 예외 종류가 다르다
            log.debug("기본 레이아웃 %s 를 지우지 못했습니다", name)

    return len(layout.sheets)


def _draw_titleblock(psp, sheet, layout, settings: Settings, scheme: LayerScheme,
                     x1: float, y0: float, w: float, h: float) -> None:
    """오른쪽 아래 표제란. 회사 양식이 있으면 이 함수만 바꾸면 된다."""
    x0 = x1 - w
    y1 = y0 + h
    lay = {"layer": scheme.titleblock.name}

    psp.add_lwpolyline(
        [(x0, y0), (x1, y0), (x1, y1), (x0, y1)],
        format="xy", dxfattribs={**lay, "closed": True},
    )

    rows = [
        ("현 장 명", settings.project_name or "-"),
        ("도 면 명", settings.drawing_title),
        ("축    척", f"1/{layout.scale_denominator:g}"),
        ("좌 표 계", f"EPSG:{settings.epsg}"),
        ("도면번호", f"{sheet.name} ({sheet.index}/{len(layout.sheets)})"),
        ("작 성 자", settings.surveyor or "-"),
    ]

    row_h = h / len(rows)
    label_w = w * 0.30
    for i, (label, value) in enumerate(rows):
        ry0 = y0 + i * row_h
        psp.add_line((x0, ry0), (x1, ry0), dxfattribs=lay)
        psp.add_line((x0 + label_w, ry0), (x0 + label_w, ry0 + row_h), dxfattribs=lay)

        t1 = psp.add_text(label, height=row_h * 0.4, dxfattribs=lay)
        t1.set_placement(
            (x0 + label_w / 2.0, ry0 + row_h / 2.0), align=TextEntityAlignment.MIDDLE_CENTER
        )
        t2 = psp.add_text(str(value), height=row_h * 0.4, dxfattribs=lay)
        t2.set_placement(
            (x0 + label_w + 3.0, ry0 + row_h / 2.0), align=TextEntityAlignment.MIDDLE_LEFT
        )
