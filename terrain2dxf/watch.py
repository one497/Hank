"""폴더에 DEM이 들어오면 알아서 도면을 만드는 무인 실행 러너.

NAS와 Windows PC 양쪽에서 돌아야 하므로 표준 라이브러리 폴링만 쓴다.
(watchdog 같은 추가 의존성이나 OS별 파일 감시 API를 쓰지 않는다.)
"""

from __future__ import annotations

from pathlib import Path
import json
import logging
import shutil
import time

from .config import Settings
from .pipeline import run

log = logging.getLogger(__name__)

DEM_SUFFIXES = {".tif", ".tiff"}
STATE_FILENAME = ".terrain2dxf_state.json"


class State:
    """이미 처리한 파일을 기억해 같은 일을 두 번 하지 않는다."""

    def __init__(self, path: Path):
        self.path = path
        self.done: dict[str, dict] = {}
        if path.exists():
            try:
                self.done = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                log.warning("상태 파일을 읽지 못해 새로 시작합니다: %s", path)

    @staticmethod
    def key(f: Path) -> str:
        st = f.stat()
        # 이름·크기·수정시각이 같으면 같은 파일로 본다.
        return f"{f.name}|{st.st_size}|{int(st.st_mtime)}"

    def seen(self, f: Path) -> bool:
        return self.key(f) in self.done

    def mark(self, f: Path, status: str, detail: str = "") -> None:
        self.done[self.key(f)] = {
            "파일": f.name,
            "상태": status,
            "시각": time.strftime("%Y-%m-%d %H:%M:%S"),
            "내용": detail,
        }
        self.save()

    def save(self) -> None:
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(
            json.dumps(self.done, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        tmp.replace(self.path)


def _is_settled(f: Path, quiet_seconds: float = 5.0) -> bool:
    """복사가 끝난 파일인지 확인한다.

    네트워크 드라이브로 큰 DEM을 옮기는 중에 처리를 시작하면 깨진 도면이
    나오므로, 마지막 수정 후 일정 시간이 지난 파일만 건드린다.
    """
    try:
        return (time.time() - f.stat().st_mtime) >= quiet_seconds
    except OSError:
        return False


def scan(in_dir: Path) -> list[Path]:
    return sorted(
        f for f in in_dir.iterdir()
        if f.is_file() and f.suffix.lower() in DEM_SUFFIXES and not f.name.startswith(".")
    )


def process_once(
    in_dir: Path,
    out_dir: Path,
    settings: Settings,
    state: State,
    archive_dir: Path | None = None,
    quiet_seconds: float = 5.0,
) -> int:
    """지금 폴더에 있는 새 파일을 모두 처리하고, 처리한 개수를 돌려준다."""
    n = 0
    for f in scan(in_dir):
        if state.seen(f):
            continue
        if not _is_settled(f, quiet_seconds):
            log.debug("아직 복사 중으로 보여 건너뜀: %s", f.name)
            continue

        log.info("처리 시작: %s", f.name)
        try:
            result = run(f, out_dir / f.stem, settings)
        except Exception as exc:  # 한 파일이 실패해도 나머지는 계속 처리한다
            log.exception("처리 실패: %s", f.name)
            state.mark(f, "실패", f"{type(exc).__name__}: {exc}")
            continue

        log.info("완료: %s", result.summary())
        for w in result.warnings:
            log.warning("  ! %s", w)
        state.mark(f, "완료", result.summary())
        n += 1

        if archive_dir is not None:
            archive_dir.mkdir(parents=True, exist_ok=True)
            target = archive_dir / f.name
            if target.exists():
                target = archive_dir / f"{f.stem}_{int(time.time())}{f.suffix}"
            try:
                shutil.move(str(f), str(target))
                log.info("  원본 이동: %s", target)
            except OSError:
                log.warning("  원본 이동 실패 (그대로 둡니다): %s", f.name)

    return n


def watch(
    in_dir: str | Path,
    out_dir: str | Path,
    settings: Settings | None = None,
    interval: float = 30.0,
    archive_dir: str | Path | None = None,
    once: bool = False,
) -> None:
    """입력 폴더를 주기적으로 살피며 새 DEM을 처리한다."""
    settings = settings or Settings()
    in_dir = Path(in_dir)
    out_dir = Path(out_dir)
    in_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    state = State(out_dir / STATE_FILENAME)
    archive = Path(archive_dir) if archive_dir else None

    log.info("감시 시작: %s → %s (%.0f초 간격)", in_dir, out_dir, interval)
    while True:
        try:
            process_once(in_dir, out_dir, settings, state, archive)
        except KeyboardInterrupt:
            log.info("감시를 멈춥니다.")
            return
        except Exception:
            # 감시 자체는 어떤 일이 있어도 죽지 않아야 한다.
            log.exception("감시 중 예기치 못한 오류. 계속 진행합니다.")

        if once:
            return
        time.sleep(interval)
