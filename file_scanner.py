"""
Discovers and filters code files recursively within the specified target folder.
Strictly ignores image assets, media, binaries, caches, and dependency directories.
"""

import os
from typing import List, Dict, Any
import config


def is_binary_file(file_path: str) -> bool:
    """
    Checks if a file appears to be binary by inspecting initial chunk for null bytes.
    Prevents trying to scroll through compiled blobs or unrecognized binaries.
    """
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(1024)
            if b"\x00" in chunk:
                return True
        return False
    except Exception:
        return True


def count_file_lines(file_path: str) -> int:
    """Safely counts line count in a code file."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def is_valid_code_file(filename: str, file_path: str) -> bool:
    """
    Determines if a file is a valid code file based on extension and filename,
    strictly rejecting image/media assets, lockfiles, and binaries.
    """
    name_lower = filename.lower()
    base, ext = os.path.splitext(name_lower)

    # Check ignored lockfiles
    if name_lower in config.IGNORE_FILES:
        return False

    # Strictly reject image/media/asset extensions
    if ext in config.ASSET_EXTENSIONS:
        return False

    # Accept special filenames (e.g. Dockerfile, Makefile)
    if name_lower in config.SPECIAL_FILENAMES:
        return not is_binary_file(file_path)

    # Accept standard code extensions
    if ext in config.CODE_EXTENSIONS:
        return not is_binary_file(file_path)

    return False


def scan_code_files(root_path: str) -> List[Dict[str, Any]]:
    """
    Recursively scans the target directory for all code files, skipping
    ignored directories (e.g. node_modules, .git, venv).

    Returns a list of dicts with:
      - 'path': Absolute file path
      - 'relative_path': Path relative to root
      - 'folder': Containing folder name
      - 'lines': Number of lines
    """
    results: List[Dict[str, Any]] = []

    root_abs = os.path.abspath(root_path)
    if not os.path.isdir(root_abs):
        raise ValueError(f"Target path does not exist or is not a directory: {root_path}")

    for dirpath, dirnames, filenames in os.walk(root_abs):
        # Filter out ignored directories in-place to prevent traversing them
        dirnames[:] = [
            d for d in dirnames
            if d.lower() not in config.IGNORE_DIRECTORIES and not d.startswith(".")
        ]

        # Natural sort for directories and files
        dirnames.sort(key=str.lower)
        filenames.sort(key=str.lower)

        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if is_valid_code_file(filename, file_path):
                rel_path = os.path.relpath(file_path, root_abs)
                line_count = count_file_lines(file_path)
                results.append({
                    "path": file_path,
                    "relative_path": rel_path,
                    "folder": os.path.relpath(dirpath, root_abs),
                    "filename": filename,
                    "lines": line_count,
                })

    return results
