# File: tests/test_core.py
import pytest
from pathlib import Path
from unittest.mock import patch
from context_headers.core import process_file
from context_headers.config import MAX_FILE_SIZE_BYTES


def test_process_file_adds_header(tmp_path: Path) -> None:
    f = tmp_path / "test.py"
    f.write_text("print('hello')\n", encoding="utf-8")

    assert process_file(str(f), fix_mode=True)

    content = f.read_text(encoding="utf-8")
    assert content.startswith(f"# File: {f.as_posix()}\n")


def test_process_file_is_idempotent(tmp_path: Path) -> None:
    f = tmp_path / "repeat.py"
    f.write_text("print('once')\n", encoding="utf-8")

    process_file(str(f), fix_mode=True)
    first_pass = f.read_text()

    assert not process_file(str(f), fix_mode=True)
    assert f.read_text() == first_pass


def test_process_file_large_file_skipped(tmp_path: Path) -> None:
    f = tmp_path / "large.py"
    f.touch()
    with patch("pathlib.Path.stat") as mock_stat:
        mock_stat.return_value.st_size = MAX_FILE_SIZE_BYTES + 1
        assert not process_file(str(f), fix_mode=True)


def test_process_file_no_fix_mode(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    f = tmp_path / "check.py"
    f.write_text("print('hi')\n")

    assert process_file(str(f), fix_mode=False)
    assert "Missing or incorrect header" in capsys.readouterr().out
    assert f.read_text() == "print('hi')\n"
