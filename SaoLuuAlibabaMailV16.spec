# -*- mode: python ; coding: utf-8 -*-
# Portable single-file Windows executable (Python runtime included).
a = Analysis(
    ['app.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=['mail_backend', 'kiem_tra', 'usage_stats', 'issue_journal', 'network_manager', 'infra_manager', 'infra_ui', 'pmc_ui', 'pmc_manager', 'pmc_advanced', 'mail_quota', 'quota_ui', 'lan_discovery', 'auth_local', 'auth_ui', 'dashboard_widgets', 'dashboard_layout', 'industrial_theme', 'factory_catalog', 'factory_schema', 'factory_core', 'factory_ui', 'psutil', 'openpyxl'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pandas', 'numpy', 'matplotlib'],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, a.binaries, a.datas, [],
    name='AlibabaOperationsCenter',
    debug=False, bootloader_ignore_signals=False,
    strip=False, upx=False,
    console=False,
)
