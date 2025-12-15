# -*- mode: python ; coding: utf-8 -*-

# tests/tests_runner.spec — сборка отдельного GUI раннера tests_runner.exe.

import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RUNNER_MAIN = os.path.join(BASE_DIR, "tests", "tests_runner_app.py")
IMG_DIR = os.path.join(BASE_DIR, "img")

a = Analysis(
    [RUNNER_MAIN],
    pathex=[BASE_DIR],
    binaries=[],
    datas=[(IMG_DIR, "img")],
    hiddenimports=["styles"],
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
    name="tests_runner",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # окно Tk, без консоли
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)


