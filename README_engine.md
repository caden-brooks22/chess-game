# Engine

This documents the C++ DLL side of the project and the Python bridge that loads it.

## Overview

The DLL exposes a `find_best_move` entry point and is loaded from Python by [engine/engine_interface.py](engine/engine_interface.py).

## Build

Build the DLL from the repository root with:

```powershell
cmake --build build --config Release
```

If you need to recreate the build directory, use:

```powershell
cmake -S C_engine -B build
cmake --build build --config Release
```

## Python Bridge

The Python loader currently configures the DLL function with this signature:

- input: `const char*`
- color flag: `bool`
- time limit: `unsigned int`
