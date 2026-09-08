"""등고선을 CAD가 바로 읽는 DXF로 쓴다."""

from __future__ import annotations

from pathlib import Path

import ezdxf
from ezdxf.enums import TextEntityAlignment

from .config import LayerScheme, Settings
from .contours import Contour, label_positions
from .dem import Dem

# DXF 헤더의 단위 코드. 6 = 미터
INSUNITS_METERS = 6


def _setup_layers(doc, scheme: LayerScheme) -> None:
    for spec in (scheme.minor, scheme.major, scheme.label, scheme.border):
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
