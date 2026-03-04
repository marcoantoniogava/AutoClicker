import ctypes
import threading
import time
from ctypes import wintypes


# WinAPI constants
WM_HOTKEY = 0x0312
VK_F8 = 0x77
VK_F9 = 0x78
VK_F10 = 0x79

HOTKEY_START = 1
HOTKEY_PAUSE = 2
HOTKEY_STOP = 3

MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
SM_CXSCREEN = 0
SM_CYSCREEN = 1


user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


class _INPUTUNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT)]


class INPUT(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("union", _INPUTUNION)]


class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("message", wintypes.UINT),
        ("wParam", wintypes.WPARAM),
        ("lParam", wintypes.LPARAM),
        ("time", wintypes.DWORD),
        ("pt", POINT),
    ]


def send_left_click() -> None:
    inputs = (INPUT * 2)()
    inputs[0].type = 0  # INPUT_MOUSE
    inputs[0].union.mi = MOUSEINPUT(0, 0, 0, MOUSEEVENTF_LEFTDOWN, 0, None)

    inputs[1].type = 0
    inputs[1].union.mi = MOUSEINPUT(0, 0, 0, MOUSEEVENTF_LEFTUP, 0, None)

    user32.SendInput(2, ctypes.byref(inputs), ctypes.sizeof(INPUT))


def get_cursor_position() -> tuple[int, int]:
    point = POINT()
    user32.GetCursorPos(ctypes.byref(point))
    return point.x, point.y


def inside_screen(x: int, y: int) -> bool:
    width = user32.GetSystemMetrics(SM_CXSCREEN)
    height = user32.GetSystemMetrics(SM_CYSCREEN)
    return 0 <= x < width and 0 <= y < height


def click_loop(state: dict) -> None:
    while not state["stop"]:
        if state["running"] and not state["paused"]:
            x, y = get_cursor_position()
            if inside_screen(x, y):
                send_left_click()
            time.sleep(state["interval"])
        else:
            time.sleep(0.02)


def register_hotkeys() -> None:
    if not user32.RegisterHotKey(None, HOTKEY_START, 0, VK_F8):
        raise RuntimeError("Falha ao registrar F8.")
    if not user32.RegisterHotKey(None, HOTKEY_PAUSE, 0, VK_F9):
        user32.UnregisterHotKey(None, HOTKEY_START)
        raise RuntimeError("Falha ao registrar F9.")
    if not user32.RegisterHotKey(None, HOTKEY_STOP, 0, VK_F10):
        user32.UnregisterHotKey(None, HOTKEY_START)
        user32.UnregisterHotKey(None, HOTKEY_PAUSE)
        raise RuntimeError("Falha ao registrar F10.")


def unregister_hotkeys() -> None:
    user32.UnregisterHotKey(None, HOTKEY_START)
    user32.UnregisterHotKey(None, HOTKEY_PAUSE)
    user32.UnregisterHotKey(None, HOTKEY_STOP)


def main() -> None:
    state = {
        "running": False,
        "paused": False,
        "stop": False,
        "interval": 0.03,  # ~33 cliques/segundo
    }

    print("Auto clicker (Python puro / Windows)")
    print("F8  -> liga")
    print("F9  -> pausa/retoma (toggle)")
    print("F10 -> desliga totalmente")
    print("Deixe este terminal aberto enquanto o script estiver rodando.")

    register_hotkeys()

    worker = threading.Thread(target=click_loop, args=(state,), daemon=True)
    worker.start()

    msg = MSG()
    try:
        while not state["stop"]:
            result = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
            if result == -1:
                break
            if msg.message == WM_HOTKEY:
                hotkey_id = msg.wParam
                if hotkey_id == HOTKEY_START:
                    state["running"] = True
                    state["paused"] = False
                    print("Ligado (F8).")
                elif hotkey_id == HOTKEY_PAUSE:
                    if state["running"]:
                        state["paused"] = not state["paused"]
                        if state["paused"]:
                            print("Pausado (F9).")
                        else:
                            print("Retomado (F9).")
                elif hotkey_id == HOTKEY_STOP:
                    state["stop"] = True
                    print("Encerrando (F10).")
                    break
    finally:
        unregister_hotkeys()
        state["stop"] = True
        worker.join(timeout=1)


if __name__ == "__main__":
    main()
