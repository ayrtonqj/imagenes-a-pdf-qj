import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

import customtkinter as ctk
from app import ImageToPDFApp
from config_app import APP_NAME, APP_VERSION


def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).parent / relative_path


def main():
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title(f"{APP_NAME} v{APP_VERSION}")
    root.geometry("1180x740")
    root.minsize(900, 580)

    # Set Window Icon
    icon_ico = get_resource_path("img/logo.ico")
    icon_png = get_resource_path("img/logo.png")

    if icon_ico.exists():
        try:
            root.iconbitmap(str(icon_ico))
            root.after(200, lambda: root.iconbitmap(str(icon_ico)))
        except Exception:
            pass

    if icon_png.exists():
        try:
            from PIL import Image, ImageTk
            img_obj = Image.open(icon_png)
            photo = ImageTk.PhotoImage(img_obj)
            root.wm_iconphoto(True, photo)
        except Exception:
            pass

    app = ImageToPDFApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
