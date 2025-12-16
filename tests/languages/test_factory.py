# File: tests/languages/test_factory.py
from pathlib import Path
from context_headers.languages.factory import get_strategy_for_file
from context_headers.languages.strategies import (
    PythonStrategy,
    XmlStrategy,
    ShebangStrategy,
    DefaultStrategy,
)


def test_factory_selects_correct_strategy() -> None:
    assert isinstance(get_strategy_for_file(Path("test.py")), PythonStrategy)
    assert isinstance(get_strategy_for_file(Path("test.xml")), XmlStrategy)
    assert isinstance(get_strategy_for_file(Path("test.sh")), ShebangStrategy)
    assert isinstance(get_strategy_for_file(Path("test.css")), DefaultStrategy)
    assert isinstance(get_strategy_for_file(Path("Dockerfile")), ShebangStrategy)


def test_factory_returns_none_for_unsupported() -> None:
    assert get_strategy_for_file(Path("test.unknown")) is None
