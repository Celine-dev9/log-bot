"""
Manages VS Code processes: launching a new instance for the target folder
and opening specific code files at line 1.
"""

import os
import shutil
import subprocess
import time
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

    def launch_new_instance(self) -> None:
        """
        Launches a new, independent VS Code window with the target folder opened.
        Minimizes the bot terminal and gives the screen to the new VS Code window.
        """
        print(f"\n[VSCode] Launching new VS Code instance for folder:")
        print(f"         {self.target_folder}")

        # Minimize the bot workspace/terminal window
        human_mouse.minimize_bot_window()

        # 'code -n <folder>' launches the target project in a brand-new window
        cmd = f'"{self.code_bin}" -n "{self.target_folder}"'
        try:
            subprocess.Popen(cmd, shell=True)
        except Exception:
            pass

        print("[VSCode] Waiting 4 seconds for window to initialize...")
        time.sleep(4.0)

    def open_file(self, file_path: str) -> None:
        """
        Opens a specific code file in the target VS Code instance at line 1.
        Uses '-r <target_folder>' so it strictly opens in the target window,
        never in the bot's workspace.
        """
        abs_file = os.path.abspath(file_path)
        cmd = f'"{self.code_bin}" -r "{self.target_folder}" -g "{abs_file}:1"'
        try:
            subprocess.run(cmd, shell=True, check=False)
        except Exception:
            pass
