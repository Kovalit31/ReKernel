import os
from os.path import isdir
import time
import platform
import string
import random
import re
from typing import Iterable

# ==============================================================
# #1 stackoverflow: https://stackoverflow.com/questions/3738381/what-do-i-do-when-i-need-a-self-referential-dictionary
# ==============================================================

class CallingDict(dict):
    """Returns the result rather than the value of referenced callables.

    >>> cd = CallingDict({1: "One", 2: "Two", 'fsh': "Fish",
    ...                   "rhyme": lambda d: ' '.join((d[1], d['fsh'],
    ...                                                d[2], d['fsh']))})
    >>> cd["rhyme"]
    'One Fish Two Fish'
    >>> cd[1] = 'Red'
    >>> cd[2] = 'Blue'
    >>> cd["rhyme"]
    'Red Fish Blue Fish'
    """
    def __getitem__(self, item):
        it = super(CallingDict, self).__getitem__(item)
        if callable(it):
            return it(self)
        else:
            return it

# ========================================
# pyright ignores this function at the EOF
# ========================================

def gen_uuid(length=20) -> str:
    """
    Generates uuid from digits and lowercase ascii letters
    """
    return "".join(
        random.choices([*(string.ascii_lowercase + string.digits)], k=length)
    )

# ============================
# Usage #1 of #1 stackoverflow
# ============================

definitions = CallingDict(
        {
            "default_path_global_log": os.path.join("/", "tmp", "build.py-{}.log".format(gen_uuid())),
            "default_path_base": os.path.dirname(__file__),
            "global_log": lambda d: LogFile(d["default_path_global_log"]),
            "debug": False,
            "verbose": False,
            "arch_regex": ["i.86/x86", "x86_64/x86_64", "sun4u/sparc64", "arm.*/arm", "sa110/arm", "s390x/s390", "ppc.*/powerpc", "mips.*/mips", "sh[234].*/sh", "aarch64.*/arm64", "riscv.*/riscv", "loongarch.*/loongarch"],
            "arch_support": lambda d: os.listdir(os.path.join(d["default_path_base"], "config", "arches")),
            
        }
    )

# ========================
#       Base objects
# ========================

# =============
# Got from Rust
# =============

class Result():
    def __init__(self, ok: Iterable = [], e=None) -> None:
        self.result = "ok" if e is None else "err"
        self.ok_data = [*ok]
        self.e_data = e

    def is_ok(self) -> bool:
        return self.result == "ok"

    def is_err(self) -> bool:
        return self.result == "err"

    def unwrap(self) -> None:
        if self.is_err():
            raise self.e_data

class Option():
    def __init__(self) -> None:
        pass

class File:
    '''
    File class
    '''
    def __init__(self, path: str) -> None:
        self.path = path
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        if not os.path.exists(self.path):
            self.clear()
        if os.path.isdir(os.path.realpath(self.path)):
            printf("Path is dir, cannot use it as file!", level='f')
    
    def read(self) -> list:
        try:
            file = open(self.path, "r", encoding="utf-8")
            data = file.readlines()
            file.close()
            return data
        except:
            return []
    
    def write(self, data, append=True) -> None:
        try:
            file = open(self.path, "w" if not append else "a", encoding="utf-8")
            file.write("".join(data) if type(data) == list else data if type(data) == str else str(data))
            file.close()
        except:
            return
    
    def remove(self) -> None:
        os.remove(self.path)
        del(self)
    
    def clear(self) -> None:
        self.write("", append=False)


class LogFile(File):
    '''
    Logging file implementation, based on File class.
    '''
    def __init__(self, path: str, parent=None) -> None:
        super().__init__(path)
        self.have_parent = parent != None
        self.parent = parent
        if type(parent) != type(self) and parent != None:
            printf(f"Parent log is not a LogFile object!", level='f')

    def read_log(self) -> str:
        return "".join(self.read()).rstrip()

    def write_log(self, data: str) -> None:
        self.write(f'\n[{time.strftime("%Y-%m-%d %H:%M:%S")} ({time.process_time()} from start)] ' + data.replace("\n\n", "\n").rstrip().replace("\n", f'\n[{time.strftime("%Y-%m-%d %H:%M:%S")} ({time.process_time()} from start)] '))

    def save_to_parent(self, prevscr: str = "") -> None:
        self.parent.write_log(f'Output of {"previous script" if prevscr == None else prevscr}:\n{self.read_log()}') if self.parent is not None else do_nothing()


# ==========================
#       Base functions
# ==========================

def check_sys() -> bool:
    return platform.system().lower().startswith('linux')

def get_arch() -> str:
    arch = platform.machine()
    for x in definitions["arch_regex"]:
        pattern, repl = x.split("/")
        arch = re.sub(pattern, repl, arch)
    return arch

def printf(*message, level="i", global_log: LogFile=definitions["global_log"]):
    '''
    Formats message with level.
    Exit, when fatal. Like in customcmd.
    @param string (str): Output string
    @param level (str): Info level ([d]ebug|[v]erbose|[i]nfo|[e]rror|[w]arning|[f]atal) (Default: i)
    '''
    string = " ".join(message)
    _level = level[0].lower().strip()
    if _level == 'd' and not definitions["debug"]:
        return
    if _level == 'v' and not definitions["verbose"]:
        return
    msg = f"[{'*' if _level == 'i' else '!' if _level == 'w' else '@' if _level == 'e' else '~' if _level == 'd' else '.' if _level == 'v' else '&' if _level == 'f' else '?'}] {string}".replace("\n", "\n[`] ")
    print(msg)
    global_log.write_log(msg)
    if _level == 'f':
        if not definitions["verbose"]:
            exit(2)
        raise Exception(string)

def do_nothing() -> None:
    '''
    Do nothing
    '''
    pass

# =========================
#       Config reader
# =========================

class ArchSpecific():
    '''
    Setups arch-specific command queue (line, sorry americans)
    '''
    def __init__(self) -> None:
        self.queue = []
    
    def copy(self, command_pointer: int) -> Result:
        if command_pointer > len(self.queue) - 1:
            return Result(e=Exception("Command pointer too big!"))
        data = self.parse(self.queue[command_pointer])
        _, *files = data
        destination, sources = files[-1], files[:-1]
        if not os.path.isdir(destination) and len(sources) > 1:
            return Result(e=Exception("Destination not dir, can't overwrite files!"))
        if len(sources) < 1:
            return Result(e=Exception("Haven't got destination!"))
        return Result()

    @staticmethod
    def parse(data) -> list[str]:
        return [data]

# ======================
#   Main functionality
# ======================

