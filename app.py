import sys
import os
import json
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from pathlib import Path
from PIL import Image, ImageTk

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).parent / relative_path

from file_handler import collect_from_sources
from pdf_generator import generate_pdf
from preview import PreviewPanel
from config_app import (
    APP_NAME, APP_VERSION, APP_EDITION,
    DEVELOPER_NAME, DEVELOPER_HANDLE,
    GITHUB_REPO_URL, APP_DESCRIPTION
)

CONFIG_FILE = Path.home() / ".img_to_pdf_config.json"


def get_default_output_dir():
    try:
        import ctypes
        from ctypes import wintypes
        buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
        # CSIDL_PERSONAL = 5 (Real Windows Documents folder / OneDrive Documentos)
        ctypes.windll.shell32.SHGetFolderPathW(None, 5, None, 0, buf)
        if buf.value:
            doc_path = Path(buf.value) / "Imágenes a PDF"
        else:
            doc_path = Path.home() / "Documents" / "Imágenes a PDF"
    except Exception:
        doc_path = Path.home() / "Documents" / "Imágenes a PDF"

    try:
        doc_path.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    return str(doc_path)


def load_user_config():
    default_docs = get_default_output_dir()
    defaults = {
        "PAGE_SIZE": "A4",
        "ORIENTATION": "Portrait",
        "QUALITY": 95,
        "OUTPUT_DIR": default_docs,
        "OUTPUT_FILENAME": "output"
    }
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                defaults.update(data)
        except Exception:
            pass
    return defaults


def save_user_config(config_dict):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving config: {e}")


class ImageToPDFApp:
    def __init__(self, root):
        self.root = root

        self.files = []
        self.filtered_files = []
        self.temp_dirs = []
        self.selected_index = None

        self._load_config()
        self._build_ui()

    def _load_config(self):
        cfg = load_user_config()

        # User's saved preferences take highest priority
        self.page_size_default = cfg.get("PAGE_SIZE") or os.getenv("PAGE_SIZE") or "A4"
        self.orientation_default = cfg.get("ORIENTATION") or os.getenv("ORIENTATION") or "Portrait"

        q_val = cfg.get("QUALITY")
        if q_val is None:
            q_val = os.getenv("QUALITY", "95")
        self.quality_default = int(q_val)

        out_dir = cfg.get("OUTPUT_DIR")
        if not out_dir or out_dir == ".":
            out_dir = get_default_output_dir()
        self.output_dir_default = out_dir

        self.filename_default = cfg.get("OUTPUT_FILENAME") or os.getenv("OUTPUT_FILENAME") or "output"

    def _build_ui(self):
        # Main Layout
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        # 1. Toolbar
        toolbar = ctk.CTkFrame(self.root, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", padx=10, pady=(8, 4))

        ctk.CTkButton(toolbar, text="+ Archivos", width=100, command=self.add_files).pack(side="left", padx=3)
        ctk.CTkButton(toolbar, text="+ Carpeta", width=100, command=self.add_folder).pack(side="left", padx=3)
        ctk.CTkButton(toolbar, text="Limpiar Todo", width=100, fg_color="#ef4444", hover_color="#dc2626", command=self.clear_files).pack(side="left", padx=3)

        ctk.CTkLabel(toolbar, text="|", text_color="#555555").pack(side="left", padx=6)

        ctk.CTkButton(toolbar, text="▲ Subir", width=70, fg_color="#3f3f46", hover_color="#52525b", command=self.move_up).pack(side="left", padx=2)
        ctk.CTkButton(toolbar, text="▼ Bajar", width=70, fg_color="#3f3f46", hover_color="#52525b", command=self.move_down).pack(side="left", padx=2)
        ctk.CTkButton(toolbar, text="A-Z Ordenar", width=90, fg_color="#3f3f46", hover_color="#52525b", command=self.sort_files).pack(side="left", padx=2)

        ctk.CTkLabel(toolbar, text="|", text_color="#555555").pack(side="left", padx=6)
        ctk.CTkButton(toolbar, text="⚙️ Ajustes", width=90, fg_color="#3f3f46", hover_color="#52525b", command=self.open_settings_window).pack(side="left", padx=2)
        ctk.CTkButton(toolbar, text="ℹ️ Info", width=70, fg_color="#3f3f46", hover_color="#52525b", command=self.open_about_window).pack(side="left", padx=2)

        ctk.CTkButton(
            toolbar, text="⚡ Generar PDF", width=140, font=ctk.CTkFont(weight="bold"),
            fg_color="#2563eb", hover_color="#1d4ed8", command=self.start_generate_pdf
        ).pack(side="right", padx=3)

        # 2. Main Content (2 Columns)
        main_content = ctk.CTkFrame(self.root, fg_color="transparent")
        main_content.grid(row=1, column=0, sticky="nsew", padx=10, pady=4)
        main_content.columnconfigure(0, weight=1)
        main_content.columnconfigure(1, weight=1)
        main_content.rowconfigure(0, weight=1)

        # Left Column: Search & Image List
        left_frame = ctk.CTkFrame(main_content, fg_color="#18181b", corner_radius=10)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=0)
        left_frame.rowconfigure(2, weight=1)
        left_frame.columnconfigure(0, weight=1)

        filter_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        filter_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 4))
        
        self.filter_var = tk.StringVar()
        self.filter_var.trace_add("write", lambda *a: self._apply_filter())
        filter_entry = ctk.CTkEntry(filter_frame, placeholder_text="🔍 Buscar imagen...", textvariable=self.filter_var)
        filter_entry.pack(fill="x", expand=True)

        self.counter_var = tk.StringVar(value="0 imágenes")
        ctk.CTkLabel(left_frame, textvariable=self.counter_var, text_color="#a1a1aa", font=ctk.CTkFont(size=12)).grid(row=1, column=0, sticky="w", padx=12, pady=(0, 4))

        self.thumb_container = ctk.CTkScrollableFrame(left_frame, fg_color="#09090b", corner_radius=8)
        self.thumb_container.grid(row=2, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self.thumb_container.columnconfigure(0, weight=1)

        # Right Column: Preview & Configuration
        right_frame = ctk.CTkFrame(main_content, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=0)
        right_frame.rowconfigure(0, weight=1)
        right_frame.columnconfigure(0, weight=1)

        # Preview Panel
        preview_outer = ctk.CTkFrame(right_frame, fg_color="#18181b", corner_radius=10)
        preview_outer.grid(row=0, column=0, sticky="nsew", pady=(0, 8))
        preview_outer.rowconfigure(1, weight=1)
        preview_outer.columnconfigure(0, weight=1)

        ctk.CTkLabel(preview_outer, text="Vista Previa", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, sticky="w", padx=12, pady=(8, 2))
        self.preview_panel = PreviewPanel(preview_outer, fg_color="transparent")
        self.preview_panel.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 6))

        # Configuration Panel
        config_outer = ctk.CTkFrame(right_frame, fg_color="#18181b", corner_radius=10)
        config_outer.grid(row=1, column=0, sticky="ew")
        config_outer.columnconfigure(1, weight=1)
        config_outer.columnconfigure(2, weight=1)

        ctk.CTkLabel(config_outer, text="Configuración del PDF", font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(8, 6))

        # Row 1: Tamaño
        ctk.CTkLabel(config_outer, text="Tamaño:").grid(row=1, column=0, sticky="e", padx=(10, 5), pady=3)
        self.page_size_var = tk.StringVar(value=self.page_size_default)
        ctk.CTkOptionMenu(
            config_outer, variable=self.page_size_var,
            values=["A4", "Letter", "Legal", "Original"], width=130
        ).grid(row=1, column=1, sticky="w", pady=3)

        # Row 2: Orientación
        ctk.CTkLabel(config_outer, text="Orientación:").grid(row=2, column=0, sticky="e", padx=(10, 5), pady=3)
        self.orientation_var = tk.StringVar(value=self.orientation_default)
        ctk.CTkOptionMenu(
            config_outer, variable=self.orientation_var,
            values=["Portrait", "Landscape"], width=130
        ).grid(row=2, column=1, sticky="w", pady=3)

        # Row 3: Calidad
        ctk.CTkLabel(config_outer, text="Calidad:").grid(row=3, column=0, sticky="e", padx=(10, 5), pady=3)
        self.quality_var = tk.IntVar(value=self.quality_default)
        qf = ctk.CTkFrame(config_outer, fg_color="transparent")
        qf.grid(row=3, column=1, sticky="ew", pady=3)
        ctk.CTkSlider(qf, from_=1, to=100, number_of_steps=99, variable=self.quality_var, width=130).pack(side="left")
        ctk.CTkLabel(qf, textvariable=self.quality_var, width=30).pack(side="left", padx=(5, 0))

        # Row 4: Salida
        ctk.CTkLabel(config_outer, text="Salida:").grid(row=4, column=0, sticky="e", padx=(10, 5), pady=3)
        of = ctk.CTkFrame(config_outer, fg_color="transparent")
        of.grid(row=4, column=1, sticky="ew", pady=3)
        self.output_var = tk.StringVar(value=self.output_dir_default)
        ctk.CTkEntry(of, textvariable=self.output_var).pack(side="left", fill="x", expand=True)
        ctk.CTkButton(of, text="Examinar", width=70, command=self.browse_output).pack(side="right", padx=(5, 0))

        # Row 5: Archivo
        ctk.CTkLabel(config_outer, text="Archivo:").grid(row=5, column=0, sticky="e", padx=(10, 5), pady=(3, 8))
        self.filename_var = tk.StringVar(value=self.filename_default)
        ctk.CTkEntry(config_outer, textvariable=self.filename_var).grid(row=5, column=1, sticky="ew", pady=(3, 8))

        # Structured Description Info Card (Right side)
        info_card = ctk.CTkFrame(config_outer, fg_color="#09090b", corner_radius=8)
        info_card.grid(row=0, column=2, rowspan=6, sticky="nsew", padx=(10, 10), pady=8)
        info_card.columnconfigure(0, weight=1)

        ctk.CTkLabel(
            info_card, text="ℹ️ Detalle de Ajustes",
            font=ctk.CTkFont(size=12, weight="bold"), text_color="#38bdf8"
        ).pack(anchor="w", padx=10, pady=(8, 4))

        self.desc_size_label = ctk.CTkLabel(
            info_card, text="", font=ctk.CTkFont(size=11), text_color="#e4e4e7",
            anchor="w", justify="left"
        )
        self.desc_size_label.pack(anchor="w", padx=10, pady=2)

        self.desc_ori_label = ctk.CTkLabel(
            info_card, text="", font=ctk.CTkFont(size=11), text_color="#e4e4e7",
            anchor="w", justify="left"
        )
        self.desc_ori_label.pack(anchor="w", padx=10, pady=2)

        self.desc_q_label = ctk.CTkLabel(
            info_card, text="", font=ctk.CTkFont(size=11), text_color="#a1a1aa",
            anchor="w", justify="left"
        )
        self.desc_q_label.pack(anchor="w", padx=10, pady=(2, 8))

        self.page_size_var.trace_add("write", self._on_config_change)
        self.orientation_var.trace_add("write", self._on_config_change)
        self.quality_var.trace_add("write", self._on_config_change)

        self.root.after(100, self._on_config_change)

        # 3. Status Bar
        progress_frame = ctk.CTkFrame(self.root, fg_color="#18181b", corner_radius=6)
        progress_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 6))
        
        self.progress = ctk.CTkProgressBar(progress_frame, mode="determinate")
        self.progress.pack(side="left", fill="x", expand=True, padx=10, pady=8)
        self.progress.set(0)

        self.status_var = tk.StringVar(value="Listo")
        ctk.CTkLabel(progress_frame, textvariable=self.status_var, text_color="#a1a1aa").pack(side="right", padx=10)

    def _on_config_change(self, *args):
        ps = self.page_size_var.get()
        ori = self.orientation_var.get()
        q = self.quality_var.get()

        size_info = {
            "A4": "📐 Tamaño: A4 (210 × 297 mm)\n   Estándar internacional.",
            "Letter": "📐 Tamaño: Carta (8.5 × 11 in)\n   Estándar común en América.",
            "Legal": "📐 Tamaño: Oficio (8.5 × 14 in)\n   Formato extendido para oficina.",
            "Original": "📐 Tamaño: Original de Imagen\n   Mantiene la resolución nativa."
        }.get(ps, "")

        ori_info = "🔄 Orientación: Vertical (Portrait)" if ori == "Portrait" else "🔄 Orientación: Horizontal (Landscape)"

        q_info = f"🗜️ Calidad JPG: {q}%\n   (" + ("Menor tamaño de archivo" if q < 85 else "Excelente fidelidad visual") + ")"

        self.desc_size_label.configure(text=size_info)
        self.desc_ori_label.configure(text=ori_info)
        self.desc_q_label.configure(text=q_info)

        if hasattr(self, "preview_panel"):
            self.preview_panel.set_config(ps, ori)

    def open_settings_window(self):
        settings_win = ctk.CTkToplevel(self.root)
        settings_win.title("⚙️ Configuración Predeterminada")
        settings_win.geometry("480x400")
        settings_win.resizable(False, False)
        settings_win.grab_set()

        ctk.CTkLabel(
            settings_win, text="⚙️ Ajustes Predeterminados de la App",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(15, 10))

        form_frame = ctk.CTkFrame(settings_win, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=20, pady=5)
        form_frame.columnconfigure(1, weight=1)

        # Page Size
        ctk.CTkLabel(form_frame, text="Tamaño Predeterminado:").grid(row=0, column=0, sticky="e", padx=5, pady=8)
        size_var = tk.StringVar(value=self.page_size_var.get())
        ctk.CTkOptionMenu(form_frame, variable=size_var, values=["A4", "Letter", "Legal", "Original"]).grid(row=0, column=1, sticky="w", padx=5, pady=8)

        # Orientation
        ctk.CTkLabel(form_frame, text="Orientación Predeterminada:").grid(row=1, column=0, sticky="e", padx=5, pady=8)
        ori_var = tk.StringVar(value=self.orientation_var.get())
        ctk.CTkOptionMenu(form_frame, variable=ori_var, values=["Portrait", "Landscape"]).grid(row=1, column=1, sticky="w", padx=5, pady=8)

        # Quality
        ctk.CTkLabel(form_frame, text="Calidad Predeterminada:").grid(row=2, column=0, sticky="e", padx=5, pady=8)
        quality_var = tk.IntVar(value=self.quality_var.get())
        q_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        q_frame.grid(row=2, column=1, sticky="ew", padx=5, pady=8)
        ctk.CTkSlider(q_frame, from_=1, to=100, number_of_steps=99, variable=quality_var, width=120).pack(side="left")
        ctk.CTkLabel(q_frame, textvariable=quality_var, width=30).pack(side="left", padx=5)

        # Output Dir
        ctk.CTkLabel(form_frame, text="Carpeta de Salida:").grid(row=3, column=0, sticky="e", padx=5, pady=8)
        out_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        out_frame.grid(row=3, column=1, sticky="ew", padx=5, pady=8)
        out_var = tk.StringVar(value=self.output_var.get())
        ctk.CTkEntry(out_frame, textvariable=out_var).pack(side="left", fill="x", expand=True)

        def browse_def():
            d = filedialog.askdirectory(initialdir=out_var.get())
            if d:
                out_var.set(d)

        ctk.CTkButton(out_frame, text="...", width=35, command=browse_def).pack(side="right", padx=(5, 0))

        def save_action():
            cfg = {
                "PAGE_SIZE": size_var.get(),
                "ORIENTATION": ori_var.get(),
                "QUALITY": quality_var.get(),
                "OUTPUT_DIR": out_var.get(),
                "OUTPUT_FILENAME": self.filename_var.get()
            }
            save_user_config(cfg)
            self.page_size_var.set(size_var.get())
            self.orientation_var.set(ori_var.get())
            self.quality_var.set(quality_var.get())
            self.output_var.set(out_var.get())
            self.status_var.set("Ajustes predeterminados guardados")
            settings_win.destroy()

        def reset_action():
            confirm = messagebox.askyesno(
                "Confirmar Restablecimiento",
                "¿Estás seguro de que deseas restablecer todos los valores a los ajustes de fábrica?",
                parent=settings_win
            )
            if confirm:
                default_path = get_default_output_dir()
                size_var.set("A4")
                ori_var.set("Portrait")
                quality_var.set(95)
                out_var.set(default_path)

                self.page_size_var.set("A4")
                self.orientation_var.set("Portrait")
                self.quality_var.set(95)
                self.output_var.set(default_path)

                save_user_config({
                    "PAGE_SIZE": "A4",
                    "ORIENTATION": "Portrait",
                    "QUALITY": 95,
                    "OUTPUT_DIR": default_path,
                    "OUTPUT_FILENAME": "output"
                })
                self.status_var.set("Ajustes restablecidos por defecto")
                settings_win.destroy()

        btn_box = ctk.CTkFrame(settings_win, fg_color="transparent")
        btn_box.pack(fill="x", padx=20, pady=(10, 15))

        ctk.CTkButton(
            btn_box, text="🔄 Restablecer", width=120,
            fg_color="#475569", hover_color="#334155",
            command=reset_action
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_box, text="💾 Guardar", width=140,
            font=ctk.CTkFont(weight="bold"), fg_color="#2563eb", hover_color="#1d4ed8",
            command=save_action
        ).pack(side="right", padx=5)

    def open_about_window(self):
        about_win = ctk.CTkToplevel(self.root)
        about_win.title(f"ℹ️ Acerca de - {APP_NAME}")
        about_win.geometry("450x420")
        about_win.resizable(False, False)
        about_win.grab_set()

        logo_path = get_resource_path("img/logo.png")
        if logo_path.exists():
            try:
                logo_img = Image.open(logo_path)
                logo_img.thumbnail((56, 56), Image.LANCZOS)
                photo = ImageTk.PhotoImage(logo_img)
                lbl_logo = tk.Label(about_win, image=photo, bg="#242424", bd=0)
                lbl_logo.image = photo
                lbl_logo.pack(pady=(12, 2))
            except Exception:
                pass

        ctk.CTkLabel(
            about_win, text=f"{APP_NAME}",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(2, 2))

        ctk.CTkLabel(
            about_win, text=f"Versión {APP_VERSION} ({APP_EDITION})",
            font=ctk.CTkFont(size=12), text_color="#a1a1aa"
        ).pack(pady=(0, 10))

        info_frame = ctk.CTkFrame(about_win, fg_color="#18181b", corner_radius=8)
        info_frame.pack(fill="both", expand=True, padx=20, pady=5)

        ctk.CTkLabel(
            info_frame, text="👤 Desarrollador:",
            font=ctk.CTkFont(size=12, weight="bold"), text_color="#38bdf8"
        ).pack(anchor="w", padx=15, pady=(12, 2))

        ctk.CTkLabel(
            info_frame, text=f"{DEVELOPER_NAME} ({DEVELOPER_HANDLE})",
            font=ctk.CTkFont(size=13), text_color="#e4e4e7"
        ).pack(anchor="w", padx=25, pady=(0, 8))

        ctk.CTkLabel(
            info_frame, text="🌐 Repositorio GitHub:",
            font=ctk.CTkFont(size=12, weight="bold"), text_color="#38bdf8"
        ).pack(anchor="w", padx=15, pady=(4, 2))

        def open_repo():
            import webbrowser
            webbrowser.open(GITHUB_REPO_URL)

        repo_link = ctk.CTkLabel(
            info_frame, text=GITHUB_REPO_URL,
            font=ctk.CTkFont(size=12, underline=True), text_color="#60a5fa", cursor="hand2"
        )
        repo_link.pack(anchor="w", padx=25, pady=(0, 10))
        repo_link.bind("<Button-1>", lambda e: open_repo())

        ctk.CTkLabel(
            info_frame, text=APP_DESCRIPTION,
            font=ctk.CTkFont(size=11), text_color="#a1a1aa", justify="left"
        ).pack(anchor="w", padx=15, pady=(0, 12))

        ctk.CTkButton(
            about_win, text="Cerrar", width=100,
            fg_color="#3f3f46", hover_color="#52525b",
            command=about_win.destroy
        ).pack(pady=(10, 15))


    def add_files(self):
        paths = filedialog.askopenfilenames(
            title="Seleccionar imágenes o comprimidos",
            filetypes=[
                ("Todos los soportados", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.tif *.webp *.zip *.rar"),
                ("Imágenes", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.tif *.webp"),
                ("Comprimidos", "*.zip *.rar"),
                ("Todos los archivos", "*.*"),
            ],
        )
        if paths:
            # Auto-assign output filename from the first file selected
            first_stem = Path(paths[0]).stem
            if first_stem:
                self.filename_var.set(first_stem)
            self._process_sources(list(paths))

    def add_folder(self):
        path = filedialog.askdirectory(title="Seleccionar carpeta")
        if path:
            # Auto-assign output filename from the selected folder name
            folder_name = Path(path).name
            if folder_name:
                self.filename_var.set(folder_name)
            self._process_sources([path])

    def _process_sources(self, sources):
        self.status_var.set("Escaneando...")
        self.progress.set(0)

        def task():
            def pc(current, total, msg):
                val = current / max(total, 1)
                self.root.after(0, lambda: self.progress.set(val))
                self.root.after(0, lambda: self.status_var.set(msg))

            try:
                new_images, new_temp_dirs = collect_from_sources(sources, pc)
                self.root.after(0, lambda: self._add_images(new_images))
                self.temp_dirs.extend(new_temp_dirs)
                self.root.after(0, lambda: self.status_var.set(f"{len(new_images)} imágenes agregadas"))
                self.root.after(0, lambda: self.progress.set(0))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
                self.root.after(0, lambda: self.status_var.set("Error"))

        threading.Thread(target=task, daemon=True).start()

    def _add_images(self, new_images):
        existing = set(self.files)
        for img in new_images:
            if img not in existing:
                self.files.append(img)
                existing.add(img)
        self._apply_filter()

    def _apply_filter(self):
        text = self.filter_var.get().lower()
        if text:
            self.filtered_files = [f for f in self.files if text in Path(f).name.lower()]
        else:
            self.filtered_files = list(self.files)
        self._rebuild_thumbnails()

    def _rebuild_thumbnails(self):
        for widget in self.thumb_container.winfo_children():
            widget.destroy()

        self.selected_index = None
        self.counter_var.set(f"{len(self.files)} imágenes ({len(self.filtered_files)} visibles)")

        for idx, filepath in enumerate(self.filtered_files):
            self._create_thumbnail_item(filepath, idx)

    def _create_thumbnail_item(self, filepath, index):
        is_selected = (self.selected_index == index)
        fg = "#27272a" if is_selected else "#18181b"
        
        frame = ctk.CTkFrame(self.thumb_container, fg_color=fg, corner_radius=6, cursor="hand2")
        frame.pack(fill="x", padx=2, pady=2)

        num_label = ctk.CTkLabel(frame, text=str(index + 1), width=24, text_color="#71717a", font=ctk.CTkFont(size=11, weight="bold"))
        num_label.pack(side="left", padx=(6, 2))

        thumb_label = tk.Label(frame, bg="#18181b", bd=0)
        thumb_label.pack(side="left", padx=4)

        try:
            img = Image.open(filepath)
            img.thumbnail((42, 42), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            thumb_label.config(image=photo)
            thumb_label.image = photo
        except Exception:
            thumb_label.config(text="[ERR]", fg="#ef4444")

        name = Path(filepath).name
        name_label = ctk.CTkLabel(frame, text=name, anchor="w", font=ctk.CTkFont(size=12))
        name_label.pack(side="left", fill="x", expand=True, padx=4)

        for widget in (frame, num_label, thumb_label, name_label):
            widget.bind("<Button-1>", lambda e, i=index: self._on_item_click(i))
            widget.bind("<Double-Button-1>", lambda e, fp=filepath: self.preview_panel.show_image(fp))

    def _on_item_click(self, index):
        self._select_item(index)
        self.preview_panel.show_image(self.filtered_files[index])

    def _select_item(self, index):
        children = self.thumb_container.winfo_children()
        for i, child in enumerate(children):
            if i == index:
                child.configure(fg_color="#27272a", border_width=1, border_color="#3b82f6")
            else:
                child.configure(fg_color="#18181b", border_width=0)
        self.selected_index = index

    def move_up(self):
        if self.selected_index is None or self.selected_index == 0:
            return
        i = self.selected_index
        fp = self.filtered_files[i]
        fp_above = self.filtered_files[i - 1]
        idx = self.files.index(fp)
        idx_above = self.files.index(fp_above)
        self.files[idx], self.files[idx_above] = self.files[idx_above], self.files[idx]
        self._apply_filter()
        self._select_item(i - 1)

    def move_down(self):
        if self.selected_index is None or self.selected_index >= len(self.filtered_files) - 1:
            return
        i = self.selected_index
        fp = self.filtered_files[i]
        fp_below = self.filtered_files[i + 1]
        idx = self.files.index(fp)
        idx_below = self.files.index(fp_below)
        self.files[idx], self.files[idx_below] = self.files[idx_below], self.files[idx]
        self._apply_filter()
        self._select_item(i + 1)

    def sort_files(self):
        self.files.sort(key=lambda x: Path(x).name.lower())
        self._apply_filter()
        if self.filtered_files:
            self._select_item(0)
        self.status_var.set("Archivos ordenados A-Z")

    def clear_files(self):
        self.files.clear()
        self.filtered_files.clear()
        self.selected_index = None
        self._rebuild_thumbnails()
        self.preview_panel.clear()
        for d in self.temp_dirs:
            try:
                import shutil
                shutil.rmtree(d, ignore_errors=True)
            except Exception:
                pass
        self.temp_dirs.clear()
        self.status_var.set("Limpiado")

    def browse_output(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Archivos PDF", "*.pdf")],
            initialdir=self.output_var.get(),
            initialfile=self.filename_var.get() + ".pdf",
        )
        if path:
            self.output_var.set(os.path.dirname(path))
            self.filename_var.set(Path(path).stem)

    def start_generate_pdf(self):
        if not self.files:
            messagebox.showwarning("Sin imágenes", "No hay imágenes para convertir. Agrega archivos primero.")
            return

        output_dir = self.output_var.get()
        filename = self.filename_var.get()
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error", f"No se puede crear la carpeta de salida:\n{e}")
            return

        output_path = os.path.join(output_dir, filename + ".pdf")
        page_size = self.page_size_var.get()
        orientation = self.orientation_var.get()
        quality = self.quality_var.get()

        self.status_var.set("Generando PDF...")
        self.progress.set(0)

        def task():
            def pc(current, total, msg):
                val = current / max(total, 1)
                self.root.after(0, lambda: self.progress.set(val))
                self.root.after(0, lambda: self.status_var.set(msg))

            try:
                generate_pdf(self.files, output_path, page_size, orientation, quality, pc)
                self.root.after(0, lambda: self.status_var.set(f"Guardado: {Path(output_path).name}"))
                self.root.after(0, lambda: self.progress.set(0))
                self.root.after(0, lambda: messagebox.showinfo("Éxito", f"PDF generado:\n{output_path}"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
                self.root.after(0, lambda: self.status_var.set("Error"))

        threading.Thread(target=task, daemon=True).start()

    def on_close(self):
        for d in self.temp_dirs:
            try:
                import shutil
                shutil.rmtree(d, ignore_errors=True)
            except Exception:
                pass
        self.root.destroy()
