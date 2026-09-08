"""DEM 한 장을 도면 한 벌로 바꾸는 전체 흐름."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path
import json
import logging
import time

from . import contours as contour_mod
from . import dem as dem_mod
from . import points as points_mod
from . import preview as preview_mod
from . import sheets as sheets_mod
from .config import Settings
from .dxf import write as write_dxf

log = logging.getLogger(__name__)


@dataclass
class Result:
    """한 번의 변환이 남긴 산출물."""

    source: Path
    dxf: Path
    dxf_flat: Path | None = None
    preview: Path | None = None
    report: Path | None = None
    n_contours: int = 0
    n_major: int = 0
    n_spots: int = 0
    n_sheets: int = 0
    elapsed: float = 0.0
    warnings: list[str] = field(default_factory=list)

    def summary(self) -> str:
        parts = [
            f"{self.source.name} → {self.dxf.name}",
            f"등고선 {self.n_contours}개 (계곡선 {self.n_major}개)",
        ]
        if self.n_spots:
            parts.append(f"표고점 {self.n_spots}개")
        if self.n_sheets:
            parts.append(f"도곽 {self.n_sheets}매")
        parts.append(f"{self.elapsed:.1f}초")
        return " / ".join(parts)


def run(
    dem_path: str | Path,
    out_dir: str | Path,
    settings: Settings | None = None,
) -> Result:
    """DEM GeoTIFF 하나를 DXF·미리보기·리포트로 변환한다."""
    settings = settings or Settings()
    dem_path = Path(dem_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    warnings: list[str] = []

    raw = dem_mod.load(dem_path)
    log.info("DEM 읽음: %s", raw.describe().replace("\n", " "))

    # 무인 실행에서는 현장마다 표제란을 손으로 채울 수 없으므로,
    # 현장명이 비어 있으면 파일 이름을 현장명으로 삼는다.
    if not settings.project_name:
        settings = replace(settings, project_name=dem_path.stem)

    if raw.crs_epsg is None:
        warnings.append(
            "원본에 좌표계 정보가 없습니다. 도면 좌표가 지적도와 어긋날 수 있으니 "
            f"EPSG:{settings.epsg} 가 맞는지 확인하세요."
        )
    elif raw.crs_epsg != settings.epsg:
        warnings.append(
            f"원본 좌표계(EPSG:{raw.crs_epsg})가 설정(EPSG:{settings.epsg})과 다릅니다. "
            "재투영 없이 원본 좌표 그대로 도면을 만듭니다."
        )

    prepared = dem_mod.prepare(raw, settings)
    lines = contour_mod.generate(prepared, settings)
    if not lines:
        warnings.append(
            "등고선이 하나도 생성되지 않았습니다. 표고 기복보다 등고선 간격이 "
            "크지 않은지 확인하세요."
        )

    # 표고점 — 등고선만으로는 도면이 되지 않는다.
    spots = []
    if settings.spot_heights:
        spacing = settings.spot_spacing or None
        spots = points_mod.grid(prepared, settings, spacing)
    if settings.spot_extremes:
        spots = spots + points_mod.extremes(prepared, settings.spot_extremes)

    # 도곽 — 한 현장을 축척·용지에 맞춰 여러 매로 나눈다.
    sheet_layout = None
    if settings.sheet_split:
        sheet_layout = sheets_mod.plan(
            prepared.bounds,
            settings.scale,
            settings.paper,
            overlap=settings.sheet_overlap,
            prefix=settings.sheet_prefix,
        )
        log.info("도곽: %s", sheet_layout.describe())

    overlays = list(settings.overlay_dxf)
    for path in overlays:
        if not Path(path).exists():
            warnings.append(f"중첩할 도면을 찾지 못해 건너뜁니다: {path}")
    overlays = [p for p in overlays if Path(p).exists()]

    stem = dem_path.stem
    if sheet_layout is not None and settings.sheet_prefix:
        # 기존 명명 규칙(C-01-02-001~008.현황측량도)에 맞춘다.
        label = sheets_mod.sheet_range_label(sheet_layout, settings.sheet_prefix)
        base = f"{label}.{settings.drawing_title}"
    else:
        base = f"{stem}_등고선"

    dxf_path = write_dxf(
        lines, prepared, settings, out_dir / f"{base}.dxf",
        spots=spots, sheet_layout=sheet_layout, overlays=overlays,
    )

    flat_path = None
    if settings.flatten_z:
        flat_path = write_dxf(
            lines, prepared, settings, out_dir / f"{base}_z0.dxf", flatten=True,
            spots=spots, sheet_layout=sheet_layout, overlays=overlays,
        )

    png_path = None
    if settings.make_preview:
        png_path = preview_mod.render(
            prepared,
            lines,
            out_dir / f"{stem}_미리보기.png",
            title=f"{settings.project_name} — {settings.scale} {settings.drawing_title}",
            settings=settings,
            spots=spots if len(spots) <= 400 else [],
            sheet_layout=sheet_layout,
        )

    result = Result(
        source=dem_path,
        dxf=dxf_path,
        dxf_flat=flat_path,
        preview=png_path,
        n_contours=len(lines),
        n_major=sum(1 for c in lines if c.is_major),
        n_spots=len(spots),
        n_sheets=len(sheet_layout.sheets) if sheet_layout else 0,
        elapsed=time.monotonic() - started,
        warnings=warnings,
    )
    result.report = _write_report(
        result, raw, prepared, settings, out_dir / f"{stem}_리포트.json"
    )
    return result


def _write_report(result: Result, raw, prepared, settings: Settings, path: Path) -> Path:
    """무인 실행에서 나중에 확인할 수 있도록 처리 내역을 남긴다."""
    e0, n0, e1, n1 = prepared.bounds
    zmin, zmax = prepared.zrange
    preset = settings.preset()

    payload = {
        "원본": str(result.source),
        "좌표계": f"EPSG:{raw.crs_epsg}" if raw.crs_epsg else None,
        # 드라이브의 _ortho.json과 같은 경계 표기를 유지한다.
        "E0": round(e0, 3),
        "E1": round(e1, 3),
        "N0": round(n0, 3),
        "N1": round(n1, 3),
        "CELL": prepared.cell,
        "표고최저": round(zmin, 3),
        "표고최고": round(zmax, 3),
        "축척": preset.name,
        "주곡선간격": preset.minor_interval,
        "계곡선간격": preset.major_interval,
        "지면필터": settings.ground_filter,
        "평활sigma": settings.smooth_sigma,
        "등고선수": result.n_contours,
        "계곡선수": result.n_major,
        "표고점수": result.n_spots,
        "도곽매수": result.n_sheets,
        "소요초": round(result.elapsed, 2),
        "경고": result.warnings,
        "산출물": {
            "dxf": str(result.dxf),
            "dxf_z0": str(result.dxf_flat) if result.dxf_flat else None,
            "미리보기": str(result.preview) if result.preview else None,
        },
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path
