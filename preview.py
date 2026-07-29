import os
import tkinter as tk
import customtkinter as ctk
from pathlib import Path
from PIL import Image, ImageTk, ImageDraw


class PreviewPanel(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.current_path = None
        self._photo = None
        self.page_size = "A4"
        self.orientation = "Portrait"

        self.preview_container = ctk.CTkFrame(self, fg_color="#18181b", corner_radius=8)
        self.preview_container.pack(fill="both", expand=True, padx=5, pady=5)

        self.preview_label = tk.Label(
            self.preview_container, bg="#18181b", fg="#888888",
            text="Ninguna imagen seleccionada", anchor="center", justify="center",
            font=("Segoe UI", 11)
        )
        self.preview_label.pack(fill="both", expand=True, padx=10, pady=10)

        self.info_var = tk.StringVar(value="Ninguna imagen seleccionada")
        self.info_label = ctk.CTkLabel(
            self, textvariable=self.info_var,
            anchor="w", justify="left",
            text_color="#a1a1aa", font=ctk.CTkFont(size=12)
        )
        self.info_label.pack(fill="x", padx=10, pady=(2, 6))

        self.bind("<Configure>", lambda e: self._update_preview())

    def show_image(self, path):
        self.current_path = path
        self._update_preview()

    def set_config(self, page_size, orientation):
        self.page_size = page_size
        self.orientation = orientation
        self._update_preview()

    def _update_preview(self):
        if not self.current_path:
            return

        try:
            img = Image.open(self.current_path)
            self.update_idletasks()
            max_w = self.preview_container.winfo_width() - 20 or 400
            max_h = self.preview_container.winfo_height() - 20 or 300

            if max_w < 50: max_w = 400
            if max_h < 50: max_h = 300

            if self.page_size != "Original":
                sizes_pt = {
                    'A4': (595.28, 841.89),
                    'Letter': (612, 792),
                    'Legal': (612, 1008),
                }
                pw, ph = sizes_pt.get(self.page_size, (595.28, 841.89))
                if self.orientation == 'Landscape':
                    pw, ph = ph, pw

                page_ratio = pw / ph
                if max_w / max_h > page_ratio:
                    disp_h = max_h - 10
                    disp_w = int(disp_h * page_ratio)
                else:
                    disp_w = max_w - 10
                    disp_h = int(disp_w / page_ratio)
                
                disp_w = max(1, disp_w)
                disp_h = max(1, disp_h)

                page_img = Image.new("RGB", (disp_w, disp_h), "white")
                img_ratio = img.width / img.height

                if img_ratio > page_ratio:
                    new_w = disp_w
                    new_h = int(disp_w / img_ratio)
                else:
                    new_h = disp_h
                    new_w = int(disp_h * img_ratio)
                
                new_w = max(1, new_w)
                new_h = max(1, new_h)

                img_resized = img.resize((new_w, new_h), Image.LANCZOS)
                x = (disp_w - new_w) // 2
                y = (disp_h - new_h) // 2
                page_img.paste(img_resized, (x, y))

                try:
                    draw = ImageDraw.Draw(page_img)
                    draw.rectangle([0, 0, disp_w-1, disp_h-1], outline="#555555")
                except Exception:
                    pass

                final_img = page_img
            else:
                img.thumbnail((max_w, max_h), Image.LANCZOS)
                final_img = img

            self._photo = ImageTk.PhotoImage(final_img)
            self.preview_label.config(image=self._photo, text="")

            file_size = os.path.getsize(self.current_path)
            info = (
                f"Archivo: {Path(self.current_path).name}  |  "
                f"Dimensiones: {img.width}x{img.height} px  |  "
                f"Formato: {img.format}  |  "
                f"Peso: {file_size / 1024:.1f} KB"
            )
            self.info_var.set(info)
        except Exception as e:
            self.preview_label.config(image="", text=f"Error: {e}")
            self.info_var.set("Error al cargar imagen")

    def clear(self):
        self.current_path = None
        self._photo = None
        self.preview_label.config(image="", text="Ninguna imagen seleccionada")
        self.info_var.set("Ninguna imagen seleccionada")
