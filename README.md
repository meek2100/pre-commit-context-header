<!-- File: README.md -->
# pre-commit-context-header

![License](https://img.shields.io/github/license/meek2100/pre-commit-context-header)
[![CI Status](https://github.com/meek2100/pre-commit-context-header/actions/workflows/ci.yaml/badge.svg)](https://github.com/meek2100/pre-commit-context-header/actions/workflows/ci.yaml)

A universal [pre-commit](https://pre-commit.com) hook and CLI utility that enforces file path headers (banners) at the top of source files.

## Purpose

While file headers are not required by compilers, they provide critical context for **AI Coding Agents** and LLMs. By embedding the file path directly in the file content, the tool prevents "hallucinations" where an AI loses track of which file it is currently analyzing or editing.

## Usage

Add this to your `.pre-commit-config.yaml` in any project:

~~~yaml
repos:
  - repo: https://github.com/meek2100/pre-commit-context-header
    rev: v0.1.1 # Use the latest tag
    hooks:
      - id: context-headers
        args: [--fix] # Optional: Remove this line if you only want to check, not auto-fix
~~~

### CLI Options

You can also run the tool manually (e.g., via `uvx pre-commit-context-header` or after `uv tool install pre-commit-context-header` / `pip install pre-commit-context-header`):

- **Default (Check Mode)**: Scans files and exits with code `1` if any file has a missing or incorrect header, `0` if all files are correct.
- **`--fix`**: Automatically adds missing headers, fixes outdated paths, and deduplicates redundant headers.
- **`--remove`**: Removes context headers from all targeted files. Useful if you decide to uninstall the tool or reset files.
  - _Example:_ `uvx pre-commit-context-header --remove src/**/*.py`

## How It Works

The tool uses specialized parsing strategies to insert headers safely without corrupting syntax or parser instructions:

1. **Shebang Preservation**: Headers are placed *after* `#!/bin/bash` or `#!/usr/bin/env python`.
2. **Encoding Cookie Preservation**: Headers are placed *after* Python PEP 263 `# -*- coding: ... -*-` cookies.
3. **XML & Doctype Preservation**: Headers are placed *after* `<?xml ... ?>`, `<!DOCTYPE ...>`, and CSS `@charset`.
4. **Dockerfile Directive Preservation**: Headers are placed *after* Docker parser directives (`# syntax=`, `# escape=`, `# check=`).
5. **Frontmatter Preservation**: Headers are placed *after* YAML frontmatter blocks (`--- ... ---`) in Markdown and Astro files.
6. **Automatic Deduplication**: If multiple headers exist in the preamble, redundant headers are cleanly removed while preserving intentional comments inside the code body.

## Supported File Types

The tool supports context headers for **500+ file extensions**.

### 🛠 Python & Scripting

- **Python:** `.py`, `.pyi`, `.pyw`, `.pyx` (Strict PEP 263 preservation)
- **Shell:** `.sh`, `.bash`, `.zsh`, `.fish`, `.ksh`, `.csh`, `.tcsh`
- **Unix Tools:** `.awk`, `.sed`
- **Dotfiles:** `.bashrc`, `.bash_profile`, `.zshrc`, `.gitignore`, `.dockerignore`, `.editorconfig`

### ⚙️ System & Backend

- **C/C++/Obj-C:** `.c`, `.cpp`, `.h`, `.hpp`, `.cc`, `.cxx`, `.m`, `.mm`
- **Java/JVM:** `.java`, `.kt` (Kotlin), `.scala`, `.groovy`
- **Modern:** `.go`, `.rs` (Rust), `.swift`, `.dart`, `.zig`, `.nim`, `.v`, `.jl` (Julia)
- **Microsoft / .NET:** `.cs` (C#), `.fs` (F#), `.bat`, `.cmd`, `.ps1` (PowerShell), `.xaml`, `.csproj`, `.vbproj`

### 🎨 Web & Frontend

- **JavaScript:** `.js`, `.mjs`, `.cjs`
- **TypeScript:** `.ts`, `.mts`, `.cts`
- **React:** `.jsx`, `.tsx`
- **Styles:** `.css`, `.scss`, `.sass`, `.less`, `.styl`
- **Frameworks:** `.vue`, `.svelte`, `.astro`, `.aspx`, `.cshtml`
- **WebAssembly:** `.wat`

### 🧱 Config, Data, & Infrastructure

- **Config:** `.yaml`, `.yml`, `.toml`, `.ini`, `.conf`, `.cfg`, `.properties`
- **Infrastructure:** `Dockerfile`, `Containerfile`, `Makefile`, `.tf` (Terraform), `.hcl`, `.dockerfile`, `.nix`, `.bicep`, `.wxs` (WiX)
- **Data:** `.sql`, `.graphql`, `.proto` (Protobuf), `.json5`, `.hjson` (Note: Standard `.json` is excluded)
- **Documentation:** `.md`, `.rst`, `.tex`, `.adoc`

### 🧪 Functional & Scientific

- **Functional:** `.ex` (Elixir), `.erl` (Erlang), `.hs` (Haskell), `.clj` (Clojure), `.elm`, `.ml` (OCaml), `.rkt` (Racket)
- **Scientific:** `.r`, `.f90` (Fortran)

(See [`src/context_headers/config.py`](file:///home/agentsvc/repos/pre-commit-context-header/src/context_headers/config.py) for the complete, authoritative list.)

## Configuration

### Excluding Files

To exclude specific files (like minified assets, migrations, or generated documentation) from having headers added, use the `exclude` regex in your `.pre-commit-config.yaml`:

~~~yaml
hooks:
  - id: context-headers
    args: [--fix]
    exclude: ^(docs/|migrations/|.*\.min\.js)
~~~

### Safety & Operational Notes

- **Encoding**: This hook enforces UTF-8 encoding. Non-UTF-8 / binary files are automatically skipped.
- **Byte Order Mark (BOM)**: Files with a UTF-8 BOM (`\ufeff`) are skipped to prevent file corruption.
- **Line Endings**: The tool uses Python's universal newline mode and normalizes line endings to the system default of the machine running the hook.
- **File Size Limit**: Files larger than 1MB are automatically skipped to prevent hangs and performance degradation.
- **Lockfile Protection**: Standard lockfiles (e.g., `package-lock.json`, `uv.lock`, `Cargo.lock`, `go.sum`, `poetry.lock`) are automatically skipped internally to prevent corruption.
- **Ambiguity**: `.m` files are assumed to be Objective-C (using `//` comments). MATLAB/Octave users should exclude `.m` files in their pre-commit config to avoid syntax errors.
