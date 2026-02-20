# -*- coding: utf-8 -*-

import ctypes
import threading
import time

# Carrega X11 e Xtst
libX11 = ctypes.cdll.LoadLibrary("libX11.so.6")
libXtst = ctypes.cdll.LoadLibrary("libXtst.so.6")

Display_p = ctypes.c_void_p

# XOpenDisplay
libX11.XOpenDisplay.argtypes = [ctypes.c_char_p]
libX11.XOpenDisplay.restype = Display_p

# XStringToKeysym / XKeysymToKeycode
libX11.XStringToKeysym.argtypes = [ctypes.c_char_p]
libX11.XStringToKeysym.restype = ctypes.c_ulong

libX11.XKeysymToKeycode.argtypes = [Display_p, ctypes.c_ulong]
libX11.XKeysymToKeycode.restype = ctypes.c_ubyte

# XQueryKeymap: preenche 32 bytes com estado de todas as teclas
KeymapArray = ctypes.c_ubyte * 32
libX11.XQueryKeymap.argtypes = [Display_p, KeymapArray]
libX11.XQueryKeymap.restype = ctypes.c_int

# XTestFakeButtonEvent (clique)
libXtst.XTestFakeButtonEvent.argtypes = [
    Display_p,
    ctypes.c_uint,   # botão
    ctypes.c_int,    # press (1) / release (0)
    ctypes.c_ulong,  # delay
]

# XFlush
libX11.XFlush.argtypes = [Display_p]


def get_keycode(display, key_name: str) -> int:
    """Converte nome da tecla (keysym) em keycode."""
    keysym = libX11.XStringToKeysym(key_name.encode("ascii"))
    if keysym == 0:
        raise RuntimeError("Keysym not found for key: " + key_name)
    keycode = libX11.XKeysymToKeycode(display, keysym)
    return int(keycode)


def is_key_pressed(display, keycode: int) -> bool:
    """
    Verifica se a tecla está pressionada usando XQueryKeymap.

    No X11, cada bit (0–255) representa um keycode.
    keycode -> byte_index = keycode // 8
               bit_index  = keycode % 8
    """
    keymap = KeymapArray()
    libX11.XQueryKeymap(display, keymap)

    if keycode < 0 or keycode > 255:
        return False

    byte_index = keycode // 8
    bit_index = keycode % 8

    byte_val = keymap[byte_index]
    return (byte_val & (1 << bit_index)) != 0


def click_loop(display, active_flag, running_flag, interval=0.1):
    """Thread que fica clicando enquanto active_flag[0] for True."""
    while running_flag[0]:
        if active_flag[0]:
            # Botao 1 = clique esquerdo
            libXtst.XTestFakeButtonEvent(display, 1, 1, 0)  # press
            libXtst.XTestFakeButtonEvent(display, 1, 0, 0)  # release
            libX11.XFlush(display)
            time.sleep(interval)
        else:
            time.sleep(0.01)


def main():
    display = libX11.XOpenDisplay(None)
    if not display:
        print("Error: could not open X display. Are you on X11?")
        return

    # Hotkeys:
    #   F9  -> toggle liga/desliga
    #   F10 -> sair
    keycode_toggle = get_keycode(display, "F9")
    keycode_exit = get_keycode(display, "F10")

    print("Keycodes:")
    print("  F9  =", keycode_toggle)
    print("  F10 =", keycode_exit)

    active_flag = [False]
    running_flag = [True]

    # Thread de clique
    t = threading.Thread(
        target=click_loop,
        args=(display, active_flag, running_flag),
        daemon=True,
    )
    t.start()

    print("=== Autoclicker Linux (X11) com hotkeys ===")
    print("F9  -> Liga/Desliga")
    print("F10 -> Sair")
    print("Se não parar: abra outro terminal e rode 'pkill python3'.")
    print("---------------------------------------------")

    prev_toggle = False
    prev_exit = False

    try:
        while running_flag[0]:
            cur_toggle = is_key_pressed(display, keycode_toggle)
            cur_exit = is_key_pressed(display, keycode_exit)

            # F9 apertado => toggle
            if cur_toggle and not prev_toggle:
                active_flag[0] = not active_flag[0]
                print("Estado:", "ON (clicando)" if active_flag[0] else "OFF (parado)")

            # F10 apertado => sair
            if cur_exit and not prev_exit:
                print("Encerrando (F10)...")
                running_flag[0] = False
                active_flag[0] = False
                break

            prev_toggle = cur_toggle
            prev_exit = cur_exit

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nExiting by Ctrl+C...")
        running_flag[0] = False
        active_flag[0] = False

    t.join(timeout=0.2)


if __name__ == "__main__":
    main()