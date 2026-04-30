from __future__ import annotations

import os
from pathlib import Path
import shutil
import tempfile
import uuid


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEST_TMP_ROOT = PROJECT_ROOT / "tests" / ".tmp" / "session-temp"


class ProjectTemporaryDirectory:
    def __init__(self, suffix: str | None = None, prefix: str | None = None, dir: str | None = None):
        self._base = Path(dir) if dir else TEST_TMP_ROOT
        self._prefix = prefix or "tmp"
        self._suffix = suffix or ""
        self.name: str | None = None

    def __enter__(self) -> str:
        target = self._base / f"{self._prefix}{uuid.uuid4().hex}{self._suffix}"
        target.mkdir(parents=True, exist_ok=False)
        self.name = str(target)
        return self.name

    def __exit__(self, exc_type, exc, tb) -> None:
        self.cleanup()

    def cleanup(self) -> None:
        if self.name:
            shutil.rmtree(self.name, ignore_errors=True)
            self.name = None


def pytest_sessionstart(session) -> None:
    if TEST_TMP_ROOT.exists():
        shutil.rmtree(TEST_TMP_ROOT, ignore_errors=True)
    TEST_TMP_ROOT.mkdir(parents=True, exist_ok=True)

    temp_root = str(TEST_TMP_ROOT)
    tempfile.tempdir = temp_root
    os.environ["TMP"] = temp_root
    os.environ["TEMP"] = temp_root
    os.environ["TMPDIR"] = temp_root
    tempfile.TemporaryDirectory = ProjectTemporaryDirectory
