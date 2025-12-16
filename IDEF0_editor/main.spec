# -*- mode: python ; coding: utf-8 -*-

import os

# PyInstaller автоматически добавляет директорию со spec файлом в путь поиска модулей
# Если нужно явно указать путь, используем os.getcwd() (PyInstaller запускается из директории со spec)
# или просто не указываем pathex, так как PyInstaller сам найдет модули
a = Analysis(
    ['main.py'],
    pathex=[],  # PyInstaller автоматически добавляет директорию со spec файлом
    binaries=[],
    datas=[('img', 'img')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Временно включено для отладки, можно вернуть False после проверки
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
