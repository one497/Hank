"""terrain2dxf 핵심 동작 검증.

    pip install pytest
    python -m pytest tests/test_terrain2dxf.py -q
"""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import ezdxf

from terrain2dxf import Settings, run
from terrain2dxf import contours as contour_mod
from terrain2dxf import dem as dem_mod
from tests.make_sample_dem import main as make_sample


@pytest.fixture(scope="module")
def sample_dem(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("dem") / "시험지형.tif"
    return make_sample(out, nx=200, ny=200)


def test_levels_cover_range_and_align_to_interval():
    levels = contour_mod._levels(62.3, 74.8, 5.0)
    assert levels == [65.0, 70.0]
    # 간격의 배수여야 도면 표고가 딱 떨어진다.
    assert all(abs(v / 5.0 - round(v / 5.0)) < 1e-9 for v in levels)


def test_levels_reject_nonpositive_interval():
    with pytest.raises(ValueError):
        contour_mod._levels(0.0, 10.0, 0.0)


def test_major_classification_follows_interval():
    assert contour_mod._is_major(100.0, 5.0)
    assert not contour_mod._is_major(101.0, 5.0)


def test_fill_gaps_removes_all_nan():
    z = np.array([[1.0, np.nan], [3.0, 4.0]], dtype="float32")
    filled = dem_mod.fill_gaps(z)
    assert np.isfinite(filled).all()
    # 기존 유효값은 건드리지 않는다.
    assert filled[0, 0] == 1.0 and filled[1, 1] == 4.0


def test_fill_gaps_rejects_all_nan():
    with pytest.raises(ValueError):
        dem_mod.fill_gaps(np.full((3, 3), np.nan, dtype="float32"))


def test_ground_filter_removes_raised_blob():
    """평지 위에 솟은 덩어리를 지면 필터가 걷어내는지."""
    z = np.full((120, 120), 50.0, dtype="float32")
    z[55:65, 55:65] += 8.0  # 건물 같은 10 m 크기, 8 m 높이 덩어리

    ground = dem_mod.ground_filter(z, cell=1.0, max_window=20.0)
    assert ground[59, 59] == pytest.approx(50.0, abs=0.5)
    # 원래 평지는 그대로여야 한다.
    assert ground[10, 10] == pytest.approx(50.0, abs=0.5)


def test_dem_bounds_and_cell(sample_dem):
    d = dem_mod.load(sample_dem)
    e0, n0, e1, n1 = d.bounds
    assert d.cell == pytest.approx(1.0)
    assert d.crs_epsg == 5186
    assert (e1 - e0) == pytest.approx(200.0)
    assert (n1 - n0) == pytest.approx(200.0)


def test_pipeline_writes_readable_dxf(sample_dem, tmp_path):
    settings = Settings(scale="1/1000", flatten_z=True, make_preview=False)
    result = run(sample_dem, tmp_path, settings)

    assert result.n_contours > 0
    assert result.dxf.exists() and result.dxf_flat is not None
    assert result.report is not None and result.report.exists()

    doc = ezdxf.readfile(result.dxf)
    msp = doc.modelspace()
    polys = [e for e in msp if e.dxftype() == "LWPOLYLINE"]
    assert len(polys) > 0

    layers = {l.dxf.name for l in doc.layers}
    assert {"등고선-주곡선", "등고선-계곡선", "등고선-표고", "도곽"} <= layers

    # 등고선의 Z는 실제 표고를 담고 있어야 한다.
    elevations = {round(e.dxf.elevation, 3) for e in polys}
    assert max(elevations) > 60.0


def test_flatten_puts_everything_on_zero(sample_dem, tmp_path):
    settings = Settings(scale="1/1000", flatten_z=True, make_preview=False)
    result = run(sample_dem, tmp_path, settings)

    doc = ezdxf.readfile(result.dxf_flat)
    elevations = {
        round(e.dxf.elevation, 6) for e in doc.modelspace() if e.dxftype() == "LWPOLYLINE"
    }
    assert elevations == {0.0}


def test_unknown_scale_is_rejected():
    with pytest.raises(ValueError, match="알 수 없는 축척"):
        Settings(scale="1/999").preset()


def test_settings_roundtrip(tmp_path):
    path = tmp_path / "설정.json"
    Settings(scale="1/500", ground_filter=True, smooth_sigma=2.0).save(path)
    loaded = Settings.load(path)
    assert loaded.scale == "1/500"
    assert loaded.ground_filter is True
    assert loaded.smooth_sigma == 2.0


def test_settings_rejects_unknown_key(tmp_path):
    path = tmp_path / "설정.json"
    path.write_text('{"scale": "1/1000", "오타항목": 1}', encoding="utf-8")
    with pytest.raises(ValueError, match="모르는 항목"):
        Settings.load(path)
