"""
Human-like mouse movement, wheel scrolling, and window management for Windows.
Utilizes native Windows ctypes API with zero external dependencies required.
"""

import time
import math
import random
import ctypes
from typing import Tuple

# Windows API constants
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_WHEEL = 0x0800
SW_MINIMIZE = 6
SW_RESTORE = 9

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


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
    Negative delta scrolls down (-120 is one standard notch).
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

    dx = target_x - start_x
    dy = target_y - start_y
    dist = math.hypot(dx, dy)

    deviation = min(max(dist * 0.2, 10), 60)
    dev_sign = random.choice([-1, 1])

    ctrl1_x = start_x + dx * 0.25 + (-dy / (dist + 1e-5)) * deviation * dev_sign * random.uniform(0.6, 1.2)
    ctrl1_y = start_y + dy * 0.25 + (dx / (dist + 1e-5)) * deviation * dev_sign * random.uniform(0.6, 1.2)

    ctrl2_x = start_x + dx * 0.75 + (-dy / (dist + 1e-5)) * (deviation * 0.5) * dev_sign
    ctrl2_y = start_y + dy * 0.75 + (dx / (dist + 1e-5)) * (deviation * 0.5) * dev_sign

    delay = duration / max(steps, 1)

    for i in range(1, steps + 1):
        t_raw = i / steps
        t = 3 * (t_raw ** 2) - 2 * (t_raw ** 3)

        curr_x = cubic_bezier(start_x, ctrl1_x, ctrl2_x, target_x, t)
        curr_y = cubic_bezier(start_y, ctrl1_y, ctrl2_y, target_y, t)

        if i < steps:
            curr_x += random.uniform(-1.0, 1.0)
            curr_y += random.uniform(-1.0, 1.0)

        set_cursor_pos(int(curr_x), int(curr_y))
        time.sleep(delay)

    set_cursor_pos(target_x, target_y)


def smooth_scroll_down(
    delta: int = -120,
    micro_steps: int = 3,
    micro_delay: float = 0.04,
) -> None:
    """Performs a gentle, smooth scroll downward subdivided into micro-ticks."""
    sub_delta = int(delta / max(micro_steps, 1))
    for _ in range(micro_steps):
        mouse_wheel(sub_delta)
        time.sleep(micro_delay)


def get_editor_center_point() -> Tuple[int, int]:
    """
    Returns (x, y) comfortably located in the center of the code editor area.
    In VS Code, the editor pane is centered slightly to the right of the sidebar.
    """
    screen_w = user32.GetSystemMetrics(0)  # Primary screen width
    screen_h = user32.GetSystemMetrics(1)  # Primary screen height

    center_x = int(screen_w * 0.55) + random.randint(-40, 40)
    center_y = int(screen_h * 0.50) + random.randint(-30, 30)
    return center_x, center_y


def minimize_bot_window() -> None:
    """Minimizes the current terminal/console or IDE window running the bot."""
    try:
        con_hwnd = kernel32.GetConsoleWindow()
        if con_hwnd and user32.IsWindow(con_hwnd):
            user32.ShowWindow(con_hwnd, SW_MINIMIZE)

        fore_hwnd = user32.GetForegroundWindow()
        if fore_hwnd and user32.IsWindow(fore_hwnd):
            user32.ShowWindow(fore_hwnd, SW_MINIMIZE)
    except Exception:
        pass
