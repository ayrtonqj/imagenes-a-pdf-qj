# 🖼️ Conversor de Imágenes a PDF (Desktop Pro)

Aplicación de escritorio moderna y rápida para convertir imágenes individuales y archivos comprimidos (ZIP, RAR) en documentos PDF organizados. Cuenta con una interfaz visual elegante en **Modo Oscuro** basada en **CustomTkinter**.

Desarrollado por **Ayrton QJ** ([@ayrtonqj](https://github.com/ayrtonqj)).

---

## ✨ Características Principales

- **Interfaz Moderna en Modo Oscuro**: Diseño limpio con tarjetas redondeadas, controles receptivos y panel visual intuitivo.
- **Asignación Inteligente de Nombre**: El archivo PDF toma automáticamente el nombre de la carpeta, imagen o comprimido `.zip`/`.rar` seleccionado.
- **Vista Previa Realista**: Muestra la proporción exacta del PDF según la configuración de página elegida (A4, Carta, Oficio, Original) y su orientación (Vertical/Horizontal).
- **Soporte para Comprimidos**: Descompresión y escaneo automático de archivos `.zip` y `.rar`.
- **Ajustes Persistentes**: Guarda tu tamaño de página, orientación, calidad y carpeta por defecto desde el botón `⚙️ Ajustes`. Se recordará en ejecuciones futuras.
- **Detección Real de la Carpeta Documentos**: Identifica la ubicación oficial de *Documentos* en Windows (con soporte para OneDrive y carpetas redirigidas).
- **Reordenamiento y Filtro**: Permite subir/bajar imágenes, filtrar por nombre o clasificar de A-Z.
- **Ejecutable Portable (.exe)**: Se empaqueta fácilmente en un solo archivo `.exe` con ícono personalizado.

---

## 🚀 Guía de Instalación y Uso

### Requisitos Previos
- Python 3.8 o superior ([python.org](https://python.org))

### Pasos de Instalación

1. **Descargar / Clonar el proyecto**
   ```bash
   git clone https://github.com/ayrtonqj/imagenes-a-pdf-qj.git
   cd imagenes-a-pdf-qj
   ```

2. **Crear y activar un entorno virtual** (Opcional recomendado)
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

3. **Instalar dependencias**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Ejecutar la aplicación**
   ```powershell
   python main.py
   ```

---

## 🛠️ Compilar a archivo Ejecutable (.exe)

Para crear tu propio ejecutable portable con el logo personalizado de la aplicación:

```powershell
pip install pyinstaller
python -m PyInstaller --noconsole --onefile --icon="img/logo.ico" --add-data "img/logo.png;img" --name "Imagenes_a_PDF" main.py
```

El ejecutable listo se guardará en la carpeta `dist/Imagenes_a_PDF.exe`.

---

## 📂 Estructura de Archivos del Proyecto

```
img_to_pdf/
├── main.py              # Punto de entrada e inicialización de la ventana
├── config_app.py        # Metadatos del proyecto (Versión, Autor, Repositorio)
├── app.py               # Lógica de interfaz gráfica CustomTkinter
├── preview.py           # Panel de vista previa proporcional del PDF
├── pdf_generator.py     # Motor de generación de PDF rápido
├── file_handler.py      # Escaneo de carpetas y extracción de ZIP/RAR
├── img/                 # Íconos y activos de la aplicación (logo.png, logo.ico)
├── requirements.txt     # Dependencias de Python
├── .gitignore           # Reglas de exclusión para Git
├── README.md            # Documentación en Inglés
└── INSTRUCCIONES.md     # Guía en Español
```

---

## 🧹 Limpieza de Archivos No Necesarios

Si vas a subir tu proyecto a GitHub, puedes eliminar con seguridad los siguientes archivos/carpetas temporales sin afectar el código:

1. Carpetas `build/` y `dist/` *(Archivos temporales de compilación)*.
2. Archivos `.spec` *(Ficheros generados por PyInstaller)*.
3. Carpeta `__pycache__/` *(Caché de Python)*.
4. Archivos `.pdf` de prueba generados en la raíz.
5. Carpeta `.venv/` o `venv/` *(Entorno virtual local)*.
