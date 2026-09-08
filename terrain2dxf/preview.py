"""사람이 눈으로 검산할 수 있는 PNG 미리보기."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # 화면 없는 NAS·서버에서도 돌아야 한다
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.colors import LightSource

from .contours import Contour, label_positions
from .dem import Dem

# 미리보기 제목·축 이름에 한글이 들어가므로 한글 폰트를 찾아 쓴다.
# 없으면 제목만 깨질 뿐 도면(DXF)에는 영향이 없으므로 조용히 넘어간다.
_KOREAN_FONT_CANDIDATES = (
    "NanumGothic", "NanumBarunGothic", "Noto Sans CJK KR", "Noto Sans KR",
    "Malgun Gothic", "AppleGothic", "UnDotum",
)


def _use_korean_font() -> str | None:
    available = {f.name for f in font_manager.fontManager.ttflist}

    # matplotlib의 폰트 캐시는 나중에 설치된 폰트를 모른다. 후보가 하나도
    # 안 잡히면 시스템을 직접 훑어 등록한다.
    if not (available & set(_KOREAN_FONT_CANDIDATES)):
        for path in font_manager.findSystemFonts():
            try:
                name = font_manager.FontProperties(fname=path).get_name()
            except Exception:
                continue
            if name in _KOREAN_FONT_CANDIDATES:
                font_manager.fontManager.addfont(path)
                available.add(name)

    for name in _KOREAN_FONT_CANDIDATES:
        if name in available:
            plt.rcParams["font.family"] = name
            plt.rcParams["axes.unicode_minus"] = False
            return name
    return None


_KOREAN_FONT = _use_korean_font()


def render(
    dem: Dem,
    contours: list[Contour],
    out_path: str | Path,
    title: str = "",
    dpi: int = 150,
    settings=None,
) -> Path:
    """음영기복 위에 등고선을 얹은 미리보기를 저장한다."""
    out_path = Path(out_path)
    e0, n0, e1, n1 = dem.bounds

    ls = LightSource(azdeg=315, altdeg=45)
    shaded = ls.hillshade(dem.z, vert_exag=2.0, dx=dem.cell, dy=dem.cell)

    fig, ax = plt.subplots(figsize=(10, 10 * (n1 - n0) / max(e1 - e0, 1e-9)))
    ax.imshow(shaded, cmap="gray", extent=(e0, e1, n0, n1), origin="upper")

    for c in contours:
        ax.plot(
            c.points[:, 0],
            c.points[:, 1],
            color="#8a3b12" if c.is_major else "#c98a5e",
            linewidth=0.9 if c.is_major else 0.4,
        )

    # 표고 라벨은 DXF와 같은 자리에 찍어, 미리보기만 보고도 검산이 되게 한다.
    if settings is not None:
        for elevation, pos, angle in label_positions(contours, settings, spacing=200.0):
            ax.text(
                pos[0], pos[1], f"{elevation:g}",
                fontsize=5, rotation=angle, color="#5a2408",
                ha="center", va="center", rotation_mode="anchor",
                bbox=dict(boxstyle="square,pad=0.05", fc="white", ec="none", alpha=0.75),
            )

    ax.set_xlabel("E (m)")
    ax.set_ylabel("N (m)")
    ax.set_aspect("equal")
    if title:
        ax.set_title(title, fontsize=10)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)
    return out_path
