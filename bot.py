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
   - Opens the project in VS Code and reads through each file from top to bottom (3 to 5s pace).
3. Once all URLs are scraped and read:
   - Runs in an infinite loop continuously reading through all created projects in VS Code.
   - No browser windows or scraping ever runs during repeat cycles.
4. Pause & Resume:
   - Press F8 (or Ctrl+Alt+P / Pause key) at any time to pause reading.
   - Press F8 again to seamlessly resume right where it left off.
5. The bot terminal window stays minimized in the background at all times.
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
from scraper import scrape_website, slugify_url


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
    Calculates how many ~3 to 5 second scroll cycles are needed to scroll
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
      2. Moves mouse to editor area with organic Bezier curve (not locked to center)
      3. Performs gentle scroll downs every 3, 4, or 5 seconds from top to bottom
      4. After 7 to 9 scroll downs, randomizes a slight scroll up (1 to 3 ticks) to inspect code
      5. Responds instantly to F8 (or Ctrl+Alt+P) to pause / resume without losing state
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
    human_mouse.pause_controller.sleep_with_pause_check(config.FILE_LOAD_WAIT)

    # 2. Position mouse naturally across code editor area (not just middle)
    target_x, target_y = human_mouse.get_random_editor_point()
    human_mouse.move_mouse_human(target_x, target_y, duration=0.45)

    scroll_cycles = calculate_reading_plan(lines)
    print(f"  ↳ Reading pacing: {scroll_cycles} scroll increments (randomized 3, 4, or 5s each, top to bottom)")

    # Scroll up inspection tracker (trigger after between 7 to 9 scroll downs)
    scroll_downs_since_up = 0
    next_scroll_up_trigger = random.randint(config.SCROLL_UPS_TRIGGER_MIN, config.SCROLL_UPS_TRIGGER_MAX)

    for cycle in range(1, scroll_cycles + 1):
        # Randomized 3, 4, or 5 seconds interval
        base_interval = random.choice(getattr(config, "SCROLL_INTERVAL_CHOICES", [3.0, 4.0, 5.0]))
        sleep_interval = max(config.SCROLL_INTERVAL_MIN, min(config.SCROLL_INTERVAL_MAX, base_interval + random.uniform(-0.25, 0.25)))

        # Micro-drift simulation during reading interval
        drift_wait = sleep_interval * 0.5
        human_mouse.pause_controller.sleep_with_pause_check(drift_wait)

        if random.random() < config.MOUSE_DRIFT_CHANCE:
            # Wander naturally across editor area (not stuck in center)
            if random.random() < 0.35:
                wander_x, wander_y = human_mouse.get_random_editor_point()
            else:
                curr_x, curr_y = human_mouse.get_cursor_pos()
                wander_x = curr_x + random.randint(-config.MOUSE_DRIFT_RANGE_X, config.MOUSE_DRIFT_RANGE_X)
                wander_y = curr_y + random.randint(-config.MOUSE_DRIFT_RANGE_Y, config.MOUSE_DRIFT_RANGE_Y)
            human_mouse.move_mouse_human(wander_x, wander_y, duration=0.25, steps=12)

        remaining_wait = max(0.1, sleep_interval - drift_wait)
        human_mouse.pause_controller.sleep_with_pause_check(remaining_wait)

        # Consistent scroll down
        delta = random.randint(config.SCROLL_DELTA_MIN, config.SCROLL_DELTA_MAX)
        human_mouse.smooth_scroll_down(
            delta=delta,
            micro_steps=config.SCROLL_MICRO_STEPS,
            micro_delay=config.SCROLL_MICRO_DELAY,
        )

        scroll_downs_since_up += 1
        progress_pct = int((cycle / scroll_cycles) * 100)
        print(f"  ↳ Scroll [{cycle}/{scroll_cycles}] ({progress_pct}%) - scrolled down")

        # After between 7 to 9 scroll downs: perform 1, 2, or 3 scroll ups to inspect previous code
        if scroll_downs_since_up >= next_scroll_up_trigger and cycle < scroll_cycles - 1:
            num_ups = random.randint(config.SCROLL_UP_COUNT_MIN, config.SCROLL_UP_COUNT_MAX)
            print(f"    ⤴ [Inspection] Scrolling up {num_ups} tick(s) to re-read previous snippet...")

            for _ in range(num_ups):
                human_mouse.pause_controller.sleep_with_pause_check(random.uniform(0.6, 1.1))
                up_delta = random.randint(config.SCROLL_UP_DELTA_MIN, config.SCROLL_UP_DELTA_MAX)
                human_mouse.smooth_scroll_up(
                    delta=up_delta,
                    micro_steps=config.SCROLL_MICRO_STEPS,
                    micro_delay=config.SCROLL_MICRO_DELAY,
                )
                # Move mouse to the snippet being re-read
                inspect_x, inspect_y = human_mouse.get_random_editor_point()
                human_mouse.move_mouse_human(inspect_x, inspect_y, duration=0.25, steps=10)

            # Brief pause while re-reading before resuming consistent scroll down
            human_mouse.pause_controller.sleep_with_pause_check(random.uniform(1.2, 1.8))
            scroll_downs_since_up = 0
            next_scroll_up_trigger = random.randint(config.SCROLL_UPS_TRIGGER_MIN, config.SCROLL_UPS_TRIGGER_MAX)

    human_mouse.pause_controller.sleep_with_pause_check(config.PAUSE_BETWEEN_FILES)


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

    print("\n" + "=" * 65)
    print("      HUMAN CODE READER & WEBSITE SCRAPER BOT")
    print(f"      Commands: Press {config.PAUSE_HOTKEY_NAME} to PAUSE / RESUME")
    print("                Press Ctrl+C to STOP")
    print("=" * 65)

    # ==========================================================
    # PHASE 1: Scrape each URL (or reuse) and read its code in VS Code
    # ==========================================================
    print(f"\n[Bot] Phase 1: Processing {len(urls)} website(s)...")

    for url_idx, target_url in enumerate(urls, start=1):
        print(f"\n{'=' * 65}")
        print(f"  [Website {url_idx}/{len(urls)}]: {target_url}")
        print(f"{'=' * 65}")

        slug = slugify_url(target_url)
        project_dir = os.path.join(config.OUTPUT_ROOT, slug)

        # Check if project already exists to avoid re-scraping from scratch
        if getattr(config, "SKIP_SCRAPING_IF_EXISTS", True) and os.path.isdir(project_dir):
            print(f"[Reuse] Project already exists: {project_dir}")
            print(f"        Skipping re-scrape and proceeding directly to code reading.")
        else:
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

        # 2. If project is ready, open in VS Code and read the code
        if project_dir and os.path.isdir(project_dir):
            scraped_projects.append(project_dir)
            try:
                read_project_folder(project_dir, cycle_num=1)
            except Exception as e:
                print(f"[Error] Issue reading {project_dir}: {e}")

        # Ensure bot window remains minimized
        human_mouse.minimize_bot_window()

    if not scraped_projects:
        print("[Notice] No projects ready to read. Exiting.")
        sys.exit(0)

    # ==========================================================
    # PHASE 2: Infinite loop reading across all projects in VS Code
    # (No browser windows or scraping; pure continuous code reading)
    # ==========================================================
    print("\n" + "=" * 65)
    print("  ALL WEBSITES PROCESSED & READ!")
    print("  Starting continuous reading loop across all created projects...")
    print(f"  (Hotkeys: Press {config.PAUSE_HOTKEY_NAME} to PAUSE / RESUME)")
    print("  (Press Ctrl+C at any time to stop)")
    print("=" * 65)

    loop_cycle = 2
    try:
        while True:
            for project_dir in scraped_projects:
                read_project_folder(project_dir, cycle_num=loop_cycle)

            print(f"\n[Loop] Finished cycle {loop_cycle} across all projects. Restarting from first project...")
            loop_cycle += 1
            human_mouse.pause_controller.sleep_with_pause_check(config.PAUSE_BETWEEN_FILES)

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
