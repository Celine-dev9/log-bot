# Human Code Reader & Website Scraper Bot

An automated Python bot that merges website mirroring and human-like code reading:
1. **Scrapes Target Websites**: Opens a visible Chrome browser window, navigates through the target URL, performs realistic human scrolls (down, left/right, and up), and discovers internal subpages to generate a multi-page project.
2. **Code Only (Zero Media Assets)**: Strictly captures only `.html`, `.css`, and `.js` code files. Images, videos, audio, and font files are completely excluded.
3. **Dedicated Output Location**: Projects are written to individual folders inside `Desktop\scraped_projects` (completely separate from the bot workspace).
4. **Human Reading in VS Code**: Opens the scraped project in a fresh VS Code instance and scrolls through the code files from top to bottom every 3 to 4 seconds with realistic mouse gaze drift.
5. **Continuous Loop**: Once all URLs have been scraped and read, the bot continues reading across all created projects in a continuous loop without opening browsers or re-scraping.
6. **Zero Screen Distraction**: The bot workspace/terminal window stays minimized in the background at all times.

---

## 🚀 How to Run

### 1. Configure Target URLs
In [`config.py`](file:///c:/Users/user/Desktop/peeples%20sites/log-mot/config.py), add as many website URLs as you want:

```python
TARGET_URLS = [
    "https://www.track-trace.com/aircargo",
    "https://example.com",
]
```

### 2. Run the Bot
In PowerShell or Command Prompt:

```powershell
python bot.py
```

You can also pass URLs directly on the command line:

```powershell
python bot.py "https://www.track-trace.com/aircargo" "https://example.com"
```

---

## ⚙️ Configuration (`config.py`)

| Setting | Default | Description |
| :--- | :--- | :--- |
| `TARGET_URLS` | `[...]` | List of website URLs to scrape & read |
| `OUTPUT_ROOT` | `Desktop/scraped_projects` | Master folder where independent project folders are created |
| `MAX_PAGES_PER_SITE` | `6` | Maximum internal subpages to discover per website |
| `SCROLL_INTERVAL_MIN` / `MAX` | `3.0` – `4.0`s | Mouse scroll interval mimicking human reading speed |
| `SCROLL_DELTA_MIN` / `MAX` | `-160` – `-100` | Wheel scroll notch intensity (4 to 8 lines) |
| `LINES_PER_SCROLL` | `8` | Lines scrolled per cycle |

---

## 🛑 Stopping the Bot
Press **`Ctrl + C`** in the terminal running `bot.py` at any time to cleanly stop the bot.
