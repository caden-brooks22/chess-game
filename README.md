# Chess GUI

This project runs the chess GUI from [main.py](main.py). The code has been reorganized into:

- [GUI/](GUI) for the Tkinter interface, board rendering, and assets
- [back_end/](back_end) for user and game data
- [engine/](engine) for the Python bridge to the compiled C++ engine

The GUI is able to utilize and interface the engine through [engine/engine_interface.py](engine/engine_interface.py).

## Setup

Create a virtual environment from the repository root:

```powershell
py -m venv .venv
```

Activate it in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, allow local scripts for your user account:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Install the Python requirements:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run The GUI

Start the application from the repository root:

```powershell
python main.py
```

The GUI loads images from [GUI/img/](GUI/img) and user data from [back_end/users.json](back_end/users.json), so run it from the repo root.

## Engine Notes

The compiled engine DLL is loaded from [build/Release/engine.dll](build/Release/engine.dll). The Python bridge uses an absolute path relative to [engine/engine_interface.py](engine/engine_interface.py), so it no longer depends on your current working directory.

To rebuild the DLL, use the existing CMake build in [build/](build):

```powershell
cmake --build build --config Release
```
