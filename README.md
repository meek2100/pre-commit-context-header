
# pre-commit-context-header

![PyPI - Version](https://img.shields.io/pypi/v/pre-commit-context-header)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/meek2100/pre-commit-context-header/ci.yaml)

A [pre-commit](https://pre-commit.com) hook that enforces file path headers (banners) at the top of source files.

## Purpose

While file headers are not required by compilers, they provide critical context for **AI Coding Agents** and LLMs. By including the file path in the file content, we reduce the likelihood of "hallucinations" where an AI loses track of which file it is currently analyzing or editing.

## Usage

Add this to your `.pre-commit-config.yaml` in any project:

```yaml
repos:
  - repo: [https://github.com/meek2100/pre-commit-context-header](https://github.com/meek2100/pre-commit-context-header)
    rev: v0.1.0 # Use the latest tag
    hooks:
      - id: context-headers
        args: [--fix] # Optional: Remove this line if you only want to check, not auto-fix
```

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
