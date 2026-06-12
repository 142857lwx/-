# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main_server.py'],
    pathex=[],
    binaries=[],
    datas=[('index.html', '.'), ('app.js', '.'), ('server.js', '.'), ('simple_server.py', '.'), ('start_http.py', '.'), ('start_server.ps1', '.'), ('..\\backend\\*.py', 'backend')],
    hiddenimports=['pkg_resources', 'html', 'http', 'socketserver'],
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
    name='图书馆管理系统',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
