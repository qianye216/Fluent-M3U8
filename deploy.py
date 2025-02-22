import os
import sys
from app.common.setting import VERSION

if sys.platform == "win32":
    args = [
        'nuitka',
        '--standalone',
        '--windows-disable-console',
        '--plugin-enable=pyside6' ,
        '--include-qt-plugins=sensible,sqldrivers',
        '--assume-yes-for-downloads',
        # '--msvc=latest',              # Use MSVC
        '--mingw64',                    # Use MinGW
        '--show-memory' ,
        '--show-progress' ,
        '--windows-icon-from-ico=app/resource/images/logo.ico',
        # '--windows-company-name="Shokokawaii Inc."',
        # '--windows-product-name=Fluent-M3U8',
        f'--windows-file-version={VERSION}',
        f'--windows-product-version={VERSION}',
        '--windows-file-description="Fluent M3U8"',
        '--output-dir=dist',
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
        '--output-dir=dist',
        'Fluent-M3U8.py',
    ]
else:
    args = [
        'nuitka',
        '--standalone',
        '--plugin-enable=pyside6',
        '--include-qt-plugins=sensible,sqldrivers',
        '--assume-yes-for-downloads',
        '--show-memory',
        '--show-progress',
        '--linux-icon=app/resource/images/logo.ico',
        '--output-dir=dist',
        'Fluent-M3U8.py',
    ]


os.system(' '.join(args))

