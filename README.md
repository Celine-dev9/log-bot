# Human Code Reader & Website Scraper Bot

An automated Python bot that merges website mirroring and human-like code reading:
1. **Scrapes Target Websites**: Opens a visible Chrome browser window, navigates through the target URL, performs realistic human scrolls (down, left/right, and up), and discovers internal subpages to generate a multi-page project.
2. **Code Only (Zero Media Assets)**: Strictly captures only `.html`, `.css`, and `.js` code files. Images, videos, audio, and font files are completely excluded.
3. **Dedicated Output Location**: Projects are written to individual folders inside `Desktop\scraped_projects` (completely separate from the bot workspace).
4. **Smart Reuse**: If a project was already scraped, the bot automatically reuses the existing code files and proceeds directly to reading without re-scraping from scratch.
5. **Human Reading in VS Code**:
   - Scrolls through code files from top to bottom every **randomized 3, 4, or 5 seconds**.
   - **Re-reading Inspection Mimic**: After every 7 to 9 scroll downs, automatically randomizes 1, 2, or 3 slight scroll ups to re-read previous snippets, then continues consistent scrolling down.
   - **Natural Mouse Roaming**: Cursor wanders organically across code lines and columns rather than staying locked in the center.
6. **Instant Pause & Resume (`F8`)**:
   - Press **`F8`** (or **`Ctrl + Alt + P`** / **`Pause`** key) at any time to pause reading.
   - Press **`F8`** again to resume right from the exact line and file where you paused.
7. **Continuous Loop**: Once all URLs have been scraped and read, the bot continues reading across all created projects in a continuous loop without opening browsers or re-scraping.
8. **Zero Screen Distraction**: The bot workspace/terminal window stays minimized in the background at all times.

---

## 🚀 How to Run

### 1. Configure Target URLs
In [`config.py`](file:///c:/Users/user/Desktop/peeples%20sites/log-mot/config.py), add as many website URLs as you want:

```python
TARGET_URLS = [
    "https://mku.ac.ke/",
    "https://www.aisfg.com/",
]
```

### 2. Run the Bot
In PowerShell or Command Prompt:

```powershell
python bot.py
```

You can also pass URLs directly on the command line:

```powershell
python bot.py "https://mku.ac.ke/" "https://www.aisfg.com/"
```

---

## ⌨️ Hotkeys & Controls

| Command | Key | Description |
| :--- | :--- | :--- |
| **Pause / Resume** | **`F8`** (or `Ctrl + Alt + P` / `Pause`) | Toggles pause on the reading loop. Resumes seamlessly from the exact spot when pressed again. |
| **Stop Bot** | **`Ctrl + C`** | Cleanly terminates the bot. |

---

## ⚙️ Configuration (`config.py`)

| Setting | Default | Description |
| :--- | :--- | :--- |
| `TARGET_URLS` | `[...]` | List of website URLs to scrape & read |
| `OUTPUT_ROOT` | `Desktop/scraped_projects` | Master folder where independent project folders are created |
| `SKIP_SCRAPING_IF_EXISTS` | `True` | Skips re-scraping if project folder already exists |
| `MAX_PAGES_PER_SITE` | `6` | Maximum internal subpages to discover per website |
| `SCROLL_INTERVAL_CHOICES` | `[3.0, 4.0, 5.0]` | Randomized scroll pacing (3, 4, or 5 seconds) |
| `SCROLL_UPS_TRIGGER_MIN` / `MAX` | `7` – `9` | Scroll downs before triggering a scroll-up inspection |
| `SCROLL_UP_COUNT_MIN` / `MAX` | `1` – `3` | Number of scroll ups when inspecting code |
