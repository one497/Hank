"""DEM에서 표고점을 뽑아 도면에 기입할 형태로 정리한다.

등고선만으로는 도면이 되지 않는다. 실무에서는 격자 간격으로 표고점을 찍고
표고값을(필요하면 좌표까지) 문자로 적는데, 이 과정이 손으로 이뤄지고 있었다.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .dem import Dem


@dataclass
class SpotHeight:
    """표고점 하나."""

    e: float
    n: float
    z: float

    @property
    def label(self) -> str:
        return f"{self.z:.2f}"

    @property
    def coord_label(self) -> str:
        """좌표까지 적어야 하는 주요 지점용."""
        return f"E {self.e:.2f}\nN {self.n:.2f}\nH {self.z:.2f}"


# 축척별 표고점 격자 간격(m). 도면에서 대략 2 cm 간격이 되도록 잡았다.
SPOT_SPACING = {
    "1/500": 10.0,
    "1/1000": 20.0,
    "1/1200": 25.0,
    "1/2500": 50.0,
    "1/5000": 100.0,
}


def _sample(dem: Dem, e: float, n: float) -> float | None:
    """실좌표 한 점의 표고를 격자에서 읽는다."""
    e0, n0, e1, n1 = dem.bounds
    ny, nx = dem.z.shape
    col = int((e - e0) / dem.cell)
    # 래스터는 첫 행이 북쪽이므로 행 번호를 뒤집는다.
    row = int((n1 - n) / dem.cell)
    if not (0 <= row < ny and 0 <= col < nx):
        return None
    v = dem.z[row, col]
    return float(v) if np.isfinite(v) else None


def grid(dem: Dem, settings, spacing: float | None = None) -> list[SpotHeight]:
    """격자 간격으로 표고점을 배치한다.

    간격은 도면 좌표의 배수에 맞춰, 인접한 도면끼리 표고점 위치가 어긋나지
    않게 한다.
    """
    if spacing is None:
        spacing = SPOT_SPACING.get(settings.scale, 20.0)
    if spacing <= 0:
        raise ValueError("표고점 간격은 0보다 커야 합니다.")

    e0, n0, e1, n1 = dem.bounds
    start_e = np.ceil(e0 / spacing) * spacing
    start_n = np.ceil(n0 / spacing) * spacing

    out: list[SpotHeight] = []
    for e in np.arange(start_e, e1, spacing):
        for n in np.arange(start_n, n1, spacing):
            z = _sample(dem, float(e), float(n))
            if z is not None:
                out.append(SpotHeight(float(e), float(n), z))
    return out


def extremes(dem: Dem, count: int = 5, min_distance: float = 50.0) -> list[SpotHeight]:
    """최고점·최저점 같은 주요 지점.

    서로 min_distance 안에 있는 점은 하나만 남겨, 같은 봉우리에 표고점이
    여러 개 찍히는 것을 막는다.
    """
    e0, n0, e1, n1 = dem.bounds
    ny, nx = dem.z.shape
    z = dem.z

    picked: list[SpotHeight] = []
    for reverse in (True, False):  # 높은 곳부터, 그다음 낮은 곳부터
        flat = np.where(np.isfinite(z), z, -np.inf if reverse else np.inf)
        order = np.argsort(flat, axis=None)
        if reverse:
            order = order[::-1]

        taken = 0
        for idx in order:
            if taken >= count:
                break
            row, col = divmod(int(idx), nx)
            v = z[row, col]
            if not np.isfinite(v):
                continue
            e = e0 + (col + 0.5) * dem.cell
            n = n1 - (row + 0.5) * dem.cell
            if any(np.hypot(p.e - e, p.n - n) < min_distance for p in picked):
                continue
            picked.append(SpotHeight(float(e), float(n), float(v)))
            taken += 1

    return picked
