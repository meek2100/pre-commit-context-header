# File: tests/languages/test_factory.py
"""
Tests for the Strategy Factory.

Verifies that the correct strategy class is instantiated for different
file extensions and naming conventions (e.g., Dockerfiles, Dotfiles).
"""

from pathlib import Path
from context_headers.languages.factory import get_strategy_for_file
from context_headers.languages.strategies import (
    PythonStrategy,
    XmlStrategy,
    ShebangStrategy,
    PhpStrategy,
    FrontmatterStrategy,
    DockerfileStrategy,
)


def test_factory_selects_correct_strategy() -> None:
    """Verifies that the factory returns the correct Strategy class for various extensions."""
    # Existing
    assert isinstance(get_strategy_for_file(Path("test.py")), PythonStrategy)
    assert isinstance(get_strategy_for_file(Path("test.xml")), XmlStrategy)
    assert isinstance(get_strategy_for_file(Path("test.sh")), ShebangStrategy)

    # CSS maps to XmlStrategy (for @charset protection)
    assert isinstance(get_strategy_for_file(Path("test.css")), XmlStrategy)

    # Check Dockerfile fix
    assert isinstance(get_strategy_for_file(Path("Dockerfile")), DockerfileStrategy)
    # Check Dockerfile variants
    assert isinstance(get_strategy_for_file(Path("Dockerfile.dev")), DockerfileStrategy)
    assert isinstance(
        get_strategy_for_file(Path("Dockerfile.prod")), DockerfileStrategy
    )
    # Check Dockerfile case sensitivity
    assert isinstance(get_strategy_for_file(Path("dockerfile")), DockerfileStrategy)
    assert isinstance(get_strategy_for_file(Path("DOCKERFILE")), DockerfileStrategy)

    # PHP (Modern & Legacy)
    assert isinstance(get_strategy_for_file(Path("test.php")), PhpStrategy)
    assert isinstance(get_strategy_for_file(Path("test.phtml")), PhpStrategy)
    assert isinstance(get_strategy_for_file(Path("test.php3")), PhpStrategy)
    assert isinstance(get_strategy_for_file(Path("test.php4")), PhpStrategy)
    assert isinstance(get_strategy_for_file(Path("test.phps")), PhpStrategy)

    # Frontmatter
    assert isinstance(get_strategy_for_file(Path("test.astro")), FrontmatterStrategy)
    assert isinstance(get_strategy_for_file(Path("test.md")), FrontmatterStrategy)

    # XML-like
    assert isinstance(get_strategy_for_file(Path("test.svelte")), XmlStrategy)
    assert isinstance(get_strategy_for_file(Path("test.vue")), XmlStrategy)
    assert isinstance(get_strategy_for_file(Path("test.xhtml")), XmlStrategy)
    assert isinstance(get_strategy_for_file(Path("test.razor")), XmlStrategy)
    assert isinstance(get_strategy_for_file(Path("test.cshtml")), XmlStrategy)

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
    assert isinstance(get_strategy_for_file(Path("test.gleam")), ShebangStrategy)
    assert isinstance(get_strategy_for_file(Path("test.odin")), ShebangStrategy)

    # Config / Infra
    assert isinstance(get_strategy_for_file(Path("test.tf")), ShebangStrategy)
    assert isinstance(get_strategy_for_file(Path("test.toml")), ShebangStrategy)
    assert isinstance(get_strategy_for_file(Path("test.yaml")), ShebangStrategy)
    assert isinstance(get_strategy_for_file(Path("test.bat")), ShebangStrategy)

    # Dotfiles (Explicitly in config or via name)
    assert isinstance(get_strategy_for_file(Path(".bashrc")), ShebangStrategy)
    assert isinstance(get_strategy_for_file(Path(".gitignore")), ShebangStrategy)


def test_factory_returns_none_for_unsupported() -> None:
    """Verifies that the factory returns None for unsupported or binary files."""
    assert get_strategy_for_file(Path("test.unknown")) is None
    # Binary exclusions (or simply not in config)
    assert get_strategy_for_file(Path("test.json")) is None
    assert get_strategy_for_file(Path("test.class")) is None
    assert get_strategy_for_file(Path("test.pyc")) is None
    # .wasm IS supported now (WebAssembly text format uses ;;)
    # assert get_strategy_for_file(Path("test.wasm")) is None
