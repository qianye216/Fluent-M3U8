import os
import sys
from app.common.setting import VERSION

if sys.platform == "win32":
    args = [
        'nuitka',
        '--standalone',
        # '--windows-disable-console',
        '--plugin-enable=pyside6' ,
        '--msvc=latest',
        '--show-memory' ,
        '--show-progress' ,
        '--include-qt-plugins=sensible,sqldrivers',
        '--windows-icon-from-ico=app/resource/images/logo.ico',
        '--output-dir=dist/Fluent-M3U8',
        'Fluent-M3U8.py',
    ]
elif sys.platform == "darwin":
    args = [
        'python3 -m nuitka',
        '--standalone',
        '--plugin-enable=pyside6',
        '--include-qt-plugins=sensible,sqldrivers',
        '--show-memory',
        '--show-progress',
        "--macos-create-app-bundle",
        "--assume-yes-for-download",
        "--macos-disable-console",
        f"--macos-app-version={VERSION}",
        "--macos-app-name=Fluent-M3U8",
        "--macos-app-icon=app/resource/images/logo.icns",
        "--copyright=zhiyiYo",
        '--output-dir=dist/Fluent-M3U8',
        'Fluent-M3U8.py',
    ]

os.system(' '.join(args))

