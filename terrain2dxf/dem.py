"""DEM(GeoTIFF) 읽기와 전처리."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import Affine
from scipy import ndimage


@dataclass
class Dem:
    """전처리를 마친 표고 격자."""

    z: np.ndarray                 # (ny, nx) float32, 결측은 np.nan
    transform: Affine
    crs_epsg: int | None
    path: Path | None = None

    @property
    def cell(self) -> float:
        """격자 간격 (m). 정사각 격자를 전제로 한다."""
        return float(abs(self.transform.a))

    @property
    def bounds(self) -> tuple[float, float, float, float]:
        """(E0, N0, E1, N1) — 드라이브 _ortho.json과 같은 표기."""
        ny, nx = self.z.shape
        e0, n1 = self.transform * (0, 0)
        e1, n0 = self.transform * (nx, ny)
        return (min(e0, e1), min(n0, n1), max(e0, e1), max(n0, n1))

    @property
    def zrange(self) -> tuple[float, float]:
        finite = self.z[np.isfinite(self.z)]
        if finite.size == 0:
            raise ValueError("DEM에 유효한 표고값이 하나도 없습니다.")
        return float(finite.min()), float(finite.max())

    def describe(self) -> str:
        e0, n0, e1, n1 = self.bounds
        zmin, zmax = self.zrange
        ny, nx = self.z.shape
        nodata = int(np.count_nonzero(~np.isfinite(self.z)))
        return (
            f"격자 {nx}×{ny}, 셀 {self.cell:g} m, EPSG:{self.crs_epsg or '미상'}\n"
            f"  E {e0:.1f}~{e1:.1f} / N {n0:.1f}~{n1:.1f}\n"
            f"  표고 {zmin:.2f}~{zmax:.2f} m, 결측 {nodata}셀"
        )


def load(path: str | Path, band: int = 1) -> Dem:
    """GeoTIFF DEM을 읽어 결측을 NaN으로 정규화한다."""
    path = Path(path)
    with rasterio.open(path) as src:
        z = src.read(band, masked=True).astype("float32")
        z = np.ma.filled(z, np.nan)
        epsg = src.crs.to_epsg() if src.crs else None
        transform = src.transform

    # 일부 DEM은 nodata를 -9999 같은 실수값으로 남겨둔다.
    z[z < -1e4] = np.nan
    z[z > 1e5] = np.nan
    return Dem(z=z, transform=transform, crs_epsg=epsg, path=path)


def fill_gaps(z: np.ndarray) -> np.ndarray:
    """결측 셀을 가장 가까운 유효 셀 값으로 메운다.

    등고선 생성기가 NaN을 만나면 그 주변 등고선이 끊기므로,
    윤곽을 잇기 위한 최소한의 보간만 수행한다.
    """
    mask = ~np.isfinite(z)
    if not mask.any():
        return z
    if mask.all():
        raise ValueError("DEM 전체가 결측입니다.")
    idx = ndimage.distance_transform_edt(mask, return_distances=False, return_indices=True)
    return z[tuple(idx)]


def smooth(z: np.ndarray, sigma: float) -> np.ndarray:
    """가우시안 평활. 드론 DSM의 격자 잡음을 줄여 등고선 떨림을 막는다."""
    if sigma <= 0:
        return z
    return ndimage.gaussian_filter(z, sigma=sigma, mode="nearest")


def ground_filter(
    z: np.ndarray,
    cell: float,
    max_window: float = 20.0,
    slope: float = 0.3,
    initial_threshold: float = 0.3,
) -> np.ndarray:
    """간이 형태학적 지면 필터 (Zhang et al. 2003 PMF의 단순화 구현).

    창을 점점 키우며 회색조 열림(opening)을 반복해 지면 표면을 추정하고,
    추정면보다 임계치 이상 높은 셀을 비지면(초목·건물)으로 보아 제거한 뒤
    주변 지면값으로 메운다.

    한계: 래스터 DSM만으로는 수관 아래 지면을 복원할 수 없다. 숲이 우거진
    구간은 원래의 포인트클라우드에서 지면점을 분류하는 편이 정확하다.
    """
    filled = fill_gaps(z)
    surface = filled.copy()
    nonground = np.zeros(z.shape, dtype=bool)

    window = 3
    last_window = window
    while True:
        radius_m = (window // 2) * cell
        # 창이 커질수록 더 큰 지형 기복을 허용한다.
        threshold = min(initial_threshold + slope * radius_m, 6.0)

        opened = ndimage.grey_opening(surface, size=(window, window), mode="nearest")
        nonground |= (surface - opened) > threshold
        surface = opened

        if radius_m >= max_window:
            break
        last_window = window
        window = window * 2 + 1
        if window == last_window:  # 안전장치
            break

    out = filled.copy()
    out[nonground] = np.nan
    return fill_gaps(out)


def prepare(dem: Dem, settings) -> Dem:
    """설정에 따라 전처리를 적용한 새 Dem을 만든다."""
    z = fill_gaps(dem.z)
    if settings.ground_filter:
        z = ground_filter(
            z,
            cell=dem.cell,
            max_window=settings.ground_max_window,
            slope=settings.ground_slope,
        )
    z = smooth(z, settings.smooth_sigma)
    return Dem(z=z, transform=dem.transform, crs_epsg=dem.crs_epsg, path=dem.path)
