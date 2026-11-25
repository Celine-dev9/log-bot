"""
Configuration settings for the Human Code Reader Bot.
Customize timings, ignored paths, code extensions, and scroll behavior here.
"""

from typing import Set

# ==========================================
# Scrolling and Human Movement Parameters
# ==========================================

# Interval between scroll events in seconds (3 to 4 seconds to mimic human reading speed)
SCROLL_INTERVAL_MIN: float = 3.0
SCROLL_INTERVAL_MAX: float = 4.0

# Wheel scroll delta per interval.
# Negative value scrolls down on Windows (-120 is one standard mouse wheel notch).
# -100 to -160 gives a natural, steady scroll down of about 4-8 lines.
SCROLL_DELTA_MIN: int = -160
SCROLL_DELTA_MAX: int = -100

# Micro-steps per scroll action (subdivides wheel ticks for smoother visual scroll)
SCROLL_MICRO_STEPS: int = 3
SCROLL_MICRO_DELAY: float = 0.04

# Human mouse movement simulation:
# Chance of a subtle cursor drift between scrolls (reading gaze tracking)
MOUSE_DRIFT_CHANCE: float = 0.45
MOUSE_DRIFT_RANGE_X: int = 15   # Max pixels to wander horizontally
MOUSE_DRIFT_RANGE_Y: int = 12   # Max pixels to wander vertically

# Time to wait after opening a new file at line 1 before beginning scroll (in seconds)
FILE_LOAD_WAIT: float = 2.0

# Reading pacing: estimated lines scrolled per 3 to 4-second cycle
LINES_PER_SCROLL: int = 8

# Maximum seconds to spend on any single file (generous ceiling allowing full top-to-bottom reading)
MAX_SECONDS_PER_FILE: float = 600.0

# Minimum seconds to spend reading any code file
MIN_SECONDS_PER_FILE: float = 6.0

# Pause between finishing one file and opening the next file
PAUSE_BETWEEN_FILES: float = 2.0


# ==========================================
# File Filtering and Code Extensions
# ==========================================

# Code and text file extensions to include
CODE_EXTENSIONS: Set[str] = {
    # Web & Scripting
    ".py", ".pyw", ".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx",
    ".html", ".htm", ".css", ".scss", ".sass", ".less", ".vue", ".svelte",
    # Systems & Compiled
    ".c", ".h", ".cpp", ".hpp", ".cc", ".cxx", ".cs", ".java",
    ".go", ".rs", ".php", ".rb", ".dart", ".swift", ".kt", ".kts",
    ".scala", ".lua", ".r", ".pl", ".pm", ".zig",
    # Shell & Scripts
    ".sh", ".bash", ".zsh", ".bat", ".cmd", ".ps1", ".psm1",
    # Data, Query & Config
    ".json", ".jsonc", ".yaml", ".yml", ".toml", ".xml", ".sql",
    ".graphql", ".gql", ".prisma", ".proto", ".env.example",
    # Documentation & Text
    ".md", ".markdown", ".rst", ".txt", ".csv",
}

# Explicit filenames to include even without typical extensions
SPECIAL_FILENAMES: Set[str] = {
    "dockerfile", "makefile", "gemfile", "rakefile", "procfile",
    ".gitignore", ".env.example", ".editorconfig", ".prettierrc",
    "tsconfig.json", "package.json", "cargo.toml", "pyproject.toml"
}

# Extensions to strictly exclude (images, videos, audio, binary, fonts, archives)
ASSET_EXTENSIONS: Set[str] = {
    # Images
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".ico", ".webp",
    ".tiff", ".tif", ".psd", ".ai", ".raw", ".heic", ".avif",
    # Audio / Video
    ".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a", ".wma",
    ".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv", ".wmv",
    # Fonts
    ".ttf", ".otf", ".woff", ".woff2", ".eot",
    # Archives & Binaries
    ".zip", ".tar", ".gz", ".rar", ".7z", ".bz2", ".xz",
    ".exe", ".dll", ".so", ".dylib", ".bin", ".iso", ".dat",
    ".pyc", ".pyo", ".class", ".o", ".obj",
    # Documents / Misc
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"
}

# Directories to skip completely (caches, dependencies, version control)
IGNORE_DIRECTORIES: Set[str] = {
    ".git", ".svn", ".hg", ".idea", ".vscode",
    "node_modules", "venv", ".venv", "env", ".env",
    "__pycache__", ".pytest_cache", ".mypy_cache",
    "dist", "build", "out", "target", "bin", "obj",
    ".next", ".nuxt", ".cache", "coverage", ".turbo",
    ".terraform", "vendor"
}

# Specific large lockfiles to skip (reading thousands of auto-generated hashes is tedious)
IGNORE_FILES: Set[str] = {
    "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "poetry.lock",
    "cargo.lock", "composer.lock", "mix.lock"
}
