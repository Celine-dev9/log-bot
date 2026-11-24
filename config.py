"""
Configuration settings for the Human Code Reader Bot.
Customize timings, ignored paths, code extensions, and scroll behavior here.
"""

from typing import Set

# ==========================================
# Scrolling and Human Movement Parameters
# ==========================================

# Interval between scroll events in seconds (approx 3 seconds as requested)
SCROLL_INTERVAL_MIN: float = 2.7
SCROLL_INTERVAL_MAX: float = 3.3

# Wheel scroll delta per interval.
# Negative value scrolls down on Windows (-120 is one standard mouse wheel notch).
# Using -60 to -120 gives a gentle, realistic scroll down.
SCROLL_DELTA_MIN: int = -120
SCROLL_DELTA_MAX: int = -80

# Micro-steps per scroll action (subdivides wheel ticks for smoother visual scroll)
SCROLL_MICRO_STEPS: int = 2
SCROLL_MICRO_DELAY: float = 0.05

# Human mouse movement simulation:
# Chance of a subtle cursor drift between scrolls (reading gaze tracking)
MOUSE_DRIFT_CHANCE: float = 0.45
MOUSE_DRIFT_RANGE_X: int = 15   # Max pixels to wander horizontally
MOUSE_DRIFT_RANGE_Y: int = 12   # Max pixels to wander vertically

# Time to wait after opening a new file before beginning scroll (in seconds)
FILE_LOAD_WAIT: float = 2.0

# Reading pacing: estimated lines scrolled per 3-second cycle
LINES_PER_SCROLL: int = 10

# Maximum seconds to spend on any single file (prevents infinite scrolling on 5,000+ line files)
MAX_SECONDS_PER_FILE: float = 45.0

# Minimum seconds to spend reading any code file
MIN_SECONDS_PER_FILE: float = 6.0

# Pause between finishing one file and opening the next file
PAUSE_BETWEEN_FILES: float = 1.8


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
