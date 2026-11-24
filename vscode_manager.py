"""
Manages VS Code processes: launching a new instance, opening workspaces,
and opening specific code files at line 1.
"""

import os
import shutil
import subprocess
import time
from typing import Optional
import human_mouse


def find_vscode_binary() -> str:
    """Finds the VS Code executable or command runner on Windows."""
    # 1. Check system PATH
    code_path = shutil.which("code")
    if code_path:
        return code_path

    # 2. Check standard Windows AppData user installation
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    candidates = [
        os.path.join(local_app_data, "Programs", "Microsoft VS Code", "bin", "code.cmd"),
        os.path.join(local_app_data, "Programs", "Microsoft VS Code", "Code.exe"),
        r"C:\Program Files\Microsoft VS Code\bin\code.cmd",
        r"C:\Program Files\Microsoft VS Code\Code.exe",
        r"C:\Program Files (x86)\Microsoft VS Code\bin\code.cmd",
    ]

    for path in candidates:
        if os.path.exists(path):
            return path

    raise FileNotFoundError(
        "VS Code executable ('code' or 'code.cmd') was not found in PATH or standard installation directories.\n"
        "Please ensure Visual Studio Code is installed."
    )


class VSCodeController:
    def __init__(self, target_folder: str):
        self.target_folder = os.path.abspath(target_folder)
        self.folder_name = os.path.basename(self.target_folder)
        self.code_bin = find_vscode_binary()
        self.hwnd: Optional[int] = None

    def launch_new_instance(self) -> None:
        """
        Launches a new, independent VS Code window with the target folder opened.
        """
        print(f"\n[VSCode] Launching new VS Code instance for folder:")
        print(f"         {self.target_folder}")

        # 'code -n <folder>' launches in a brand-new window
        cmd = [self.code_bin, "-n", self.target_folder]
        subprocess.Popen(cmd, shell=True)

        # Allow VS Code time to open and render workspace
        print("[VSCode] Waiting for window to initialize...")
        for _ in range(10):
            time.sleep(1.0)
            self.hwnd = human_mouse.find_vscode_window(keyword=self.folder_name)
            if self.hwnd:
                break

        if not self.hwnd:
            # Fallback to any VS Code window
            self.hwnd = human_mouse.find_vscode_window()

        if self.hwnd:
            human_mouse.focus_window(self.hwnd)
            print(f"[VSCode] Connected to window (HWND: {self.hwnd}).")
        else:
            print("[VSCode] Notice: Window handle could not be hooked directly; will rely on active window.")

    def open_file(self, file_path: str) -> None:
        """
        Opens a specific code file in the current VS Code instance at line 1.
        """
        abs_file = os.path.abspath(file_path)
        # 'code -r -g file:1' reuses current window and places cursor at line 1
        cmd = [self.code_bin, "-r", "-g", f"{abs_file}:1"]
        subprocess.run(cmd, shell=True, check=False)

        # Ensure VS Code window stays in focus
        if self.hwnd:
            human_mouse.focus_window(self.hwnd)
