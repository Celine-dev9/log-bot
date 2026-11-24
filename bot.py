"""
Human Code Reader Bot for VS Code & Antigravity
================================================
Opens a new VS Code window with your selected folder, recursively scans
all code files, and scrolls down each file naturally mimicking human reading:
  - Opens folders and code files inside them
  - Strictly ignores images, video, audio, binaries, and dependencies
  - Simulates organic human mouse movement and natural reading gaze drift
  - Performs gentle scroll down every ~3 seconds
  - Makes ZERO edits or changes to any files

Run directly:
  python bot.py
  python bot.py "C:\\path\\to\\your\\project"
"""

import os
import sys
import time
import random
import argparse
from typing import Optional

import config
import human_mouse
from file_scanner import scan_code_files
from vscode_manager import VSCodeController


def prompt_folder_path() -> str:
    """Prompts the user to enter a folder path with optional GUI folder picker."""
    print("=" * 65)
    print("      HUMAN CODE READER BOT FOR VS CODE & ANTIGRAVITY")
    print("=" * 65)

    # Try graphical folder picker if available (very convenient on Windows)
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        selected = filedialog.askdirectory(title="Select Folder to Read in VS Code")
        root.destroy()
        if selected and os.path.isdir(selected):
            print(f"Selected via dialog: {selected}")
            return selected
    except Exception:
        pass

    # Console input fallback
    while True:
        user_input = input("\nEnter the full folder path to open: ").strip().strip('"').strip("'")
        if not user_input:
            print("Path cannot be empty. Please enter a valid directory path.")
            continue
        if not os.path.isdir(user_input):
            print(f"Error: Directory '{user_input}' does not exist. Please try again.")
            continue
        return user_input


def calculate_reading_plan(line_count: int) -> int:
    """
    Calculates how many ~3-second scroll cycles are needed based on file size.
    Small files need fewer scrolls, large files cap at MAX_SECONDS_PER_FILE.
    """
    if line_count <= 25:
        # Fits on one screen without much scrolling
        return 2

    # Estimate scrolls needed
    estimated_scrolls = max(2, int(line_count / config.LINES_PER_SCROLL))

    # Cap by max seconds allowed per file
    max_scrolls = int(config.MAX_SECONDS_PER_FILE / config.SCROLL_INTERVAL_MIN)
    min_scrolls = int(config.MIN_SECONDS_PER_FILE / config.SCROLL_INTERVAL_MAX)

    return max(min_scrolls, min(estimated_scrolls, max_scrolls))


def read_file_humanly(
    vscode: VSCodeController,
    file_info: dict,
    current_index: int,
    total_files: int,
) -> None:
    """
    Simulates human reading on a single file:
      1. Opens file at line 1 in the VS Code instance
      2. Moves mouse to editor area with organic Bezier curve
      3. Makes slight scrolls down every ~3 seconds with natural mouse drift
    """
    rel_path = file_info["relative_path"]
    lines = file_info["lines"]
    folder = file_info["folder"]

    print("\n" + "─" * 65)
    print(f"[{current_index}/{total_files}] File: {rel_path}")
    print(f"     Folder: {folder if folder != '.' else '(root)'} | Lines: {lines}")
    print("─" * 65)

    # 1. Open file in VS Code at line 1
    vscode.open_file(file_info["path"])
    time.sleep(config.FILE_LOAD_WAIT)

    # 2. Position mouse naturally in editor area
    if vscode.hwnd:
        target_x, target_y = human_mouse.get_random_editor_point(vscode.hwnd)
        human_mouse.move_mouse_human(target_x, target_y, duration=0.45)
    else:
        # Fallback to center-screen area if hwnd isn't directly bound
        target_x, target_y = human_mouse.get_cursor_pos()

    scroll_cycles = calculate_reading_plan(lines)
    print(f"  ↳ Reading pacing: {scroll_cycles} scroll increments (~3s each)")

    for cycle in range(1, scroll_cycles + 1):
        # Human reading interval: approx 3 seconds with subtle variation
        sleep_interval = random.uniform(config.SCROLL_INTERVAL_MIN, config.SCROLL_INTERVAL_MAX)

        # Micro-drift simulation during reading interval
        drift_wait = sleep_interval * 0.5
        time.sleep(drift_wait)

        if random.random() < config.MOUSE_DRIFT_CHANCE:
            curr_x, curr_y = human_mouse.get_cursor_pos()
            drift_x = curr_x + random.randint(-config.MOUSE_DRIFT_RANGE_X, config.MOUSE_DRIFT_RANGE_X)
            drift_y = curr_y + random.randint(-config.MOUSE_DRIFT_RANGE_Y, config.MOUSE_DRIFT_RANGE_Y)
            human_mouse.move_mouse_human(drift_x, drift_y, duration=0.25, steps=12)

        remaining_wait = max(0.1, sleep_interval - drift_wait)
        time.sleep(remaining_wait)

        # Gentle scroll down
        delta = random.randint(config.SCROLL_DELTA_MIN, config.SCROLL_DELTA_MAX)
        human_mouse.smooth_scroll_down(
            delta=delta,
            micro_steps=config.SCROLL_MICRO_STEPS,
            micro_delay=config.SCROLL_MICRO_DELAY,
        )

        progress_pct = int((cycle / scroll_cycles) * 100)
        print(f"  ↳ Scroll [{cycle}/{scroll_cycles}] ({progress_pct}%) - scrolled down")

    # Short pause after completing a file before moving to the next
    time.sleep(config.PAUSE_BETWEEN_FILES)


def main():
    parser = argparse.ArgumentParser(description="Human Code Reader Bot for VS Code & Antigravity")
    parser.add_argument(
        "folder",
        nargs="?",
        default=None,
        help="Path to the folder to open and read (optional; prompted if not provided)",
    )
    args = parser.parse_args()

    target_folder = args.folder if args.folder else prompt_folder_path()
    target_folder = os.path.abspath(target_folder)

    if not os.path.isdir(target_folder):
        print(f"[Error] Directory not found: {target_folder}")
        sys.exit(1)

    print(f"\n[Scanner] Scanning code files in: {target_folder}")
    files = scan_code_files(target_folder)

    if not files:
        print("[Scanner] No code files found in the specified directory.")
        print("          (Images, assets, and dependency folders like node_modules are ignored)")
        sys.exit(0)

    total_lines = sum(f["lines"] for f in files)
    print(f"[Scanner] Found {len(files)} code files (approx {total_lines:,} total lines).")
    print(f"[Scanner] Asset/binary files and ignore folders were excluded.")

    # Launch new VS Code instance
    try:
        vscode = VSCodeController(target_folder)
        vscode.launch_new_instance()
    except Exception as e:
        print(f"[Error] Failed to launch VS Code: {e}")
        sys.exit(1)

    print("\n" + "=" * 65)
    print("  BOT RUNNING: Reading through code files with human scrolls...")
    print("  Press Ctrl+C at any time in this terminal to stop.")
    print("=" * 65)

    try:
        for idx, file_info in enumerate(files, start=1):
            read_file_humanly(vscode, file_info, idx, len(files))

        print("\n" + "=" * 65)
        print("  FINISHED: Successfully read through all code files!")
        print("=" * 65)

    except KeyboardInterrupt:
        print("\n\n[Bot] Paused/Stopped by user (Ctrl+C). Exiting cleanly.")
        sys.exit(0)


if __name__ == "__main__":
    main()
