"""DEM 격자에서 등고선을 뽑아 도면에 쓸 수 있는 폴리라인으로 정리한다."""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from contourpy import contour_generator, LineType
from shapely.geometry import LineString

from .dem import Dem


@dataclass
class Contour:
    """등고선 한 조각."""

    elevation: float
    points: np.ndarray   # (N, 2) — 실좌표 (E, N)
    is_major: bool       # 계곡선 여부
    closed: bool

    @property
    def length(self) -> float:
        d = np.diff(self.points, axis=0)
        return float(np.hypot(d[:, 0], d[:, 1]).sum())


def _levels(zmin: float, zmax: float, interval: float) -> list[float]:
    """DEM 표고 범위를 덮는 등고선 표고 목록."""
    if interval <= 0:
        raise ValueError("등고선 간격은 0보다 커야 합니다.")
    start = math.ceil(zmin / interval) * interval
    out: list[float] = []
    v = start
    # 부동소수 누적 오차를 피하려고 배수로 계산한다.
    k = round(start / interval)
    while v < zmax:
        out.append(round(v, 6))
        k += 1
        v = k * interval
    return out


def _is_major(elevation: float, major_interval: float, tol: float = 1e-6) -> bool:
    r = elevation / major_interval
    return abs(r - round(r)) < tol


def generate(dem: Dem, settings) -> list[Contour]:
    """설정된 축척에 맞는 주곡선·계곡선을 생성한다."""
    preset = settings.preset()
    zmin, zmax = dem.zrange

    ny, nx = dem.z.shape
    # 래스터는 첫 행이 북쪽이므로, y가 증가하도록 뒤집어서 넘긴다.
    z = np.flipud(dem.z)
    e0, n0, e1, n1 = dem.bounds
    cell = dem.cell
    x = e0 + (np.arange(nx) + 0.5) * cell
    y = n0 + (np.arange(ny) + 0.5) * cell

    cg = contour_generator(x=x, y=y, z=z, line_type=LineType.Separate, name="serial")

    tol = preset.simplify_tol
    results: list[Contour] = []
    for level in _levels(zmin, zmax, preset.minor_interval):
        for seg in cg.lines(level):
            pts = np.asarray(seg, dtype=float)
            if len(pts) < settings.min_points:
                continue

            closed = bool(np.allclose(pts[0], pts[-1]))
            if tol > 0 and len(pts) > 2:
                simplified = LineString(pts).simplify(tol, preserve_topology=False)
                pts = np.asarray(simplified.coords, dtype=float)
                if len(pts) < 2:
                    continue

            c = Contour(
                elevation=level,
                points=pts,
                is_major=_is_major(level, preset.major_interval),
                closed=closed,
            )
            if c.length < settings.min_length:
                continue
            results.append(c)

    return results


def label_positions(
    contours: list[Contour], settings, spacing: float = 120.0
) -> list[tuple[float, np.ndarray, float]]:
    """표고 라벨을 놓을 (표고, 좌표, 회전각) 목록.

    계곡선 중 설정된 간격에 해당하는 것만, 선을 따라 일정 거리마다 배치한다.
    """
    preset = settings.preset()
    out: list[tuple[float, np.ndarray, float]] = []

    for c in contours:
        if not _is_major(c.elevation, preset.label_every):
            continue
        if c.length < spacing * 0.4:
            continue

        pts = c.points
        seg = np.diff(pts, axis=0)
        seglen = np.hypot(seg[:, 0], seg[:, 1])
        cum = np.concatenate([[0.0], np.cumsum(seglen)])
        total = cum[-1]

        n = max(1, int(total // spacing))
        for i in range(n):
            target = total * (i + 0.5) / n
            j = int(np.searchsorted(cum, target)) - 1
            j = min(max(j, 0), len(seg) - 1)
            if seglen[j] == 0:
                continue
            t = (target - cum[j]) / seglen[j]
            pos = pts[j] + t * seg[j]

            angle = math.degrees(math.atan2(seg[j][1], seg[j][0]))
            # 글자가 뒤집히지 않도록 항상 읽는 방향으로 맞춘다.
            if angle > 90:
                angle -= 180
            elif angle < -90:
                angle += 180
            out.append((c.elevation, pos, angle))

    return out
