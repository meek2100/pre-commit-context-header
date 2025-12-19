# File: tests/languages/test_factory.py
from pathlib import Path
from context_headers.languages.factory import get_strategy_for_file
from context_headers.languages.strategies import (
    PythonStrategy,
    XmlStrategy,
    ShebangStrategy,
    PhpStrategy,
    FrontmatterStrategy,
)


def test_factory_selects_correct_strategy() -> None:
    # Existing
    assert isinstance(get_strategy_for_file(Path("test.py")), PythonStrategy)
    assert isinstance(get_strategy_for_file(Path("test.xml")), XmlStrategy)
    assert isinstance(get_strategy_for_file(Path("test.sh")), ShebangStrategy)

    # CSS now maps to ShebangStrategy (default fallback)
    assert isinstance(get_strategy_for_file(Path("test.css")), ShebangStrategy)

    # Check Dockerfile fix
    assert isinstance(get_strategy_for_file(Path("Dockerfile")), ShebangStrategy)
    # Check Dockerfile variants (New test case)
    assert isinstance(get_strategy_for_file(Path("Dockerfile.dev")), ShebangStrategy)
    assert isinstance(get_strategy_for_file(Path("Dockerfile.prod")), ShebangStrategy)

    # PHP
    assert isinstance(get_strategy_for_file(Path("test.php")), PhpStrategy)
    assert isinstance(get_strategy_for_file(Path("test.phtml")), PhpStrategy)

    # Frontmatter
    assert isinstance(get_strategy_for_file(Path("test.astro")), FrontmatterStrategy)
    assert isinstance(get_strategy_for_file(Path("test.md")), FrontmatterStrategy)

    # XML-like
    assert isinstance(get_strategy_for_file(Path("test.svelte")), XmlStrategy)
    assert isinstance(get_strategy_for_file(Path("test.vue")), XmlStrategy)
    assert isinstance(get_strategy_for_file(Path("test.aspx")), XmlStrategy)
    assert isinstance(get_strategy_for_file(Path("test.jsp")), XmlStrategy)

    # Scripts / Shebangs
    assert isinstance(get_strategy_for_file(Path("test.ps1")), ShebangStrategy)
    assert isinstance(get_strategy_for_file(Path("test.lua")), ShebangStrategy)
    assert isinstance(get_strategy_for_file(Path("test.rb")), ShebangStrategy)
    assert isinstance(get_strategy_for_file(Path("test.pl")), ShebangStrategy)

    # New Modern Languages
    assert isinstance(get_strategy_for_file(Path("test.mojo")), ShebangStrategy)
    assert isinstance(get_strategy_for_file(Path("test.go")), ShebangStrategy)
    assert isinstance(get_strategy_for_file(Path("test.rs")), ShebangStrategy)
    assert isinstance(get_strategy_for_file(Path("test.zig")), ShebangStrategy)
    assert isinstance(get_strategy_for_file(Path("test.v")), ShebangStrategy)
    assert isinstance(get_strategy_for_file(Path("test.nim")), ShebangStrategy)

    # Config / Infra
    assert isinstance(get_strategy_for_file(Path("test.tf")), ShebangStrategy)
    assert isinstance(get_strategy_for_file(Path("test.toml")), ShebangStrategy)
    assert isinstance(get_strategy_for_file(Path("test.yaml")), ShebangStrategy)
    assert isinstance(get_strategy_for_file(Path("test.bat")), ShebangStrategy)
    assert isinstance(get_strategy_for_file(Path("test.tab")), ShebangStrategy)

    # Exotic
    assert isinstance(get_strategy_for_file(Path("test.🔥")), ShebangStrategy)

    # Dotfiles
    assert isinstance(get_strategy_for_file(Path(".bashrc")), ShebangStrategy)
    assert isinstance(get_strategy_for_file(Path(".zprofile")), ShebangStrategy)


def test_factory_returns_none_for_unsupported() -> None:
    assert get_strategy_for_file(Path("test.unknown")) is None
    # Binary exclusions
    assert get_strategy_for_file(Path("test.json")) is None
    assert get_strategy_for_file(Path("test.class")) is None
    assert get_strategy_for_file(Path("test.pyc")) is None
    assert get_strategy_for_file(Path("test.wasm")) is None
