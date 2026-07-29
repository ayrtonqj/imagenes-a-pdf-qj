# 🖼️ Image to PDF Converter (Desktop Pro)

A modern, fast, and intuitive desktop application to convert images and compressed archives (ZIP, RAR) into organized PDF documents. Built with Python and **CustomTkinter** featuring a native dark mode UI.

Developed by **Ayrton QJ** ([@ayrtonqj](https://github.com/ayrtonqj)).

---

## ✨ Features

- **Modern Dark UI**: Powered by CustomTkinter with smooth dark themes, rounded cards, and responsive controls.
- **Smart Auto-Naming**: Automatically names the output PDF based on the first added folder, image, or ZIP/RAR file name.
- **Realistic Page Layout Preview**: Displays a live preview matching the selected PDF page size (A4, Letter, Legal, Original) and orientation (Portrait/Landscape).
- **Archive Extraction**: Automatically extracts and scans `.zip` and `.rar` archives.
- **Persistent Preferences**: Configure default page size, orientation, JPEG quality, and output folder in `⚙️ Settings`, saved permanently across runs.
- **Real Windows Documents Folder**: Automatically detects and uses the official Windows Shell Documents directory (supports OneDrive & folder redirection).
- **Batch Processing**: Convert hundreds of images into a single PDF in seconds.
- **Sorting & Reordering**: Move images up/down, drag & drop, or sort alphabetically A-Z.
- **Standalone Portable `.exe`**: Easily compile into a single `.exe` file with custom icon support.

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+ ([python.org](https://python.org))

### Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/ayrtonqj/imagenes-a-pdf-qj.git
   cd imagenes-a-pdf-qj
   ```

2. **Create & Activate Virtual Environment** (Optional but recommended)
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**
   ```bash
   python main.py
   ```

---

## 📦 Building Standalone Executable (.exe)

To build a portable `.exe` file with the custom logo icon:

```bash
pip install pyinstaller
python -m PyInstaller --noconsole --onefile --icon="img/logo.ico" --add-data "img/logo.png;img" --name "Imagenes_a_PDF" main.py
```

The compiled binary will be placed inside the `dist/` directory.

---

## 📁 Project Structure

```
img_to_pdf/
├── main.py              # Application entry point & window initialization
├── config_app.py        # Centralized project metadata (version, author, repo)
├── app.py               # Main CustomTkinter GUI layout & logic
├── preview.py           # Real-time PDF layout preview panel
├── pdf_generator.py     # High-performance PDF generation engine
├── file_handler.py      # Directory scanning, ZIP/RAR extraction & sorting
├── img/                 # Application icons and branding assets (logo.png, logo.ico)
├── requirements.txt     # Python dependencies
├── .gitignore           # Git ignore rules
├── README.md            # English documentation
└── INSTRUCCIONES.md     # Spanish installation & usage guide
```

---

## 📄 License

Distributed under the MIT License. Developed with ❤️ by [Ayrton QJ](https://github.com/ayrtonqj).
