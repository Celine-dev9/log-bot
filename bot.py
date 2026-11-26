"""
Human Code Reader & Website Scraper Bot
========================================
1. Accepts website URLs from config.py, CLI arguments, or prompt.
2. For each URL:
   - Opens a visible Chrome browser on screen.
   - Performs human browsing scrolls (down, left/right, and back up).
   - Discovers internal pages across the website to build a multi-page project.
   - STRICTLY captures code only: HTML, CSS, and JavaScript (zero media/assets).
   - Saves each project in an independent folder under config.OUTPUT_ROOT (outside the bot).
   - Opens the project in VS Code and reads through each file from top to bottom (3 to 4s pace).
3. Once all URLs are scraped and read:
   - Runs in an infinite loop continuously reading through all created projects in VS Code.
   - No browser windows or scraping ever runs during repeat cycles.
4. The bot terminal window stays minimized in the background at all times.
"""

import os
import sys
import time
import math
import random
import argparse
from typing import List

import config
import human_mouse
from file_scanner import scan_code_files
from vscode_manager import VSCodeController
from scraper import scrape_website


def get_target_urls(cli_urls: List[str]) -> List[str]:
    """Gets target URLs from CLI arguments, config.py, or user input."""
    # 1. Check CLI arguments
    if cli_urls:
        return [u.strip() for u in cli_urls if u.strip()]

    # 2. Check config.TARGET_URLS
    if hasattr(config, "TARGET_URLS") and config.TARGET_URLS:
        return [u.strip() for u in config.TARGET_URLS if u.strip()]

    # 3. Interactive console fallback
    print("=" * 65)
    print("      HUMAN CODE READER & WEBSITE SCRAPER BOT")
    print("=" * 65)
    print("Enter website URLs to scrape & read (one per line).")
    print("Press Enter on an empty line when finished:\n")

    urls = []
    while True:
        try:
            line = input("Website URL: ").strip().strip('"').strip("'")
            if not line:
                if urls:
                    break
                print("Please enter at least one URL.")
                continue
            if not line.startswith(("http://", "https://")):
                line = "https://" + line
            urls.append(line)
        except (KeyboardInterrupt, EOFError):
            break

    return urls


def calculate_reading_plan(line_count: int) -> int:
    """
    Calculates how many ~3 to 4 second scroll cycles are needed to scroll
    completely from the top of the file to the very bottom at human reading speed.
    """
    if line_count <= 25:
        return 2

    # Advance through lines at LINES_PER_SCROLL pace from top to bottom
    lines_to_scroll = max(1, line_count - 25)
    scrolls = int(math.ceil(lines_to_scroll / max(1, config.LINES_PER_SCROLL)))
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
    Simulates human reading on a single code file:
      1. Opens file at line 1 in VS Code
      2. Moves mouse to editor area with organic Bezier curve
      3. Performs gentle scroll downs every 3 to 4 seconds from top to bottom
    """
    rel_path = file_info["relative_path"]
    lines = file_info["lines"]
    folder = file_info["folder"]

    cycle_prefix = f"[Loop {cycle_num}] " if cycle_num > 1 else ""
    print("\n" + "─" * 65)
    print(f"{cycle_prefix}[{current_index}/{total_files}] File: {rel_path}")
    print(f"     Folder: {folder if folder != '.' else '(root)'} | Lines: {lines}")
    print("─" * 65)

    # 1. Open file in VS Code at line 1
    vscode.open_file(file_info["path"])
    time.sleep(config.FILE_LOAD_WAIT)

    # 2. Position mouse naturally in editor area
    target_x, target_y = human_mouse.get_editor_center_point()
    human_mouse.move_mouse_human(target_x, target_y, duration=0.45)

    scroll_cycles = calculate_reading_plan(lines)
    print(f"  ↳ Reading pacing: {scroll_cycles} scroll increments (~3 to 4s each, top to bottom)")

    for cycle in range(1, scroll_cycles + 1):
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

    time.sleep(config.PAUSE_BETWEEN_FILES)


def read_project_folder(project_dir: str, cycle_num: int = 1) -> None:
    """Opens a project in VS Code and reads all its code files in order."""
    if not os.path.isdir(project_dir):
        return

    files = scan_code_files(project_dir)
    if not files:
        return

    total_lines = sum(f["lines"] for f in files)
    proj_name = os.path.basename(project_dir)
    print(f"\n[Project: {proj_name}] Reading {len(files)} code files (~{total_lines:,} lines)...")

    vscode = VSCodeController(project_dir)
    vscode.launch_new_instance()

    for idx, file_info in enumerate(files, start=1):
        read_file_humanly(vscode, file_info, idx, len(files), cycle_num=cycle_num)


def main():
    parser = argparse.ArgumentParser(description="Human Code Reader & Website Scraper Bot")
    parser.add_argument(
        "urls",
        nargs="*",
        default=[],
        help="One or more website URLs to scrape and read (optional; uses config.py if not provided)",
    )
    args = parser.parse_args()

    urls = get_target_urls(args.urls)
    if not urls:
        print("[Notice] No URLs provided. Exiting cleanly.")
        sys.exit(0)

    # Immediately minimize the bot workspace/terminal window so it stays in background
    human_mouse.minimize_bot_window()

    scraped_projects: List[str] = []

    # ==========================================================
    # PHASE 1: Scrape each URL and read its code in VS Code
    # ==========================================================
    print(f"\n[Bot] Starting Phase 1: Scraping and reading {len(urls)} website(s)...")

    for url_idx, target_url in enumerate(urls, start=1):
        print(f"\n{'=' * 65}")
        print(f"  [Website {url_idx}/{len(urls)}]: {target_url}")
        print(f"{'=' * 65}")

        # 1. Open visible Chrome browser and scrape HTML, CSS, JS
        try:
            project_dir = scrape_website(
                target_url,
                output_root=config.OUTPUT_ROOT,
                max_pages=config.MAX_PAGES_PER_SITE,
            )
        except Exception as e:
            print(f"[Error] Failed scraping {target_url}: {e}")
            project_dir = None

        # 2. If project was created, open in VS Code and read the code
        if project_dir and os.path.isdir(project_dir):
            scraped_projects.append(project_dir)
            try:
                read_project_folder(project_dir, cycle_num=1)
            except Exception as e:
                print(f"[Error] Issue reading {project_dir}: {e}")

        # Ensure bot window remains minimized after browser closes
        human_mouse.minimize_bot_window()

    if not scraped_projects:
        print("[Notice] No projects were successfully scraped. Exiting.")
        sys.exit(0)

    # ==========================================================
    # PHASE 2: Infinite loop reading across all projects in VS Code
    # (No more browser windows or scraping; pure code reading)
    # ==========================================================
    print("\n" + "=" * 65)
    print("  ALL WEBSITES SCRAPED & READ!")
    print("  Starting continuous reading loop across all created projects...")
    print("  (Browser will NOT open again. Press Ctrl+C at any time to stop)")
    print("=" * 65)

    loop_cycle = 2
    try:
        while True:
            for project_dir in scraped_projects:
                read_project_folder(project_dir, cycle_num=loop_cycle)

            print(f"\n[Loop] Finished cycle {loop_cycle} across all projects. Restarting from first project...")
            loop_cycle += 1
            time.sleep(config.PAUSE_BETWEEN_FILES)

    except KeyboardInterrupt:
        print("\n\n[Bot] Stopped by user (Ctrl+C). Exiting cleanly.")
        sys.exit(0)
    except Exception:
        # Silent clean exit on any unexpected termination
        sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
    except Exception:
        sys.exit(0)
