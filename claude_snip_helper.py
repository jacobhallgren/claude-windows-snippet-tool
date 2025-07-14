#!/usr/bin/env python3
# coding: utf-8
"""
Clipboard-to-file helper for Windows + VS Code

– After a Win+Shift+S snip (CF_DIB on clipboard), a *left-click*
  anywhere saves the image if the window under the mouse OR the
  foreground window belongs to a VS Code process.
– Saves images to "…Pictures\Screenshots" with timestamp format
  "screenshot_YYYYMMDD_HHMMSS.png" and copies the path to clipboard.
– Ignores synthetic clicks that occur ≤ 200 ms after the snip.
– Monitors clipboard changes every 50 ms for new image data.
– Single instance protection: only one copy can run at a time.
– Clean exit with Ctrl-C.

Needs: pywin32, pillow, mouse, pyperclip, psutil
"""

import io, sys, time, threading, socket, random
from pathlib import Path
from datetime import datetime

import win32gui, win32process, win32clipboard, win32con
import mouse, pyperclip, psutil
from mouse import ButtonEvent
from PIL import Image

# ── CONFIG ─────────────────────────────────────────────────────────
CLICK_SUPPRESS_MS = 200
SAVE_DIR = Path.home() / "Pictures" / "Screenshots"
SAVE_DIR.mkdir(parents=True, exist_ok=True)
VS_CODE_EXE = {"code.exe", "code - insiders.exe", "vscode.exe"}
# ───────────────────────────────────────────────────────────────────

last_snip_ts    = 0.0
last_snip_seq   = 0
last_snip_bytes = b""
lock_socket     = None


# ── instance lock ──────────────────────────────────────────────────
def _acquire_lock() -> bool:
    global lock_socket
    
    # Use a fixed port that all instances will try to bind to
    LOCK_PORT = 19847  # Fixed port for this script
    
    try:
        lock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lock_socket.bind(('127.0.0.1', LOCK_PORT))
        lock_socket.listen(1)
        return True
    except OSError:
        # Port already in use - another instance is running
        if lock_socket:
            lock_socket.close()
        return False


def _release_lock():
    global lock_socket
    if lock_socket:
        lock_socket.close()
        lock_socket = None
# ───────────────────────────────────────────────────────────────────


# ── clipboard helpers ──────────────────────────────────────────────
def _seq() -> int:
    return win32clipboard.GetClipboardSequenceNumber()


def _dib_available() -> bool:
    return win32clipboard.IsClipboardFormatAvailable(win32con.CF_DIB)


def _read_dib() -> bytes | None:
    try:
        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData(win32con.CF_DIB)
        win32clipboard.CloseClipboard()
        return data
    except Exception:
        return None


def _save_image(dib: bytes) -> Path:
    img = Image.open(io.BytesIO(dib))
    fname = SAVE_DIR / f"screenshot_{datetime.now():%Y%m%d_%H%M%S}.png"
    img.save(fname, "PNG")
    return fname
# ───────────────────────────────────────────────────────────────────


# ── VS Code detection ──────────────────────────────────────────────
def _pid_is_vscode(pid: int) -> bool:
    try:
        return psutil.Process(pid).name().lower() in VS_CODE_EXE
    except psutil.Error:
        return False


def _foreground_is_vscode() -> bool:
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd:
        return False
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    return _pid_is_vscode(pid)


def _window_at_point_is_vscode(x: int, y: int) -> bool:
    hwnd = win32gui.WindowFromPoint((x, y))
    if not hwnd:
        return False
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    return _pid_is_vscode(pid)
# ───────────────────────────────────────────────────────────────────


# ── clipboard watcher ──────────────────────────────────────────────
def _clip_monitor():
    global last_snip_ts, last_snip_seq, last_snip_bytes
    seq_prev = _seq()

    while True:
        seq_now = _seq()
        if seq_now != seq_prev:
            seq_prev = seq_now
            if _dib_available():
                dib = _read_dib()
                if dib:
                    last_snip_bytes = dib
                    last_snip_seq   = seq_now
                    last_snip_ts    = time.time()
        time.sleep(0.05)           # poll 50 ms
# ───────────────────────────────────────────────────────────────────


# ── mouse hook ─────────────────────────────────────────────────────
def _click_handler(event):
    if not isinstance(event, ButtonEvent):
        return
    if event.event_type != "down" or event.button != mouse.LEFT:
        return

    # current pointer position (ButtonEvent has no x/y on Windows)
    x, y = mouse.get_position()

    # accept click if foreground OR window under pointer is VS Code
    if not (_foreground_is_vscode() or _window_at_point_is_vscode(x, y)):
        return

    # filter the synthetic click right after snip
    if (time.time() - last_snip_ts) * 1000 <= CLICK_SUPPRESS_MS:
        return

    # ensure we act only on the latest snip still present
    if _seq() != last_snip_seq or not _dib_available():
        return

    path = _save_image(last_snip_bytes)
    pyperclip.copy(str(path))
    print(f"✓ Saved → {path}  (path copied)")


# ── entry point ────────────────────────────────────────────────────
def main():
    if sys.platform != "win32":
        print("Windows only.")
        sys.exit(1)

    # Check for existing instance
    if not _acquire_lock():
        print("🚫 Another instance is already running. Shutting down.")
        sys.exit(1)

    print("🟢 VS-Code snip helper running – Ctrl-C to quit")
    threading.Thread(target=_clip_monitor, daemon=True).start()
    mouse.hook(_click_handler)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping…")
        mouse.unhook(_click_handler)
    finally:
        _release_lock()


if __name__ == "__main__":
    main()
