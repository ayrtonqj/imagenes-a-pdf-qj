# 🖼️ Conversor de Imágenes a PDF (Desktop Pro)

Una aplicación de escritorio moderna, rápida e intuitiva para convertir imágenes y archivos comprimidos (ZIP, RAR) en documentos PDF organizados. Desarrollada en Python con **CustomTkinter** y diseño nativo en Modo Oscuro.

Desarrollado por **Ayrton QJ** ([@ayrtonqj](https://github.com/ayrtonqj)).

---

## ✨ Características Principales

- **Interfaz Moderna en Modo Oscuro**: Creada con CustomTkinter, ofrece una experiencia visual elegante con tarjetas redondeadas y controles receptivos.
- **Asignación Inteligente de Nombres**: Asigna automáticamente el nombre del PDF de salida según la primera carpeta, imagen o archivo ZIP/RAR seleccionado.
- **Vista Previa Proporcional del PDF**: Visualiza en tiempo real el resultado según el tamaño de página elegido (A4, Carta, Oficio, Original) y su orientación (Vertical/Horizontal).
- **Soporte para Archivos Comprimidos**: Descompresión y escaneo automático de archivos `.zip` y `.rar`.
- **Ajustes Persistentes**: Guarda tu configuración preferida en `⚙️ Ajustes` (tamaño de página, calidad, carpeta de salida) para recordarla en cada uso.
- **Ruta Real de Documentos de Windows**: Identifica automáticamente la ubicación oficial de la carpeta *Documentos* en Windows (compatible con OneDrive y carpetas redirigidas).
- **Conversión por Lotes**: Convierte cientos de imágenes en un solo PDF en cuestión de segundos.
- **Ordenamiento y Reorganización**: Permite subir/bajar posiciones, arrastrar o clasificar de A-Z.
- **Ejecutable Portable (.exe)**: Fácil compilación en un solo archivo `.exe` con ícono personalizado.

---

## 🛠️ Instalación y Configuración

### Requisitos Previos
- Python 3.8 o superior ([python.org](https://python.org))

### Pasos

1. **Clonar el Repositorio**
   ```bash
   git clone https://github.com/ayrtonqj/imagenes-a-pdf-qj.git
   cd imagenes-a-pdf-qj
   ```

2. **Crear y Activar un Entorno Virtual** (Opcional pero recomendado)
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

3. **Instalar Dependencias**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Ejecutar la Aplicación**
   ```powershell
   python main.py
   ```

---

## 📦 Compilación a Ejecutable Portable (.exe)

Para crear el archivo ejecutable portable `.exe` con el logo oficial del programa:

```powershell
pip install pyinstaller
python -m PyInstaller --noconsole --onefile --icon="img/logo.ico" --add-data "img;img" --name "Imagenes_a_PDF" main.py
```

El ejecutable compilado estará disponible en la carpeta `dist/`.

---

## 📁 Estructura del Proyecto

```
img_to_pdf/
├── main.py              # Punto de entrada e inicialización de la ventana con ícono
├── config_app.py        # Metadatos del proyecto (Versión, Autor, Repositorio)
├── app.py               # Lógica e interfaz gráfica CustomTkinter
├── preview.py           # Panel de vista previa proporcional
├── pdf_generator.py     # Motor de generación rápida de PDF
├── file_handler.py      # Escaneo de carpetas y extracción de ZIP/RAR
├── img/                 # Activos visuales (logo.png, logo.ico)
├── requirements.txt     # Dependencias de Python
├── .gitignore           # Archivos excluidos de Git
├── README.md            # Documentación principal en Español
└── INSTRUCCIONES.md     # Guía detallada de uso e instalación
```

---

## 📄 Licencia

Distribuido bajo la licencia MIT. Desarrollado con ❤️ por [Ayrton QJ](https://github.com/ayrtonqj).
