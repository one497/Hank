"""기존 도면(지적선·구역계 등)을 등고선 도면에 겹친다.

XREF_지적도_GRS80, 연속주제도 같은 도면을 매번 손으로 불러 얹던 작업을
자동으로 처리한다. 같은 좌표계(EPSG:5186)를 쓰고 있으므로 좌표 변환 없이
그대로 포갠다.
"""

from __future__ import annotations

from pathlib import Path
import logging

import ezdxf
from ezdxf.addons.importer import Importer

log = logging.getLogger(__name__)


def merge(doc, source_path: str | Path, layer: str | None = None) -> int:
    """외부 DXF의 모델공간 도형을 현재 문서로 가져온다.

    layer를 주면 가져온 도형을 모두 그 레이어로 몰아넣어, 원본 도면의 레이어가
    수십 개여도 중첩분을 한 번에 켜고 끌 수 있다. None이면 원본 레이어 구성을
    그대로 유지한다.

    DWG는 읽지 못한다. ODA File Converter로 DXF로 바꾼 뒤 넣어야 한다.
    """
    source_path = Path(source_path)
    if not source_path.exists():
        raise FileNotFoundError(f"중첩할 도면을 찾을 수 없습니다: {source_path}")
    if source_path.suffix.lower() == ".dwg":
        raise ValueError(
            f"DWG는 직접 읽을 수 없습니다: {source_path.name}\n"
            "  무료 ODA File Converter로 DXF로 변환한 뒤 넣어 주세요."
        )

    try:
        src = ezdxf.readfile(source_path)
    except (IOError, ezdxf.DXFStructureError) as exc:
        raise ValueError(f"도면을 읽지 못했습니다 ({source_path.name}): {exc}") from exc

    before = len(doc.modelspace())

    importer = Importer(src, doc)
    importer.import_modelspace()
    importer.finalize()

    added = len(doc.modelspace()) - before

    if layer:
        if layer not in doc.layers:
            doc.layers.add(layer)
        msp = doc.modelspace()
        # 방금 들여온 것들만 옮긴다.
        for entity in list(msp)[before:]:
            entity.dxf.layer = layer

    log.info("중첩: %s에서 도형 %d개 가져옴", source_path.name, added)
    return added
