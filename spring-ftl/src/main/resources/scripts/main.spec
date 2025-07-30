# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['spring-ftl/src/main/resources/scripts/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('output/*', 'output'),
        ('spring-ftl/src/main/java/com/example/spring_ftl/controller/*', 'controller'),
        ('spring-ftl/src/main/java/com/example/spring_ftl/dto/*', 'dto'),
        ('spring-ftl/src/main/java/com/example/spring_ftl/service/*', 'service'),
        ('spring-ftl/src/main/resources/templates/*', 'templates'),
        ('*.properties', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=['__pycache__'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='spring_python_executable',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='dist'
)
