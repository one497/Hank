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


# ── 표고점 ────────────────────────────────────────────────────────────────

def test_spot_grid_aligns_to_spacing(sample_dem):
    from terrain2dxf import points

    d = dem_mod.load(sample_dem)
    spots = points.grid(d, Settings(scale="1/1000"), spacing=25.0)
    assert spots
    # 간격의 배수에 맞아야 인접 도면끼리 표고점이 어긋나지 않는다.
    assert all(abs(p.e % 25.0) < 1e-6 and abs(p.n % 25.0) < 1e-6 for p in spots)
    # 모든 점이 DEM 범위 안에 있어야 한다.
    e0, n0, e1, n1 = d.bounds
    assert all(e0 <= p.e <= e1 and n0 <= p.n <= n1 for p in spots)


def test_spot_grid_rejects_bad_spacing(sample_dem):
    from terrain2dxf import points

    d = dem_mod.load(sample_dem)
    with pytest.raises(ValueError):
        points.grid(d, Settings(), spacing=0.0)


def test_extremes_are_spread_out(sample_dem):
    from terrain2dxf import points

    d = dem_mod.load(sample_dem)
    picked = points.extremes(d, count=3, min_distance=40.0)
    assert len(picked) > 0
    for i, a in enumerate(picked):
        for b in picked[i + 1:]:
            assert np.hypot(a.e - b.e, a.n - b.n) >= 40.0


# ── 도곽 ──────────────────────────────────────────────────────────────────

def test_sheet_plan_covers_whole_extent():
    from terrain2dxf import sheets

    bounds = (229500.0, 506400.0, 231200.0, 508500.0)
    layout = sheets.plan(bounds, "1/1000", "A1", overlap=20.0)

    e0, n0, e1, n1 = bounds
    assert max(s.e1 for s in layout.sheets) >= e1
    assert max(s.n1 for s in layout.sheets) >= n1
    assert min(s.e0 for s in layout.sheets) <= e0
    assert min(s.n0 for s in layout.sheets) <= n0


def test_sheet_cover_matches_scale():
    """1/1000에서 도면 1 mm는 실제 1 m여야 한다."""
    from terrain2dxf import sheets

    layout = sheets.plan((0, 0, 100, 100), "1/1000", "A1")
    assert layout.cover_e == pytest.approx(layout.draw_w_mm)
    assert layout.cover_n == pytest.approx(layout.draw_h_mm)

    layout2 = sheets.plan((0, 0, 100, 100), "1/500", "A1")
    assert layout2.cover_n == pytest.approx(layout.draw_h_mm * 0.5)


def test_sheet_naming_matches_existing_convention():
    from terrain2dxf import sheets

    layout = sheets.plan((229500.0, 506400.0, 231200.0, 508500.0), "1/1000", "A1")
    label = sheets.sheet_range_label(layout, "C-01-02-")
    # 기존 도면이 'C-01-02-001~008' 형식이다.
    assert label.startswith("C-01-02-001~")
    assert label.count("C-01-02-") == 1


def test_sheet_plan_rejects_bad_input():
    from terrain2dxf import sheets

    with pytest.raises(ValueError):
        sheets.plan((0, 0, 0, 0), "1/1000", "A1")
    with pytest.raises(ValueError, match="모르는 용지"):
        sheets.plan((0, 0, 100, 100), "1/1000", "A9")
    with pytest.raises(ValueError, match="축척 표기"):
        sheets.plan((0, 0, 100, 100), "1대1000", "A1")


def test_pipeline_creates_one_layout_per_sheet(sample_dem, tmp_path):
    settings = Settings(
        scale="1/1000", paper="A3", sheet_split=True, sheet_prefix="C-01-02-",
        spot_heights=True, make_preview=False, project_name="시험현장",
    )
    result = run(sample_dem, tmp_path, settings)
    assert result.n_sheets > 0
    assert result.n_spots > 0

    doc = ezdxf.readfile(result.dxf)
    names = [l.name for l in doc.layouts]
    assert "Model" in names
    # 도곽마다 레이아웃 하나. 기본 빈 레이아웃은 남지 않아야 한다.
    sheet_names = [n for n in names if n != "Model"]
    assert len(sheet_names) == result.n_sheets
    assert all(n.startswith("C-01-02-") for n in sheet_names)


def test_viewport_scale_is_exact(sample_dem, tmp_path):
    """뷰포트가 실제로 지정한 축척으로 보이는지."""
    settings = Settings(
        scale="1/1000", paper="A3", sheet_split=True, make_preview=False
    )
    result = run(sample_dem, tmp_path, settings)
    doc = ezdxf.readfile(result.dxf)

    psp = doc.layouts.get([l.name for l in doc.layouts if l.name != "Model"][0])
    viewports = [e for e in psp if e.dxftype() == "VIEWPORT"]
    # 첫 번째는 ezdxf가 만드는 기본 뷰포트라 건너뛴다.
    vp = viewports[-1]
    # 모델 높이(m) / 도면 높이(mm) = 1000 이어야 1/1000 이다.
    assert (vp.dxf.view_height * 1000.0) / vp.dxf.height == pytest.approx(1000.0)


def test_titleblock_carries_project_fields(sample_dem, tmp_path):
    settings = Settings(
        scale="1/1000", paper="A3", sheet_split=True, make_preview=False,
        project_name="원삼면 용수선", drawing_title="현황측량도", surveyor="한크건설",
    )
    result = run(sample_dem, tmp_path, settings)
    doc = ezdxf.readfile(result.dxf)
    psp = doc.layouts.get([l.name for l in doc.layouts if l.name != "Model"][0])
    texts = {e.dxf.text for e in psp if e.dxftype() == "TEXT"}
    assert "원삼면 용수선" in texts
    assert "현황측량도" in texts
    assert "한크건설" in texts
    assert "1/1000" in texts


# ── 중첩 ──────────────────────────────────────────────────────────────────

def test_overlay_merges_into_named_layer(tmp_path):
    from terrain2dxf import overlay

    src = ezdxf.new("R2010", setup=True)
    src.layers.add("지번", color=2)
    src.modelspace().add_lwpolyline(
        [(0, 0), (10, 0), (10, 10)], format="xy", dxfattribs={"layer": "지번"}
    )
    src_path = tmp_path / "지적.dxf"
    src.saveas(src_path)

    doc = ezdxf.new("R2010", setup=True)
    added = overlay.merge(doc, src_path, layer="중첩-지적")
    assert added == 1
    layers = {e.dxf.layer for e in doc.modelspace()}
    assert layers == {"중첩-지적"}


def test_overlay_rejects_dwg(tmp_path):
    from terrain2dxf import overlay

    dwg = tmp_path / "지적도.dwg"
    dwg.write_bytes(b"not really a dwg")
    doc = ezdxf.new("R2010")
    with pytest.raises(ValueError, match="ODA File Converter"):
        overlay.merge(doc, dwg)


def test_overlay_reports_missing_file(tmp_path):
    from terrain2dxf import overlay

    doc = ezdxf.new("R2010")
    with pytest.raises(FileNotFoundError):
        overlay.merge(doc, tmp_path / "없음.dxf")


def test_pipeline_warns_on_missing_overlay(sample_dem, tmp_path):
    settings = Settings(
        scale="1/1000", make_preview=False,
        overlay_dxf=[str(tmp_path / "없는지적도.dxf")],
    )
    result = run(sample_dem, tmp_path, settings)
    assert any("찾지 못해" in w for w in result.warnings)
