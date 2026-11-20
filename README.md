# Aura QA

Herramienta de QA automatizado para dispositivos Android. Crea un pipeline completo de listing, crawling de UI, captura de screenshots, análisis OCR y exportación de reportes.

## Características

- **Listing**: Enumera paquetes instalados en el DUT (Device Under Test)
- **Crawl**: Navega la UI de cada app capturando screenshots
- **QA**: Análisis de screenshots con OCR (PaddleOCR) y detección de problemas
- **AutoExport**: Genera reportes en Excel/PDF con los resultados
- **Grafos**: Visualización de navegación UI con vis-network
- **Portable**: Entorno Python embebido, no requiere instalación de Python en el sistema

## Estructura

```
├── GUI                  # Aplicación principal (pywebview)
├── run_pipeline.py      # Runner del pipeline (subproceso de la GUI)
├── phoenix              # Pipeline QA-only (sin DUT)
├── plk.bat              # Script de ejecución directa
├── setup.bat            # Instalador portable (Python embebido + deps)
├── requirements.txt     # Dependencias Python
├── Customlib/
│   ├── sgna_listing.py  # Enumeración de paquetes
│   ├── sgna_crawler.py  # Crawler de UI
│   ├── sgna_qa.py       # Motor de QA
│   ├── sgna_dut.py      # Control del DUT (ADB)
│   ├── sgna_extractor.py# Extracción de APKs
│   ├── sgna_graph.py    # Generación de grafos de navegación
│   ├── sgna_vivotune.py # Integración VivoTune
│   ├── sgna_log.py      # Logging
│   ├── sgna_extractor.py
│   ├── run_state.py     # Estado del pipeline
│   ├── psdns.py         # Motor de decisión
│   ├── psdns2.py
│   ├── psdns.json       # Data del motor de decisión
│   ├── qa_export/       # Exportación de reportes
│   ├── sgna_crawler/    # Módulos del crawler
│   ├── DeepBlue/        # Motor BlueCode (IA)
│   └── UiBrowser.py     # Navegador UI
├── UI/
│   ├── index.html       # Interfaz web
│   ├── app.js           # Lógica de la UI
│   ├── style.css        # Estilos
│   └── settings.json    # Configuración por defecto
├── Tools/
│   ├── vis-network.min.js  # Lib de grafos
│   └── get-pip.py          # Bootstrap de pip
├── inno/                # Scripts de Inno Setup (instalador)
└── src launcher/        # Launcher C++ (Win32)
```

## Requisitos

- Windows 10/11
- ADB (Android Debug Bridge) en PATH
- Dispositivo Android conectado (para listing/crawl)
- Internet solo para el primer `setup.bat`

## Instalación

```bat
setup.bat
```

Esto descarga Python embebido, instala todas las dependencias y pre-descarga los modelos de OCR. Después de esto, el proyecto es 100% offline y portable.

## Uso

### Con GUI

```bat
plk.bat
```

### Pipeline completo (listing → crawl → QA → export)

```bat
Python\python.exe run_pipeline.py <config.json>
```

### Solo QA (screenshots ya en disco)

```bat
Python\python.exe phoenix --qa-only
```

## Pipeline

```
┌─────────┐    ┌───────┐    ┌────┐    ┌───────────┐
│ Listing │ →  │ Crawl │ →  │ QA │ →  │ AutoExport│
└─────────┘    └───────┘    └────┘    └───────────┘
  Paquetes      Screenshots   OCR +     Excel/PDF
  instalados    por app       análisis  + Grafos
```

Cada etapa es opcional y configurable.

## Build del instalador

1. Compilar launcher: `src launcher\setup.bat`
2. Compilar Inno Setup: abrir el `.iss` en `inno/` y compilar

## Stack

- Python 3.12 (embebido)
- pywebview (GUI)
- PaddleOCR / PaddleX (OCR)
- uiautomator2 + ADB (control de dispositivo)
- androguard (análisis de APKs)
- networkx + vis-network (grafos)
- openpyxl / xlsxwriter (export Excel)
- C++ Win32 (launcher)
- Inno Setup 7 (instalador)
