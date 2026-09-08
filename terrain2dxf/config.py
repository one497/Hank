"""축척·레이어 규약 정의.

기본값은 국내 토목 실무에서 통용되는 지형도 등고선 간격을 따른다.
회사 도면 규약이 다르면 이 파일이나 설정 JSON만 고치면 된다.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path
import json

# 드라이브의 _ortho.json 규약과 동일: 중부원점 GRS80
DEFAULT_EPSG = 5186


@dataclass(frozen=True)
class ScalePreset:
    """축척별 등고선 간격과 표고 라벨 규칙."""

    name: str
    minor_interval: float   # 주곡선 간격 (m)
    major_interval: float   # 계곡선 간격 (m)
    label_every: float      # 표고를 기입할 간격 (m)
    text_height: float      # 도면 단위(m) 기준 문자 높이
    simplify_tol: float     # 등고선 단순화 허용오차 (m)


# 1/1000 지형도 = 주곡선 1m, 계곡선 5m (그 외 축척도 같은 1:5 비율)
SCALE_PRESETS: dict[str, ScalePreset] = {
    "1/500": ScalePreset("1/500", 0.5, 2.5, 2.5, 0.75, 0.10),
    "1/1000": ScalePreset("1/1000", 1.0, 5.0, 5.0, 1.50, 0.20),
    "1/1200": ScalePreset("1/1200", 1.0, 5.0, 5.0, 1.80, 0.25),
    "1/2500": ScalePreset("1/2500", 2.0, 10.0, 10.0, 3.75, 0.50),
    "1/5000": ScalePreset("1/5000", 5.0, 25.0, 25.0, 7.50, 1.00),
}


@dataclass(frozen=True)
class LayerSpec:
    """DXF 레이어 하나의 정의."""

    name: str
    color: int          # AutoCAD Color Index
    lineweight: int     # 1/100 mm 단위. -3 = 기본값


@dataclass(frozen=True)
class LayerScheme:
    minor: LayerSpec = LayerSpec("등고선-주곡선", 8, 13)
    major: LayerSpec = LayerSpec("등고선-계곡선", 3, 30)
    label: LayerSpec = LayerSpec("등고선-표고", 7, 13)
    border: LayerSpec = LayerSpec("도곽", 1, 50)
    spot: LayerSpec = LayerSpec("표고점", 5, 13)
    spot_text: LayerSpec = LayerSpec("표고점-문자", 7, 13)
    titleblock: LayerSpec = LayerSpec("표제란", 7, 35)
    overlay: LayerSpec = LayerSpec("중첩-지적", 2, 18)

    def all_specs(self) -> tuple[LayerSpec, ...]:
        return (
            self.minor, self.major, self.label, self.border,
            self.spot, self.spot_text, self.titleblock, self.overlay,
        )


@dataclass
class Settings:
    """파이프라인 한 번의 실행을 결정하는 전체 설정."""

    scale: str = "1/1000"
    epsg: int = DEFAULT_EPSG

    # DEM 전처리
    smooth_sigma: float = 1.5        # 가우시안 평활 강도. 0이면 끔
    ground_filter: bool = False      # 간이 지면 필터(초목·건물 제거) 사용 여부
    ground_max_window: float = 20.0  # 지면 필터 최대 창 크기 (m)
    ground_slope: float = 0.3        # 지면 필터 허용 경사 (m/m)

    # 등고선
    min_points: int = 4              # 이보다 짧은 등고선 조각은 버림
    min_length: float = 2.0          # 이보다 짧은(m) 등고선 조각은 버림

    # 표고점
    spot_heights: bool = False       # 격자 표고점을 찍을지
    spot_spacing: float = 0.0        # 0이면 축척에 맞는 기본 간격을 쓴다
    spot_coords: bool = False        # 표고와 함께 E/N 좌표도 적을지
    spot_extremes: int = 0           # 최고·최저 주요 지점을 몇 개씩 표시할지

    # 도곽
    sheet_split: bool = False        # 도곽을 나눠 레이아웃을 만들지
    paper: str = "A1"                # A0~A3
    sheet_overlap: float = 20.0      # 인접 도면이 겹치는 폭 (m)
    sheet_prefix: str = ""           # 도면번호 접두사. 예: "C-01-02-"

    # 중첩할 외부 도면 (지적선·구역계 등). DXF만 읽을 수 있다.
    overlay_dxf: list[str] = field(default_factory=list)

    # 표제란에 채울 내용
    project_name: str = ""
    drawing_title: str = "현황측량도"
    surveyor: str = ""

    # 출력
    flatten_z: bool = False          # True면 Z=0으로 눕힌 평면도용 사본도 생성
    make_preview: bool = True

    def preset(self) -> ScalePreset:
        if self.scale not in SCALE_PRESETS:
            raise ValueError(
                f"알 수 없는 축척 {self.scale!r}. 사용 가능: {', '.join(SCALE_PRESETS)}"
            )
        return SCALE_PRESETS[self.scale]

    @classmethod
    def load(cls, path: str | Path) -> "Settings":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        known = {f for f in cls.__dataclass_fields__}
        unknown = set(data) - known
        if unknown:
            raise ValueError(f"설정 파일에 모르는 항목이 있습니다: {sorted(unknown)}")
        return cls(**data)

    def save(self, path: str | Path) -> None:
        Path(path).write_text(
            json.dumps(asdict(self), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
