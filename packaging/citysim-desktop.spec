# -*- mode: python ; coding: utf-8 -*-
"""Spec de PyInstaller para el cliente de escritorio (ADR-0013).

Build:   pyinstaller packaging/citysim-desktop.spec
Salida:  dist/citysim-desktop[.exe]

Decisión onefile vs onedir: se usa **onefile** (un único archivo descargable, lo más
cómodo para distribuir). Pygame funciona bien en onefile porque su hook incluye SDL y la
fuente integrada (freesansbold) que la vista usa vía `pygame.font.Font(None, …)`; por eso
no hace falta `--add-data` para fuentes. Si en algún SO el arranque onefile diera
problemas (extracción lenta o antivirus), el fallback es cambiar a onedir: poner
`exclude_binaries=True` en el EXE y agregar un COLLECT. No se bundlean otros assets.
"""

block_cipher = None

a = Analysis(
    ["entry.py"],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="citysim-desktop",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # app de ventana: sin consola en Windows/macOS
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
