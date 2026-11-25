"""
Human Code Reader Bot for VS Code & Antigravity
================================================
Opens a new VS Code window with your selected folder, recursively scans
all code files, and scrolls down each file naturally mimicking human reading:
  - Opens target folder in a new VS Code instance
  - Minimizes the bot window so the target folder is prominently displayed
  - Strictly ignores images, video, audio, binaries, and dependencies
  - Simulates organic mouse movement and reading gaze drift
  - Performs gentle scroll down every 3 to 4 seconds from top to bottom
  - Repeats in a continuous loop from top-most file to bottom-most file
  - Makes ZERO edits or changes to any files
"""

import os
import sys
import time
import math
import random
import argparse

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
    Calculates how many ~3 to 4 second scroll cycles are needed to scroll
    completely from the top of the file to the very bottom at human reading speed.
    """
    if line_count <= 25:
        # Short file fits on one screen; 2 pauses allow human inspection
        return 2

    # A standard VS Code editor screen displays approx 25 lines.
    # To scroll all the way from line 1 to the bottom, advance through remaining lines:
    lines_to_scroll = max(1, line_count - 25)
    scrolls = int(math.ceil(lines_to_scroll / max(1, config.LINES_PER_SCROLL)))

    # Ensure full top-to-bottom coverage while respecting safety ceiling on massive files
    max_scrolls = int(config.MAX_SECONDS_PER_FILE / config.SCROLL_INTERVAL_MIN)
    return max(3, min(scrolls, max_scrolls))


def read_file_humanly(
    vscode: VSCodeController,
    file_info: dict,
    current_index: int,
    total_files: int,
    cycle_num: int = 1,
) -> None:
    """
    Simulates human reading on a single file:
      1. Opens file at line 1 in the target VS Code instance
      2. Moves mouse to editor area with organic Bezier curve
      3. Makes gentle scroll downs every 3 to 4 seconds from top to bottom
    """
    rel_path = file_info["relative_path"]
    lines = file_info["lines"]
    folder = file_info["folder"]

    cycle_prefix = f"[Loop {cycle_num}] " if cycle_num > 1 else ""
    print("\n" + "─" * 65)
    print(f"{cycle_prefix}[{current_index}/{total_files}] File: {rel_path}")
    print(f"     Folder: {folder if folder != '.' else '(root)'} | Lines: {lines}")
    print("─" * 65)

    # 1. Open file in target VS Code window at line 1
    vscode.open_file(file_info["path"])
    time.sleep(config.FILE_LOAD_WAIT)

    # 2. Position mouse naturally in editor area
    target_x, target_y = human_mouse.get_editor_center_point()
    human_mouse.move_mouse_human(target_x, target_y, duration=0.45)

    scroll_cycles = calculate_reading_plan(lines)
    print(f"  ↳ Reading pacing: {scroll_cycles} scroll increments (~3 to 4s each, top to bottom)")

    for cycle in range(1, scroll_cycles + 1):
        # Human reading interval: 3 to 4 seconds with subtle variation
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
        sys.exit(0)

    print(f"\n[Scanner] Scanning code files in: {target_folder}")
    files = scan_code_files(target_folder)

    if not files:
        print("[Scanner] No code files found in the specified directory.")
        sys.exit(0)

    total_lines = sum(f["lines"] for f in files)
    print(f"[Scanner] Found {len(files)} code files (approx {total_lines:,} total lines).")

    # Minimize bot window so target VS Code window takes the screen
    human_mouse.minimize_bot_window()

    # Launch new VS Code instance for target folder
    vscode = VSCodeController(target_folder)
    vscode.launch_new_instance()

    print("\n" + "=" * 65)
    print("  BOT RUNNING: Reading through code files in continuous loop...")
    print("  Press Ctrl+C at any time in this terminal to stop.")
    print("=" * 65)

    cycle_num = 1
    try:
        while True:
            for idx, file_info in enumerate(files, start=1):
                read_file_humanly(vscode, file_info, idx, len(files), cycle_num=cycle_num)

            print(f"\n[Loop] Completed cycle {cycle_num} (read from top-most to bottom-most file).")
            print("       Restarting from the first file...")
            cycle_num += 1
            time.sleep(config.PAUSE_BETWEEN_FILES)

    except KeyboardInterrupt:
        print("\n\n[Bot] Stopped by user (Ctrl+C). Exiting cleanly.")
        sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
    except Exception:
        sys.exit(0)
