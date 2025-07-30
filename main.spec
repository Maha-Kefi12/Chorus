# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['spring-ftl/src/main/resources/scripts/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('output', 'output'), 
        ('spring-ftl/src/main/java/com/example/spring_ftl/controller', 'controller'), 
        ('spring-ftl/src/main/java/com/example/spring_ftl/dto', 'dto'), 
        ('spring-ftl/src/main/java/com/example/spring_ftl/service', 'service'), 
        ('spring-ftl/src/main/resources/templates', 'templates'),
        ('spring-ftl/src/main/resources/scripts', 'scripts'),
        ('*.properties', '.')
    ],
    hiddenimports=['scripts'],
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
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
