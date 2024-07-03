import os
from cx_Freeze import setup, Executable

serial_data = os.environ.get('SERIAL', '')

buildOptions = {
    "packages": [
        'requests', 'time', 'subprocess', 'tkinter', 'os', 'sys', 're', 'uuid', 'queue', 'socketio'
    ],
    "excludes": [
        ""
    ]
}

exe = [Executable(f'auto40_{serial_data}.py', base='Win32GUI', icon='favicon.ico')]

setup(
    name='pattern auto',
    version='3.0',
    author='me',
    options=dict(build_exe=buildOptions),
    executables=exe
)