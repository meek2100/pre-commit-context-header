# pre-commit-context-header

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
