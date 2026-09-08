"""terrain2dxf 명령줄 도구.

    python -m terrain2dxf convert 현장.tif -o 도면/
    python -m terrain2dxf watch 입력/ 출력/ --archive 처리완료/
    python -m terrain2dxf init-config 설정.json
    python -m terrain2dxf sample 시험.tif
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from .config import SCALE_PRESETS, Settings
from .pipeline import run
from .watch import watch


def _setup_logging(verbose: bool, logfile: str | None) -> None:
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stderr)]
    if logfile:
        Path(logfile).parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(logfile, encoding="utf-8"))
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
    )
    # ezdxf는 파일을 쓸 때마다 내부 딕셔너리 생성을 INFO로 알린다.
    # 무인 실행 로그에서는 잡음이므로 경고부터만 남긴다.
    for noisy in ("ezdxf", "matplotlib", "PIL", "rasterio"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def _settings_from_args(args) -> Settings:
    settings = Settings.load(args.config) if args.config else Settings()

    # 값이 주어진 옵션만 설정을 덮어쓴다. 나머지는 설정 파일 값을 지킨다.
    for name in (
        "scale", "smooth_sigma", "spot_spacing", "spot_extremes",
        "paper", "sheet_overlap", "sheet_prefix",
        "project_name", "drawing_title", "surveyor",
    ):
        value = getattr(args, name, None)
        if value is not None:
            setattr(settings, name, value)

    for flag in ("ground_filter", "flatten_z", "spot_heights", "spot_coords", "sheet_split"):
        if getattr(args, flag, False):
            setattr(settings, flag, True)

    if getattr(args, "no_preview", False):
        settings.make_preview = False

    if getattr(args, "overlay_dxf", None):
        settings.overlay_dxf = list(args.overlay_dxf)

    # 표고점 옵션만 주고 --spot-heights를 빠뜨리는 실수를 막는다.
    if (args.spot_spacing or args.spot_coords) and not settings.spot_heights:
        settings.spot_heights = True

    return settings


def _add_common(p: argparse.ArgumentParser) -> None:
    p.add_argument("--config", help="설정 JSON 경로")
    p.add_argument("--scale", choices=sorted(SCALE_PRESETS), help="도면 축척")
    p.add_argument("--smooth-sigma", type=float, dest="smooth_sigma",
                   help="가우시안 평활 강도 (0이면 끔)")
    p.add_argument("--ground-filter", action="store_true", dest="ground_filter",
                   help="초목·건물을 걷어내는 간이 지면 필터 적용")
    p.add_argument("--flatten-z", action="store_true", dest="flatten_z",
                   help="Z를 0으로 눕힌 평면도용 사본도 생성")
    p.add_argument("--no-preview", action="store_true", dest="no_preview",
                   help="검산용 PNG를 만들지 않음")

    g = p.add_argument_group("표고점")
    g.add_argument("--spot-heights", action="store_true", dest="spot_heights",
                   help="격자 표고점을 찍고 표고를 기입")
    g.add_argument("--spot-spacing", type=float, dest="spot_spacing",
                   help="표고점 간격(m). 생략하면 축척에 맞는 기본값")
    g.add_argument("--spot-coords", action="store_true", dest="spot_coords",
                   help="표고와 함께 E/N 좌표도 기입")
    g.add_argument("--spot-extremes", type=int, dest="spot_extremes",
                   help="최고·최저 주요 지점을 각각 몇 개 표시할지")

    g = p.add_argument_group("도곽")
    g.add_argument("--sheet-split", action="store_true", dest="sheet_split",
                   help="축척·용지에 맞춰 도곽을 나누고 레이아웃 생성")
    g.add_argument("--paper", choices=["A0", "A1", "A2", "A3"], help="용지 규격")
    g.add_argument("--sheet-overlap", type=float, dest="sheet_overlap",
                   help="인접 도면이 겹치는 폭(m)")
    g.add_argument("--sheet-prefix", dest="sheet_prefix",
                   help="도면번호 접두사. 예: C-01-02-")

    g = p.add_argument_group("중첩·표제란")
    g.add_argument("--overlay", action="append", dest="overlay_dxf", default=None,
                   metavar="DXF", help="겹칠 기존 도면(지적선 등). 여러 번 지정 가능")
    g.add_argument("--project", dest="project_name", help="표제란 현장명")
    g.add_argument("--title", dest="drawing_title", help="표제란 도면명")
    g.add_argument("--surveyor", dest="surveyor", help="표제란 작성자")
    p.add_argument("-v", "--verbose", action="store_true")
    p.add_argument("--log", help="로그 파일 경로")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="terrain2dxf",
        description="드론 DEM에서 등고선 도면(DXF)을 상용 SW 없이 생성합니다.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_conv = sub.add_parser("convert", help="DEM 파일 하나를 도면으로 변환")
    p_conv.add_argument("dem", help="입력 GeoTIFF DEM")
    p_conv.add_argument("-o", "--out", default="output", help="출력 폴더")
    _add_common(p_conv)

    p_watch = sub.add_parser("watch", help="폴더를 감시하며 새 DEM을 자동 처리")
    p_watch.add_argument("in_dir", help="감시할 입력 폴더")
    p_watch.add_argument("out_dir", help="결과를 쌓을 출력 폴더")
    p_watch.add_argument("--interval", type=float, default=30.0, help="확인 주기(초)")
    p_watch.add_argument("--archive", help="처리한 원본을 옮겨둘 폴더")
    p_watch.add_argument("--once", action="store_true",
                         help="한 번만 훑고 끝냄 (NAS 예약작업용)")
    _add_common(p_watch)

    p_init = sub.add_parser("init-config", help="기본 설정 JSON 생성")
    p_init.add_argument("path", nargs="?", default="terrain2dxf.json")

    p_sample = sub.add_parser("sample", help="시험용 합성 DEM 생성")
    p_sample.add_argument("path", nargs="?", default="output/합성지형_시험.tif")
    p_sample.add_argument("--size", type=int, default=600, help="한 변의 격자 수")

    args = parser.parse_args(argv)

    if args.command == "init-config":
        Settings().save(args.path)
        print(f"기본 설정을 만들었습니다: {args.path}")
        return 0

    if args.command == "sample":
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        from tests.make_sample_dem import main as make_sample

        make_sample(Path(args.path), args.size, args.size)
        return 0

    _setup_logging(args.verbose, args.log)
    settings = _settings_from_args(args)

    if args.command == "convert":
        result = run(args.dem, args.out, settings)
        print(result.summary())
        for w in result.warnings:
            print(f"  ! {w}")
        print(f"  DXF      : {result.dxf}")
        if result.dxf_flat:
            print(f"  DXF(z=0) : {result.dxf_flat}")
        if result.preview:
            print(f"  미리보기 : {result.preview}")
        print(f"  리포트   : {result.report}")
        return 0

    if args.command == "watch":
        watch(
            args.in_dir, args.out_dir, settings,
            interval=args.interval, archive_dir=args.archive, once=args.once,
        )
        return 0

    parser.error(f"알 수 없는 명령: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
