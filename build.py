#!/usr/bin/env python3
import os
import time
import platform
import string
import random
import re
import shutil
import json
import subprocess
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
            "debug": True,
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

class Err(Exception):
    pass

class Result():
    def __init__(self, data) -> None:
        self.result = True
        if isinstance(data, Iterable):
            self.data = (data)
        elif isinstance(data, Exception):
            self.data = Err(str(data))
            self.result = False
        else:
            self.data = ([data])

    def is_ok(self) -> bool:
        return self.result

    def is_err(self) -> bool:
        return not self.result

    def unwrap(self) -> object:
        if self.is_err():
            printf(str(self.data), level='f')
        return self.data[0]

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
#       Decorators
# ==========================

def debug_func(wrap: Callable) -> Callable:
    def wrapper(*args, **kwargs) -> object:
        if not definitions["debug"]:
            return None
        return wrap(*args, **kwargs)
    return wrapper

# ==========================
#       Base functions
# ==========================

@debug_func
def clever_out(data) -> Result:
    try:
        printf(json.dumps(data, indent=4), level='d')
        return Result(True)
    except Exception as e:
        return Result(e)

def parse_at(data, nums) -> Result:
    parsed = data
    for x in nums:
        parsed = parsed[x]
    return Result(parsed)

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

def strip_clean(data: list[str]) -> list[str]:
    to_pop = []
    out = data
    for pos, x in enumerate(data):
        if len(x.strip()) == 0:
            to_pop.append(pos - len(to_pop))
    for y in to_pop:
        out.pop(y)
    return out

def do_nothing() -> None:
    '''
    Do nothing
    '''
    pass

def pass_result(*args) -> Result:
    return Result(True)

def execute(cmd: str) -> int:
    """
    Wrap around os.system()
    """
    code = os.system(f"/bin/bash -c '{cmd}'")
    code = code >> 8
    return code

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
            "check_cmd": self.check_cmd,
            "run": self.run_cmd,
        }
        self.variables = {
            "workdir": definitions["default_path_base"],
            "filename": os.path.basename(file)
        }
        self.parse()
    
    def build(self, command_pointer: int) -> Result:
        return Result(True)

    def check_cmd(self, command_pointer: int) -> Result:
        data = self.queue[command_pointer][1]
        for x in data:
            if shutil.which(x) is None:
                return Result(Exception(f"No command {x} found at {command_pointer}"))
        return Result(True)

    def run_cmd(self, command_pointer: int) -> Result:
        data = " ".join(self.queue[command_pointer][1])
        code = execute(data)
        if code == 0:
            return Result(True)
        return Result(Exception(f"Command ended with code {code}!"))

    def move(self, command_pointer: int) -> Result:
        data = self.queue[command_pointer][1]
        destination, sources = data[-1], data[:-1]
        self._fs_io_check(sources, destination).unwrap()
        for x in sources:
            try:
                self._fs_io_real(x, destination, shutil.move, shutil.move)
            except Exception as e:
                return Result(e)
        return Result(True)

    def mkdir(self, command_pointer: int) -> Result:
        data = self.queue[command_pointer][1]
        for x in data:
            try:
                os.makedirs(x, exist_ok=True)
            except Exception as e:
                return Result(e)
        return Result(True)

    def echo(self, command_pointer: int) -> Result:
        data = self.queue[command_pointer][1]
        print(" ".join(data))
        return Result(True)

    def copy(self, command_pointer: int) -> Result:
        data = self.queue[command_pointer][1]
        destination, sources = data[-1], data[:-1]
        self._fs_io_check(sources, destination).unwrap()
        for x in sources:
            try:    
                self._fs_io_real(x, destination, shutil.copytree, shutil.copyfile)
            except Exception as e:
                return Result(e)
        return Result(True)
    
    def run(self) -> None:
        if len(self.queue) < 1:
            return # Do nothing
        ign_count = 0 # It ignores upcoming commands
        for pos, x in enumerate(self.queue):
            if ign_count > 0:
                ign_count -= 1
                continue
            data = {
                "not_fatal": False,
                "no_message": False,
                "ignore": 0,
                "error_message": ""
            }
            try:
                wait_next = False
                section = ""
                result = self.command_registry[x[0]](pos)
                mods = x[2]
                printf(f"Mods: {mods}")
                printf(f"Result Ok: {result.is_ok()}")
                for m_pos, mod in enumerate(mods):
                    if mod == "ignore":
                        wait_next = True
                        section = mod
                    elif mod == "%":
                        wait_next = True
                        section = "error_message"
                    elif wait_next:
                        data[section] = mod
                    else:
                        try:
                            _ = data[mod]
                            data[mod] = True
                        except KeyError:
                            printf(f"Unknown mod at {m_pos}", level='e')
                ign_count = int(data["ignore"])
                ok = result.is_ok()
                if ok:
                    continue
                else:
                    error = str(result.data)
                    ign_count = 0
                    if len(data["error_message"]) > 0:
                        error = data["error_message"]
                    if data["no_message"]:
                        error = None
                    if data["not_fatal"]:
                        continue
                    if error is not None:
                        printf(error, level='f')
            except KeyError:
                printf(f"Unresolved command: {x[0]}", level="e")
    
    @staticmethod
    def _fs_io_check(src: list[str], dst: str) -> Result:
        if not os.path.isdir(dst) and len(src) > 1:
            return Result(Exception("Destination is not dir, cannot overwrite files!"))
        if len(src) < 1:
            return Result(Exception("Destination is not set!"))
        return Result(True)

    @staticmethod
    def _fs_io_real(src: str, dst: str, src_dir_hand: Callable, src_oth_hand: Callable) -> None:
        if os.path.isdir(dst):
            dst = os.path.join(dst, os.path.basename(src))
        if os.path.isdir(src):
            src_dir_hand(src, dst)
        else:
            src_oth_hand(src, dst)
        return
    
    def parse(self) -> None:
        data = "".join(self.file.read())
        tokens = self.lex(data)
        splitted = self.gen_instructions(tokens, variables=self.variables)
        clever_out(splitted)
        out = []
        for command in splitted:
            out.append([command[0][0], command[0][1:],command[1]])
        self.queue = out

    @staticmethod
    def gen_instructions(tokens: list[list[str]], variables: dict = {}) -> list[list[list[str]]]:
        out = [[[""], [""]]]
        write_to = 0
        dash = False
        skipped = False
        put = True
        quotes = False
        double = False
        nline_ignore = False
        variable = False
        variable_data = ""
        for pos, x in enumerate(tokens):
            if nline_ignore:
                put = False
            if not pos == 0:
                if put:
                    if not variable:
                        out[-1][write_to][-1] += tokens[pos-1][1]
                    else:
                        variable_data += tokens[pos-1][1]
                put = True
            if x[0] == "DASH":
                if skipped:
                    skipped = False
                    continue
                if quotes:
                    continue
                if variable:
                    continue
                put = False
                if dash == True:
                    write_to = (write_to + 1) % 2
                    dash = False
                    continue
                dash = True
                continue
            if x[0] == "BACKSLASH":
                if skipped:
                    skipped = False
                    continue
                put = False
                skipped = True
                continue
            if x[0] == "NLINE":
                if skipped:
                    skipped = False
                    continue
                put = False
                if variable:
                    variable = False
                    out[-1][write_to][-1] += variable_data
                if nline_ignore:
                    nline_ignore = False
                    continue
#                if len(tokens[-1][0]+tokens[-1][1]) > pos+1 and len(tokens) - 1 > pos:
                out[-1][0] = strip_clean(out[-1][0])
                out[-1][1] = strip_clean(out[-1][1])
                if len(out[-1][0]+out[-1][1]) == 0:
                    out.pop()
                out.append([[""], [""]])
                write_to = 0
                continue
            if x[0] == "QUOTA":
                if skipped:
                    skipped = False
                    continue
                if variable:
                    variable = False
                    out[-1][write_to][-1] += variable_data
                put = False
                if quotes:
                    if double:
                        put = True
                        continue
                    quotes = False
                    continue
                quotes = True
                continue
            if x[0] == "DOUBLE_QUOTA":
                if skipped:
                    skipped = False
                    continue
                if variable:
                    variable = False
                    out[-1][write_to][-1] += variable_data
                put = False
                if quotes:
                    if not double:
                        put = True
                        continue
                    quotes = False
                    double = False
                    continue
                quotes = True
                double = True
                continue
            if x[0] == "COMMENT":
                if not (skipped or quotes):
                    if skipped:
                        skipped = False
                    nline_ignore = True
                if variable:
                    variable = False
                    out[-1][write_to][-1] += variable_data
                continue
            if x[0] == "WHITESPACE":
                if skipped or quotes:
                    if skipped:
                        skipped = False
                    continue
                if len(out[-1][write_to][-1]) > 0:
                    out[-1][write_to].append("")
                if variable:
                    variable = False
                    out[-1][write_to][-1] += variable_data
                put = False
                continue
            if x[0] == "VARIABLE":
                if quotes and not double:
                    continue
                if skipped:
                    continue
                put = False
                if variable:
                    try:
                        out[-1][write_to][-1] += variables[variable_data]
                    except:
                        printf(f"Unknown variable at {pos}", level='d')
                    variable = False
                    variable_data = ""
                    continue
                variable = True
                continue
            if dash:
                if variable:
                    variable_data += "-"
                else:
                    out[-1][write_to][-1] += "-"
                dash = False
        real_out = []
        for pos, y in enumerate(out):
            if not len("".join(y[0]+y[1])) == 0:
                real_out.append(y)
        return real_out

    @staticmethod
    def lex(data: str) -> list[list[str]]:
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
            " ": "WHITESPACE",
            "\n": "NLINE",
            ";": "NLINE",
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
    arch.run()

if __name__ == "__main__":
    main()
#arch = ArchSpecific()
#arch.run()
