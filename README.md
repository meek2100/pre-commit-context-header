
# pre-commit-context-header

![PyPI - Version](https://img.shields.io/pypi/v/pre-commit-context-header)
![Python Versions](https://img.shields.io/pypi/pyversions/pre-commit-context-header)
![License](https://img.shields.io/github/license/meek2100/pre-commit-context-header)
[![CI Status](https://github.com/meek2100/pre-commit-context-header/actions/workflows/ci.yaml/badge.svg)](https://github.com/meek2100/pre-commit-context-header/actions/workflows/ci.yaml)

A [pre-commit](https://pre-commit.com) hook that enforces file path headers (banners) at the top of source files.

## Purpose

While file headers are not required by compilers, they provide critical context for **AI Coding Agents** and LLMs. By including the file path in the file content, we reduce the likelihood of "hallucinations" where an AI loses track of which file it is currently analyzing or editing.

## Usage

Add this to your `.pre-commit-config.yaml` in any project:

~~~yaml
repos:
  - repo: https://github.com/meek2100/pre-commit-context-header
    rev: v0.1.0 # Use the latest tag
    hooks:
      - id: context-headers
        args: [--fix] # Optional: Remove this line if you only want to check, not auto-fix
~~~

## Supported File Types

The tool supports context headers for **100+ file extensions**, including:

### 🐍 Scripting & Shell
- **Unix:** `.sh`, `.bash`, `.zsh`, `.fish`, `.tcl`, `.awk`, `.pl` (Perl), `.rb` (Ruby), `.lua`
- **Windows:** `.ps1`, `.psm1` (PowerShell), `.bat`, `.cmd`
- **Python:** `.py`, `.pyi`, `.pyw`, `.pyx` (plus strict PEP 263 encoding preservation)

### ☕ Backend & Systems
- **Major:** `.java`, `.go`, `.rs` (Rust), `.c`, `.cpp`, `.h`, `.hpp`, `.cs` (C#), `.kt` (Kotlin), `.swift`
- **PHP:** `.php`, `.phtml`, `.phps` (Handles `<?php` and short tags safely)
- **Functional:** `.ex`, `.exs` (Elixir), `.erl` (Erlang), `.hs` (Haskell), `.cljs` (ClojureScript), `.elm`
- **Niche/Systems:** `.zig`, `.nim`, `.v` (VLang), `.jl` (Julia), `.dart`, `.sol` (Solidity)

### 🌐 Web & Frontend
- **JS/TS:** `.js`, `.ts`, `.jsx`, `.tsx`, `.mjs`, `.cjs`
- **Frameworks:** `.vue`, `.svelte`, `.astro` (Handles Frontmatter), `.aspx`, `.cshtml`, `.jsp`
- **Styles:** `.css`, `.scss`, `.sass`, `.less`

### 🏗️ Infrastructure & Config
- **Cloud:** `.tf` (Terraform), `.hcl`, `.bicep`, `.nix`, `.dockerfile`
- **Data:** `.sql`, `.yaml`, `.yml`, `.toml`, `.json` (excluded by default), `.xml`
- **Protocols:** `.graphql`, `.proto` (Protobuf), `.prisma`, `.ini`, `.conf`

### 🚀 Emerging & Ultra-Modern
- **AI/Next-Gen:** `.mojo`, `.carbon`, `.val`, `.gleam`, `.odin`, `.roc`, `.typ` (Typst)

## Configuration

### Excluding Files

To exclude specific files (like minified assets, migrations, or generated documentation) from having headers added, use the `exclude` regex in your `.pre-commit-config.yaml`:

~~~yaml
hooks:
  - id: context-headers
    args: [--fix]
    exclude: ^(docs/|migrations/|.*\.min\.js)
~~~

### Notes

- **Encoding**: This hook enforces UTF-8 encoding.
- **Line Endings**: The tool uses Python's universal newline mode and may normalize line endings to the system default of the machine running the hook.
- **Safety**: Files larger than 1MB are automatically skipped to prevent performance issues.
