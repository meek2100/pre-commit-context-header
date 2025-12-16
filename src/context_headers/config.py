# File: src/context_headers/config.py
from __future__ import annotations

# Safety: Do not process files larger than this (1MB) to prevent hangs.
MAX_FILE_SIZE_BYTES = 1024 * 1024

# Configuration: Comment styles for various extensions.
COMMENT_STYLES: dict[str, str] = {
    # Scripting / Config
    ".py": "# File: {}",
    ".yaml": "# File: {}",
    ".yml": "# File: {}",
    ".sh": "# File: {}",
    ".bash": "# File: {}",
    ".zsh": "# File: {}",
    ".toml": "# File: {}",
    ".tf": "# File: {}",
    ".dockerfile": "# File: {}",
    ".rb": "# File: {}",
    ".pl": "# File: {}",
    ".conf": "# File: {}",
    ".properties": "# File: {}",
    ".env": "# File: {}",
    ".ini": "; File: {}",
    # Database
    ".sql": "-- File: {}",
    # Web / JS
    ".js": "// File: {}",
    ".ts": "// File: {}",
    ".jsx": "// File: {}",
    ".tsx": "// File: {}",
    ".css": "/* File: {} */",
    ".scss": "/* File: {} */",
    ".less": "/* File: {} */",
    # Compiled / Systems
    ".java": "// File: {}",
    ".kt": "// File: {}",
    ".rs": "// File: {}",
    ".go": "// File: {}",
    ".c": "// File: {}",
    ".cpp": "// File: {}",
    ".h": "// File: {}",
    ".hpp": "// File: {}",
    ".cs": "// File: {}",
    ".swift": "// File: {}",
    # HTML / Markdown / XML (Using visible comments)
    ".html": "<!-- File: {} -->",
    ".md": "<!-- File: {} -->",
    ".xml": "<!-- File: {} -->",
    ".vue": "<!-- File: {} -->",
}
