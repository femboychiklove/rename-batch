# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['../assets/main.py'],
    pathex=['../assets'],
    binaries=[],
    datas=[('../assets', 'assets')],
    hiddenimports=[
        'customtkinter',
        'tkinter',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='rename-batch',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon='../installer/icon.ico',
) 
