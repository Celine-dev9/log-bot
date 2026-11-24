"""
Human-like mouse movement, wheel scrolling, and window management for Windows.
Utilizes native Windows ctypes API with zero external dependencies required.
"""

import sys
import time
import math
import random
import ctypes
from ctypes import wintypes
from typing import Optional, Tuple

# Windows API constants
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_WHEEL = 0x0800
SW_RESTORE = 9

# Load user32
user32 = ctypes.windll.user32


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]


def get_cursor_pos() -> Tuple[int, int]:
    """Get current mouse cursor position (x, y)."""
    pt = POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y


def set_cursor_pos(x: int, y: int) -> None:
    """Set mouse cursor position directly."""
    user32.SetCursorPos(int(x), int(y))


def mouse_wheel(delta: int) -> None:
    """
    Send mouse wheel event.
    Negative delta scrolls down (-120 is one notch).
    Positive delta scrolls up (+120 is one notch).
    """
    user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, delta, 0)


def cubic_bezier(p0: float, p1: float, p2: float, p3: float, t: float) -> float:
    """Standard cubic Bezier interpolation point."""
    return (
        (1 - t) ** 3 * p0
        + 3 * (1 - t) ** 2 * t * p1
        + 3 * (1 - t) * t ** 2 * p2
        + t ** 3 * p3
    )


def move_mouse_human(
    target_x: int,
    target_y: int,
    duration: float = 0.45,
    steps: int = 25,
) -> None:
    """
    Moves mouse from current position to (target_x, target_y) using a smooth
    cubic Bezier curve with natural human acceleration, deceleration, and micro-jitter.
    """
    start_x, start_y = get_cursor_pos()
    if start_x == target_x and start_y == target_y:
        return

    # Random control points to produce a subtle natural curve rather than a robotic straight line
    dx = target_x - start_x
    dy = target_y - start_y
    dist = math.hypot(dx, dy)

    # Lateral deviation
    deviation = min(max(dist * 0.2, 10), 60)
    dev_sign = random.choice([-1, 1])

    ctrl1_x = start_x + dx * 0.25 + (-dy / (dist + 1e-5)) * deviation * dev_sign * random.uniform(0.6, 1.2)
    ctrl1_y = start_y + dy * 0.25 + (dx / (dist + 1e-5)) * deviation * dev_sign * random.uniform(0.6, 1.2)

    ctrl2_x = start_x + dx * 0.75 + (-dy / (dist + 1e-5)) * (deviation * 0.5) * dev_sign
    ctrl2_y = start_y + dy * 0.75 + (dx / (dist + 1e-5)) * (deviation * 0.5) * dev_sign

    delay = duration / max(steps, 1)

    for i in range(1, steps + 1):
        t_raw = i / steps
        # Human ease-in-out timing function: 3*t^2 - 2*t^3
        t = 3 * (t_raw ** 2) - 2 * (t_raw ** 3)

        curr_x = cubic_bezier(start_x, ctrl1_x, ctrl2_x, target_x, t)
        curr_y = cubic_bezier(start_y, ctrl1_y, ctrl2_y, target_y, t)

        # Micro-jitter on intermediate steps
        if i < steps:
            curr_x += random.uniform(-1.0, 1.0)
            curr_y += random.uniform(-1.0, 1.0)

        set_cursor_pos(int(curr_x), int(curr_y))
        time.sleep(delay)

    # Ensure cursor lands precisely at target
    set_cursor_pos(target_x, target_y)


def smooth_scroll_down(
    delta: int = -120,
    micro_steps: int = 2,
    micro_delay: float = 0.04,
) -> None:
    """
    Performs a gentle, smooth scroll downward subdivided into micro-ticks.
    Feels like a physical mouse wheel click or trackpad finger glide.
    """
    sub_delta = int(delta / max(micro_steps, 1))
    for _ in range(micro_steps):
        mouse_wheel(sub_delta)
        time.sleep(micro_delay)


def find_vscode_window(keyword: Optional[str] = None) -> Optional[int]:
    """
    Finds the HWND (window handle) of the target VS Code window.
    Searches for windows containing 'Visual Studio Code' and optionally the folder/workspace keyword.
    """
    found_hwnds = []

    def enum_windows_callback(hwnd, extra):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buffer = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buffer, length + 1)
                title = buffer.value
                if "Visual Studio Code" in title:
                    found_hwnds.append((hwnd, title))
        return True

    ENUM_WINDOWS_PROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    user32.EnumWindows(ENUM_WINDOWS_PROC(enum_windows_callback), 0)

    if not found_hwnds:
        return None

    # If keyword specified, look for matching title first
    if keyword:
        keyword_lower = keyword.lower()
        for hwnd, title in found_hwnds:
            if keyword_lower in title.lower():
                return hwnd

    # Default to the most recently active or first VS Code window
    return found_hwnds[0][0]


def focus_window(hwnd: int) -> bool:
    """Brings window to foreground and restores if minimized."""
    if not hwnd or not user32.IsWindow(hwnd):
        return False
    user32.ShowWindow(hwnd, SW_RESTORE)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.3)
    return True


def get_window_editor_area(hwnd: int) -> Tuple[int, int, int, int]:
    """
    Returns (left, top, right, bottom) of the estimated text editor area
    inside the VS Code window, avoiding the activity bar, sidebar, and tab bars.
    """
    rect = RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))

    width = rect.right - rect.left
    height = rect.bottom - rect.top

    # Code editor is typically located:
    # X: ~35% to 75% across the window (skipping sidebar)
    # Y: ~30% to 70% down the window (skipping tabs & status bar)
    editor_left = int(rect.left + width * 0.35)
    editor_top = int(rect.top + height * 0.25)
    editor_right = int(rect.left + width * 0.75)
    editor_bottom = int(rect.top + height * 0.75)

    return editor_left, editor_top, editor_right, editor_bottom


def get_random_editor_point(hwnd: int) -> Tuple[int, int]:
    """Gets a random point comfortably located inside the code editor pane."""
    left, top, right, bottom = get_window_editor_area(hwnd)
    x = random.randint(min(left, right), max(left, right))
    y = random.randint(min(top, bottom), max(top, bottom))
    return x, y
