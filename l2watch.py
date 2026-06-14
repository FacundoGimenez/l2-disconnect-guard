import time
import os
import sys
import threading
import tkinter as tk
import pystray
import cv2
import numpy as np
import mss
from PIL import Image, ImageDraw
from datetime import datetime


def resource_path(relative_path):
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
        return os.path.join(base_path, relative_path)

    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


IMAGE_PATH = resource_path("disconnect.png")
CONFIDENCE = 0.50

running = True
tray_icon = None


def disconnect_found():
    template = cv2.imread(IMAGE_PATH, cv2.IMREAD_GRAYSCALE)
    if template is None:
        return False

    with mss.mss() as sct:
        monitor = sct.monitors[0]  # todos los monitores juntos
        screenshot = np.array(sct.grab(monitor))

    gray = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2GRAY)
    result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)

    _, max_val, _, _ = cv2.minMaxLoc(result)
    return max_val >= CONFIDENCE


def create_icon_image(color="green"):
    img = Image.new("RGB", (64, 64), "black")
    draw = ImageDraw.Draw(img)
    draw.ellipse((12, 12, 52, 52), fill=color)
    return img


def update_status(text, color="green"):
    status_label.config(text=text)
    status_dot.delete("all")
    status_dot.create_oval(2, 2, 14, 14, fill=color, outline=color)

    if tray_icon:
        tray_icon.icon = create_icon_image(color)


def update_last_check():
    last_check_label.config(text=datetime.now().strftime("%H:%M:%S"))


def show_window(icon=None, item=None):
    root.after(0, root.deiconify)
    root.after(0, root.lift)


def hide_window():
    root.withdraw()


def exit_app(icon=None, item=None):
    global running, tray_icon
    running = False

    if tray_icon:
        tray_icon.stop()

    root.after(0, root.destroy)


def watch_disconnect():
    global running

    while running:
        found = disconnect_found()
        root.after(0, update_last_check)

        if found:
            root.after(
                0,
                update_status,
                "Disconnect detectado, confirmando...",
                "orange"
            )

            time.sleep(15)

            if disconnect_found():
                root.after(
                    0,
                    update_status,
                    "Apagado programado en 60 segundos",
                    "red"
                )
                os.system("shutdown /s /t 60")
                running = False
                break
            else:
                root.after(
                    0,
                    update_status,
                    "Monitoreando disconnects",
                    "green"
                )

        time.sleep(3)


def setup_tray():
    global tray_icon

    menu = pystray.Menu(
        pystray.MenuItem("Mostrar", show_window, default=True),
        pystray.MenuItem("Salir", exit_app)
    )

    tray_icon = pystray.Icon(
        "Disconnect Guard",
        create_icon_image("green"),
        "Disconnect Guard - Monitoreando",
        menu
    )

    tray_icon.run()


root = tk.Tk()
root.title("Disconnect Guard")
root.geometry("360x300")
root.resizable(False, False)

title = tk.Label(root, text="Disconnect Guard", font=("Segoe UI", 16, "bold"))
title.pack(pady=(15, 10))

separator = tk.Frame(root, height=1, bg="#cccccc")
separator.pack(fill="x", padx=20, pady=5)

tk.Label(root, text="Estado:", font=("Segoe UI", 10)).pack(anchor="w", padx=35)

status_frame = tk.Frame(root)
status_frame.pack(anchor="w", padx=35, pady=(5, 18))

status_dot = tk.Canvas(status_frame, width=18, height=18, highlightthickness=0)
status_dot.create_oval(2, 2, 14, 14, fill="green", outline="green")
status_dot.pack(side="left", padx=(0, 8))

status_label = tk.Label(
    status_frame,
    text="Monitoreando disconnects",
    font=("Segoe UI", 11),
    justify="left"
)
status_label.pack(side="left")

tk.Label(root, text="Última verificación:", font=("Segoe UI", 10)).pack(anchor="w", padx=35)

last_check_label = tk.Label(
    root,
    text="--:--:--",
    font=("Segoe UI", 11, "bold")
)
last_check_label.pack(anchor="w", padx=35, pady=(0, 18))

reminder_label = tk.Label(
    root,
    text="Recordá dejar el cliente de Lineage sin minimizar",
    font=("Segoe UI", 8),
    fg="#666666",
    wraplength=280,
    justify="center"
)
reminder_label.pack(pady=(0, 16))

buttons = tk.Frame(root)
buttons.pack()

tk.Button(buttons, text="Ocultar", width=10, command=hide_window).pack(side="left", padx=5)
tk.Button(buttons, text="Salir", width=10, command=exit_app).pack(side="left", padx=5)

root.protocol("WM_DELETE_WINDOW", hide_window)

threading.Thread(target=watch_disconnect, daemon=True).start()
threading.Thread(target=setup_tray, daemon=True).start()

root.mainloop()