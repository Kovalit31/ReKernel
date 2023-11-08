#!/usr/bin/env python3
import os
import time
import platform
import string
import random
import re
import shutil
from typing import Callable, Iterable

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
global definitions

definitions = CallingDict(
        {   
            "default_path_global_log_name": f"build.py-{gen_uuid()}.log",
            "default_path_global_log_path": os.path.join("/", "tmp"),
            "default_path_global_log": lambda d: os.path.join(d["default_path_global_log_path"], d["default_path_global_log_name"]),
            "default_path_base": os.path.dirname(__file__),
            "global_log": lambda d: LogFile(d["default_path_global_log"]),
            "debug": False,
            "verbose": False,
            "arch_regex": ["i.86/x86", "x86_64/x86_64", "sun4u/sparc64", "arm.*/arm", "sa110/arm", "s390x/s390", "ppc.*/powerpc", "mips.*/mips", "sh[234].*/sh", "aarch64.*/arm64", "riscv.*/riscv", "loongarch.*/loongarch"],
            "default_path_arch_support": lambda d: os.path.join(d["default_path_base"], "configs", "arch"),
            "arch_support": lambda d: os.listdir(d["default_path_arch_support"])            
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
            printf(str(self.e_data), level='f')

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
        self.parent.write_log(f'Output of {"previous script" if len(prevscr) == 0 else prevscr}:\n{self.read_log()}') if self.parent is not None else do_nothing()

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
        printf(string, level='f')

def do_nothing() -> None:
    '''
    Do nothing
    '''
    pass

# =========================
#       Config reader
# =========================

class ConfigRead():
    '''
    Setups arch-specific command queue (line, sorry americans)
    '''
    def __init__(self, file: str) -> None:
        self.file = File(file)
        self.queue = []
        self.command_registry = {
            "copy": self.copy,
            "echo": self.echo,
            "mkdir": self.mkdir,
            "move": self.move,
            "build": self.build,
        }
        self.preparse()
    
    def build(self, command_pointer: int) -> Result:
        return Result()

    def move(self, command_pointer: int) -> Result:
        data = self.parse(self.queue[command_pointer][1])
        destination, sources = data[-1], data[:-1]
        self._fs_io_check(sources, destination).unwrap()
        for x in sources:
            try:
                self._fs_io_real(x, destination, shutil.move, shutil.move)
            except Exception as e:
                return Result(e=e)
        return Result()

    def mkdir(self, command_pointer: int) -> Result:
        data = self.parse(self.queue[command_pointer][1])
        for x in data:
            try:
                os.makedirs(x, exist_ok=True)
            except Exception as e:
                return Result(e=e)
        return Result()

    def echo(self, command_pointer: int) -> Result:
        data = self.parse(self.queue[command_pointer][1])
        print(" ".join(data))
        return Result()

    def copy(self, command_pointer: int) -> Result:
        data = self.parse(self.queue[command_pointer][1])
        destination, sources = data[-1], data[:-1]
        self._fs_io_check(sources, destination).unwrap()
        for x in sources:
            try:    
                self._fs_io_real(x, destination, shutil.copytree, shutil.copyfile)
            except Exception as e:
                return Result(e=e)
        return Result()
    
    def run(self) -> None:
        if len(self.queue) < 1:
            return # Do nothing
        for x in range(len(self.queue)):
            command = self.queue[x][0]
            try:
                self.command_registry[command](x).unwrap()
            except KeyError:
                printf(f"Unresolved command: {command}", level="e")

    def preparse(self) -> None:
        lines = self.file.read()
        for x in lines:
            if x.strip() == "":
                continue
            command, data = x.strip().split(" ", maxsplit=1)
            self.queue.append([command.lower(), data])
    
    @staticmethod
    def _fs_io_check(src: list[str], dst: str) -> Result:
        if not os.path.isdir(dst) and len(src) > 1:
            return Result(e=Exception("Destination is not dir, cannot overwrite files!"))
        if len(src) < 1:
            return Result(e=Exception("Destination is not set!"))
        return Result()

    @staticmethod
    def _fs_io_real(src: str, dst: str, src_dir_hand: Callable, src_oth_hand: Callable) -> None:
        if os.path.isdir(dst):
            dst = os.path.join(dst, os.path.basename(src))
        if os.path.isdir(src):
            src_dir_hand(src, dst)
        else:
            src_oth_hand(src, dst)
        return

    @staticmethod
    def parse(data: str) -> list[str]:
        letters = {token: "LETTER" for token in string.ascii_letters}
        numbers = {token: "NUMBER" for token in string.digits}
        punc = {token: "PUNCTUATION" for token in string.punctuation}
        replace = {
            "\\": "BACKSLASH",
            "#": "COMMENT",
            "\'": "QUOTA",
            "\"": "DOUBLE_QUOTA",
            "?": "VARIABLE",
            "(": "PARENTESS_LEFT",
            ")": "PARENTESS_RIGHT",
            "-": "DASH",
            " ": "WHITESPACE"
        }
        _tokens = {}
        _tokens.update(letters)
        _tokens.update(numbers)
        _tokens.update(punc)
        _tokens.update(replace)
        # tokens: [[token, value]]
        tokens = []
        for pos, x in enumerate(data):
            try:
                tokens.append([_tokens[x], x])
            except KeyError:
                printf(f"Unknown symbol '{x}' at {pos}")
        return tokens

# ======================
#   Main functionality
# ======================

def argparse():
    # TODO Implement arg parser
    pass

def main(args: list = []) -> None:
    if not get_arch() in definitions["arch_support"]:
        printf("Arch not supported yet!", level="f")
    arch = ConfigRead(os.path.join(definitions["default_path_arch_support"], get_arch()))
#    arch.run()

if __name__ == "__main__":
    main()
#arch = ArchSpecific()
#arch.run()
