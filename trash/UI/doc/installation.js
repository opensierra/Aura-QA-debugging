window.DOCS_DATA = window.DOCS_DATA || {};
window.DOCS_DATA["installation"] = `# Installation Guide

## Prerequisites

| Requirement | Details |
|-------------|---------|
| OS | Windows (batch scripts) |
| Internet | Required during setup only (3 downloads) |
| Android device | USB-connected, USB debugging enabled |
| BlueCode | Must be installed separately and available in system PATH |

No system Python is required. The embedded Python is extracted from
\`Python.rar\` during setup.

## First-Time Setup

1. Run \`setup.bat\` from the distribution folder:
   \`\`\`
   setup.bat
   \`\`\`

   This will:
   - Extract \`Python.rar\` to \`.\\Python\\\` (embedded Python 3.12)
   - Verify \`python312._pth\` is configured (site-packages + Customlib already set)
   - Download \`get-pip.py\` via PowerShell (INTERNET REQUIRED)
   - Install pip in the embedded Python
   - Download all 66 dependencies from \`requirements.txt\` as wheels (INTERNET REQUIRED)
   - Install dependencies into the embedded Python (offline step)
   - Download PaddleOCR models to \`.\\models\\paddlex\\\` (INTERNET REQUIRED)
   - Clean up temporary wheels directory

2. After \`setup.bat\` completes, the folder is offline and portable (except
   for BlueCode, which must be installed on each machine).

## Internet Usage

| Step | What | Why |
|------|------|-----|
| 3 | \`get-pip.py\` download | Bootstrapping pip in embedded Python (via PowerShell) |
| 5 | \`pip download\` | Fetching all Python packages as wheels |
| 7 | PaddleOCR model download | Pre-caching OCR models for offline use |

## Post-Setup

After setup, the distribution folder contains:
\`\`\`
dist/
  Python/              Embedded Python with all packages installed
  models/paddlex/      PaddleOCR model files
  Tools/               ADB, apktool, vis-network.js, get-pip.py
  Java/                JRE for apktool
  Customlib/           Pipeline source code
  phoenix              Entry point
  plk.bat              Launcher
  requirements.txt     Dependency list (reference)
  Python.rar           Preserved for re-installation
\`\`\`

\`get-pip.py\` and \`Python.rar\` are preserved after setup so the
installation can be re-run without needing to re-download them.

## Device Preparation

1. Connect an Android device via USB.
2. Enable **USB debugging** in Developer Options.
3. Authorize the computer when the RSA fingerprint dialog appears.
4. Verify ADB detects the device:
   \`\`\`
   adb devices
   \`\`\`
   The device must appear as \`device\` (not \`unauthorized\`).
5. Initialize uiautomator2 on the device (first time only):
   \`\`\`
   plk.bat -m uiautomator2 init
   \`\`\`
   **Note:** This instruction is inferred from general uiautomator2
   documentation. No project file references this command. It is required
   because uiautomator2 needs to install a helper APK (ATX agent) on the
   device before \`u2.connect()\` can work.
6. Set the device locale to the **source** language of the pair (e.g.,
   \`id\` for an \`id-en\` run). The pipeline does not change device locale.

## BlueCode Preparation

1. Verify BlueCode is installed and in PATH:
   \`\`\`
   bluecode --version
   \`\`\`
2. If not, install it separately (it is not bundled with FENNIX 2).
3. The pipeline starts the BlueCode server automatically on an
   **auto-selected free port** (\`BC_PORT=0\` in \`config.py\`). No fixed
   port is required and no pre-existing server is reused.

## Clean Re-install

To perform a clean re-install:
1. Delete the \`Python/\` directory.
2. Delete the \`models/\` directory.
3. Re-run \`setup.bat\` (it will use the preserved \`Python.rar\` and
   \`get-pip.py\`).

## Note on Portability

- The Python environment is portable post-setup.
- ADB, apktool, and Java JRE are bundled.
- PaddleOCR models are pre-downloaded.
- **BlueCode is NOT bundled** — must be installed on each machine.
- The system is Windows-only (batch scripts).
`;
