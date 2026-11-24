# Human Code Reader Bot for VS Code & Antigravity

A realistic Python bot that opens a new instance of Visual Studio Code with a target folder of your choice, scans all code files (recursively through folders), and gently scrolls through each file mimicking human reading behavior.

---

## ✨ Features

- **Opens a Fresh VS Code Instance**: Launches a separate, clean VS Code window (`code -n <folder>`) specifically for the folder you select.
- **Strict Code File Filtering**:
  - **Included**: Python (`.py`), JavaScript/TypeScript (`.js`, `.ts`, `.tsx`, `.jsx`), Web (`.html`, `.css`, `.scss`, `.vue`), Systems (`.c`, `.cpp`, `.cs`, `.go`, `.rs`, `.java`), Config & Data (`.json`, `.yaml`, `.toml`, `.sql`, `Dockerfile`, `.md`), and more.
  - **Strictly Ignored**: Images (`.png`, `.jpg`, `.svg`, `.ico`), Audio/Video (`.mp3`, `.mp4`), Binaries/Executables (`.exe`, `.dll`, `.zip`, `.pdf`), Lockfiles (`package-lock.json`), and dependency directories (`node_modules`, `.git`, `venv`, `dist`, `__pycache__`).
- **Human Reading Simulation**:
  - **Mouse Effect Felt**: Moves the cursor into the editor pane using smooth cubic Bézier curves with natural acceleration/deceleration and subtle reading gaze drift.
  - **Slight Scroll Down Every ~3 Seconds**: Gentle, micro-stepped wheel events every 2.7 to 3.3 seconds.
  - **Zero Edits / Changes**: Does not press keys or send keystrokes; your source files remain 100% untouched.
  - **Paced by File Length**: Automatically calculates reading duration based on file line count, with a safe ceiling for very large files.
- **Zero External Dependencies**: Powered by Python's built-in standard library and native Windows `ctypes` (`user32.dll`). No `pip install` required.

---

## 🚀 How to Run

### Option 1: In VS Code or Antigravity IDE
1. Open this folder (`log-mot`) in VS Code or Antigravity IDE.
2. Open `bot.py`.
3. Press **`F5`** (or click the **Play / Run Python File** button in the top-right corner).
4. Enter or paste the path of the folder you want to read (or use the graphical folder picker popup).

### Option 2: From the Terminal
In PowerShell or Command Prompt:

```powershell
# Interactive mode (prompts you for the path or opens folder picker)
python bot.py

# Direct path mode (specify the folder path directly)
python bot.py "C:\Users\USER\Desktop\my-project"
```

---

## ⚙️ Configuration (`config.py`)

You can tweak any behavioral setting in [`config.py`](file:///c:/Users/USER/Desktop/peeples%20sites/log-mot/config.py):

| Setting | Default | Description |
| :--- | :--- | :--- |
| `SCROLL_INTERVAL_MIN` / `MAX` | `2.7` – `3.3`s | Time between scroll actions (~3 seconds) |
| `SCROLL_DELTA_MIN` / `MAX` | `-120` – `-80` | Mouse wheel scroll notch intensity |
| `SCROLL_MICRO_STEPS` | `2` | Subdivides wheel clicks for silky-smooth motion |
| `MOUSE_DRIFT_CHANCE` | `0.45` | Probability of subtle cursor adjustment while reading |
| `FILE_LOAD_WAIT` | `2.0`s | Pause after opening a file before scrolling starts |
| `MAX_SECONDS_PER_FILE` | `45.0`s | Max time to spend on huge files |
| `PAUSE_BETWEEN_FILES` | `1.8`s | Natural breathing pause between files |

---

## 🛑 Stopping the Bot
Press **`Ctrl + C`** in the terminal running `bot.py` at any time to cleanly stop the reader.
