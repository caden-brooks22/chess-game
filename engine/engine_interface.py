import ctypes
from pathlib import Path
from ctypes import c_char_p, c_bool, c_uint

ROOT_DIR = Path(__file__).resolve().parents[1]
ENGINE_DLL = ROOT_DIR / "build" / "Release" / "engine.dll"

# Load DLL from the repo root so it works regardless of the current working directory.
engine = ctypes.CDLL(str(ENGINE_DLL))

# Set argument and return types
engine.find_best_move.argtypes = [c_char_p, c_bool, c_uint]
engine.find_best_move.restype = c_char_p

# # Call C function
# input_str = "Hello from Python"
# result = engine.find_best_move(input_str.encode('utf-8'), 10000).decode('utf-8')

# # Decode and print result
# print(result)