"""드론 3D 산출물(DEM)에서 CAD 도면(DXF)을 상용 SW 없이 자동 생성한다.

구성
----
config    축척·레이어 규약
dem       GeoTIFF 읽기, 결측 보간, 평활, 간이 지면 필터
contours  등고선 생성과 단순화
dxf       DXF 출력
preview   검산용 PNG
pipeline  DEM 한 장 → 도면 한 벌
watch     폴더 감시 무인 실행
"""

from .config import Settings, SCALE_PRESETS, LayerScheme, LayerSpec, ScalePreset
from .pipeline import run, Result

__all__ = [
    "Settings",
    "SCALE_PRESETS",
    "LayerScheme",
    "LayerSpec",
    "ScalePreset",
    "run",
    "Result",
]
__version__ = "0.1.0"
