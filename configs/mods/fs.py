import os
import shutil
import sys
from typing import Callable

# Get default functions
try:
    _build_py = sys.modules["build_py"]
except KeyError:
    raise Exception("build_py not found, exit!")

_ConfigRead = _build_py.ConfigRead
_Result = _build_py.Result

def touch(_: _ConfigRead, __: list) -> _Result:
    return _Result(True)

def ls(_: _ConfigRead, __: list) -> _Result:
    return _Result([]) # listdir()

def rm(_: _ConfigRead, __: list) -> _Result:
    return _Result(True)

def rmdir(_: _ConfigRead, __: list) -> _Result:
    return _Result(True)

def chmod_exec(_: _ConfigRead, command_data: list[str]) -> _Result:
    try:
        os.chmod(command_data[-1], 0o755)
        return _Result(True)
    except:
        return _Result(Exception("Can't chmod executable"))

#    def build(self, _: list[str]) -> Result:
#        return Result(True)

def mv(_: _ConfigRead, command_data: list[str]) -> _Result:
    destination, sources = command_data[-1], command_data[:-1]
    _fs_io_check(sources, destination).unwrap()
    for x in sources:
        try:
            _fs_io_real(x, destination, shutil.move, shutil.move)
        except Exception as e:
            return _Result(e)
    return _Result(True)

def mkdir(_: _ConfigRead, command_data: list[str]) -> _Result:
    for x in command_data:
        try:
            os.makedirs(x, exist_ok=True)
        except Exception as e:
           return _Result(e)
    return _Result(True)

def cp(_: _ConfigRead, command_data: list[str]) -> _Result:
    destination, sources = command_data[-1], command_data[:-1]
    _fs_io_check(sources, destination).unwrap()
    for x in sources:
        try:    
            _fs_io_real(x, destination, shutil.copytree, shutil.copyfile)
        except Exception as e:
            return _Result(e)
    return _Result(True)

def _fs_io_check(src: list[str], dst: str) -> _Result:
    if not os.path.isdir(dst) and len(src) > 1:
        return _Result(Exception("Destination is not dir, cannot overwrite files!"))
    if len(src) < 1:
        return _Result(Exception("Destination is not set!"))
    return _Result(True)

def _fs_io_real(src: str, dst: str, src_dir_hand: Callable, src_oth_hand: Callable) -> None:
    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    if os.path.isdir(src):
        src_dir_hand(src, dst)
    else:
        src_oth_hand(src, dst)
    return
