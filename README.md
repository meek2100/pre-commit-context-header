<!-- File: README.md -->
# pre-commit-context-header

![License](https://img.shields.io/github/license/meek2100/pre-commit-context-header)
[![CI Status](https://github.com/meek2100/pre-commit-context-header/actions/workflows/ci.yaml/badge.svg)](https://github.com/meek2100/pre-commit-context-header/actions/workflows/ci.yaml)

A [pre-commit](https://pre-commit.com) hook that enforces file path headers (banners) at the top of source files.

## Purpose

While file headers are not required by compilers, they provide critical context for **AI Coding Agents** and LLMs. By including the file path in the file content, we reduce the likelihood of "hallucinations" where an AI loses track of which file it is currently analyzing or editing.

## Usage

Add this to your `.pre-commit-config.yaml` in any project:

```yaml
repos:
  - repo: https://github.com/meek2100/pre-commit-context-header
    rev: v0.1.0 # Use the latest tag
    hooks:
      - id: context-headers
        args: [--fix] # Optional: Remove this line if you only want to check, not auto-fix
```

### CLI Options

You can also run the tool manually (after `pip install pre-commit-context-header`):

- **`--fix`**: Automatically adds or updates missing headers.
- **`--remove`**: **Removes** context headers from all targeted files. Useful if you decide to uninstall the tool or need to "reset" files.
- _Example:_ `context-headers --remove src/**/*.py`

## Supported File Types

The tool supports context headers for **200+ file extensions**.

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
- **Infrastructure:** `.tf` (Terraform), `.hcl`, `.dockerfile`, `.nix`, `.bicep`, `.wxs` (WiX)
- **Data:** `.sql`, `.graphql`, `.proto` (Protobuf), `.json5`, `.hjson` (Note: Standard `.json` is excluded)
- **Documentation:** `.md`, `.rst`, `.tex`, `.adoc`

### 🧪 Functional & Scientific

- **Functional:** `.ex` (Elixir), `.erl` (Erlang), `.hs` (Haskell), `.clj` (Clojure), `.elm`, `.ml` (OCaml), `.rkt` (Racket)
- **Scientific:** `.r`, `.f90` (Fortran)

(See `src/context_headers/config.py` for the complete, authoritative list.)

## Configuration

### Excluding Files

To exclude specific files (like minified assets, migrations, or generated documentation) from having headers added, use the `exclude` regex in your `.pre-commit-config.yaml`:

```yaml
hooks:
  - id: context-headers
    args: [--fix]
    exclude: ^(docs/|migrations/|.*\.min\.js)
```

### Notes

- **Encoding**: This hook enforces UTF-8 encoding.
- **Line Endings**: The tool uses Python's universal newline mode and may normalize line endings to the system default of the machine running the hook.
- **Safety**: Files larger than 1MB are automatically skipped to prevent performance issues.
- **Safety**: Standard lockfiles (e.g., `package-lock.json`, `Cargo.lock`, `go.sum`) are automatically skipped internally to prevent corruption.
- **Ambiguity**: `.m` files are assumed to be Objective-C (using `//` comments). MATLAB/Octave users should exclude `.m` files in their pre-commit config to avoid syntax errors.
