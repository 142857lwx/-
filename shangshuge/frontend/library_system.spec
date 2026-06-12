# -*- coding: utf-8 -*-
import sys
from pathlib import Path

block_cipher = None

# 获取当前目录
current_dir = Path.spec

a = Analysis(
    ['main_server.py'],
    pathex=[str(current_dir)],
    binaries=[],
    datas=[
        (str(current_dir / 'index.html'), '.'),
        (str(current_dir / 'app.js'), '.'),
        (str(current_dir / 'server.js'), '.'),
        (str(current_dir / 'simple_server.py'), '.'),
        (str(current_dir / 'start_http.py'), '.'),
        (str(current_dir / 'start_server.ps1'), '.'),
        (str(Path(__file__).parent / 'shangshuge' / 'backend' / '*.py'), 'backend'),
    ],
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
    [],
    exclude_binaries=True,
    name='图书馆管理系统',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # 不显示控制台
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='图书馆管理系统',
)
