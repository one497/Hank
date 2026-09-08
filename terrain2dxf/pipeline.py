"""DEM 한 장을 도면 한 벌로 바꾸는 전체 흐름."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import json
import logging
import time

from . import contours as contour_mod
from . import dem as dem_mod
from . import preview as preview_mod
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
    elapsed: float = 0.0
    warnings: list[str] = field(default_factory=list)

    def summary(self) -> str:
        parts = [
            f"{self.source.name} → {self.dxf.name}",
            f"등고선 {self.n_contours}개 (계곡선 {self.n_major}개)",
            f"{self.elapsed:.1f}초",
        ]
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

    stem = dem_path.stem
    dxf_path = write_dxf(lines, prepared, settings, out_dir / f"{stem}_등고선.dxf")

    flat_path = None
    if settings.flatten_z:
        flat_path = write_dxf(
            lines, prepared, settings, out_dir / f"{stem}_등고선_z0.dxf", flatten=True
        )

    png_path = None
    if settings.make_preview:
        png_path = preview_mod.render(
            prepared,
            lines,
            out_dir / f"{stem}_미리보기.png",
            title=f"{stem} — {settings.scale}",
            settings=settings,
        )

    result = Result(
        source=dem_path,
        dxf=dxf_path,
        dxf_flat=flat_path,
        preview=png_path,
        n_contours=len(lines),
        n_major=sum(1 for c in lines if c.is_major),
        elapsed=time.monotonic() - started,
        warnings=warnings,
    )
    result.report = _write_report(result, raw, prepared, settings, out_dir / f"{stem}_리포트.json")
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
