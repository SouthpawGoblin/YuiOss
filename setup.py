import sys
from yui import VERSION
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["optparse"], "excludes": []}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
# if sys.platform == "win32":
#     base = "Win32GUI"

setup(name="yui",
      version=VERSION,
      description="Yui OSS console application",
      options={"build_exe": build_exe_options},
      executables=[Executable("yui.py", base=base)])
