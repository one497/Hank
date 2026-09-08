"""검증용 합성 DEM 생성.

드라이브의 실제 DEM(EPSG:5186, 1 m 격자, 용인 일원)과 같은 규약으로
능선·계곡·하천이 있는 지형을 만든다. 실제 현장 데이터 없이도 파이프라인을
끝까지 돌려볼 수 있게 하는 것이 목적이다.
"""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import rasterio
from rasterio.transform import from_origin
from rasterio.crs import CRS

# 드라이브 _ortho.json 과 같은 좌표 규약
E0, N0 = 229500.0, 506400.0
CELL = 1.0


def synth(nx: int = 600, ny: int = 600, seed: int = 20260908) -> np.ndarray:
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:ny, 0:nx].astype("float32")
    u = xx / nx
    v = yy / ny

    # 북동에서 남서로 내려오는 사면
    z = 140.0 - 55.0 * u - 20.0 * v

    # 능선 두 줄
    z += 14.0 * np.exp(-(((v - 0.30) / 0.11) ** 2))
    z += 9.0 * np.exp(-(((v - 0.72) / 0.08) ** 2))

    # 사행하는 계곡 — 하천이 지나가는 자리
    thalweg = 0.52 + 0.10 * np.sin(2.6 * np.pi * u) + 0.03 * np.sin(7.0 * np.pi * u)
    z -= 11.0 * np.exp(-(((v - thalweg) / 0.045) ** 2))

    # 완만한 기복
    for wavelength, amp in ((0.45, 3.0), (0.17, 1.2)):
        z += amp * np.sin(2 * np.pi * u / wavelength) * np.cos(2 * np.pi * v / wavelength)

    # 드론 DSM다운 격자 잡음
    z += rng.normal(0.0, 0.12, size=z.shape)

    # 초목·건물처럼 지면 위로 솟은 덩어리 (지면 필터 검증용)
    for _ in range(45):
        cx, cy = rng.integers(30, nx - 30), rng.integers(30, ny - 30)
        r = rng.integers(4, 11)
        h = rng.uniform(4.0, 13.0)
        blob = ((xx - cx) ** 2 + (yy - cy) ** 2) < r**2
        z[blob] += h

    return z.astype("float32")


def main(out: Path, nx: int = 600, ny: int = 600) -> Path:
    z = synth(nx, ny)
    transform = from_origin(E0, N0 + ny * CELL, CELL, CELL)
    out.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(
        out, "w", driver="GTiff", height=ny, width=nx, count=1,
        dtype="float32", crs=CRS.from_epsg(5186), transform=transform, nodata=-9999.0,
    ) as dst:
        dst.write(z, 1)
    print(f"{out} 생성: {nx}×{ny}, 표고 {z.min():.1f}~{z.max():.1f} m")
    return out


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/합성지형_시험.tif")
    main(target)
