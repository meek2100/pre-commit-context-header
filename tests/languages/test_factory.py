# File: tests/languages/test_factory.py
from pathlib import Path
from context_headers.languages.factory import get_strategy_for_file
from context_headers.languages.strategies import (
    PythonStrategy,
    XmlStrategy,
    ShebangStrategy,
    DefaultStrategy,
    PhpStrategy,
    FrontmatterStrategy,
)


def test_factory_selects_correct_strategy() -> None:
    # Existing
    assert isinstance(get_strategy_for_file(Path("test.py")), PythonStrategy)
    assert isinstance(get_strategy_for_file(Path("test.xml")), XmlStrategy)
    assert isinstance(get_strategy_for_file(Path("test.sh")), ShebangStrategy)
    assert isinstance(get_strategy_for_file(Path("test.css")), DefaultStrategy)

    # Check Dockerfile fix
    assert isinstance(get_strategy_for_file(Path("Dockerfile")), ShebangStrategy)

    # New Mappings
    # PHP
    assert isinstance(get_strategy_for_file(Path("test.php")), PhpStrategy)

    # Astro
    assert isinstance(get_strategy_for_file(Path("test.astro")), FrontmatterStrategy)

    # Svelte, ASPX, CSHTML -> XmlStrategy (or behaves like it)
    assert isinstance(get_strategy_for_file(Path("test.svelte")), XmlStrategy)
    assert isinstance(get_strategy_for_file(Path("test.aspx")), XmlStrategy)
    assert isinstance(get_strategy_for_file(Path("test.cshtml")), XmlStrategy)

    # Shebang Scripts
    assert isinstance(get_strategy_for_file(Path("test.ps1")), ShebangStrategy)
    assert isinstance(get_strategy_for_file(Path("test.lua")), ShebangStrategy)
    assert isinstance(get_strategy_for_file(Path("test.r")), ShebangStrategy)
    assert isinstance(get_strategy_for_file(Path("test.jl")), ShebangStrategy)
    assert isinstance(get_strategy_for_file(Path("test.exs")), ShebangStrategy)
    assert isinstance(get_strategy_for_file(Path("test.dart")), ShebangStrategy)

    # Default Fallback (but supported extensions)
    # .nix, .hcl, .tf, .tfvars, .toml -> DefaultStrategy
    assert isinstance(get_strategy_for_file(Path("test.nix")), DefaultStrategy)
    assert isinstance(get_strategy_for_file(Path("test.hcl")), DefaultStrategy)
    assert isinstance(get_strategy_for_file(Path("test.tfvars")), DefaultStrategy)


def test_factory_returns_none_for_unsupported() -> None:
    assert get_strategy_for_file(Path("test.unknown_extension_123")) is None
