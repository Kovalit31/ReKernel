#!/usr/bin/env python3
import os
import time
import platform
import string
import random
import re
import shutil
import json
#import subprocess
import argparse
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

class Err(Exception):
    pass

class Result():
    err_msg = None
    
    def __init__(self, data) -> None:
        self.result = True
        if isinstance(data, Exception):
            self.data = Err(str(data))
            self.err_msg = str(data)
            self.result = False
        else:
            self.data = (data, None)

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
        raise Exception(msg)

def strip_clean(data: list) -> list:
    to_pop = []
    out = data
    for pos, x in enumerate(data):
        if len(x.strip() if isinstance(x, str) else x) == 0:
            to_pop.append(pos - len(to_pop))
    for y in to_pop:
        out.pop(y)
    return out

def do_nothing() -> None:
    '''
    Do nothing
    '''
    pass

def pass_result(*_) -> Result:
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
            "chmod_exec": self.chmod_exec,
        }
        self.variables = {
            "workdir": definitions["default_path_base"],
            "filename": os.path.basename(file)
        }
        self.parse()
    
    def chmod_exec(self, command_data: list[str]) -> Result:
        try:
            os.chmod(command_data[-1], 0o755)
            return Result(True)
        except:
            return Result(Exception("Can't chmod executable"))

    def build(self, _: list[str]) -> Result:
        return Result(True)

    def check_cmd(self, command_data: list[str]) -> Result:
        for x in command_data:
            result = self.run_cmd([f"command -v {x}>/dev/null"])
            if result.is_err():
                return Result(Exception(f"No command {x} found "))
        return Result(True)

    def run_cmd(self, command_data: list[str]) -> Result:
        data = " ".join(command_data)
        code = execute(data)
        if code == 0:
            return Result(True)
        return Result(Exception(f"Command ended with code {code}!"))

    def move(self, command_data: list[str]) -> Result:
        destination, sources = command_data[-1], command_data[:-1]
        self._fs_io_check(sources, destination).unwrap()
        for x in sources:
            try:
                self._fs_io_real(x, destination, shutil.move, shutil.move)
            except Exception as e:
                return Result(e)
        return Result(True)

    def mkdir(self, command_data: list[str]) -> Result:
        for x in command_data:
            try:
                os.makedirs(x, exist_ok=True)
            except Exception as e:
                return Result(e)
        return Result(True)

    def echo(self, command_data: list[str]) -> Result:
        print(" ".join(command_data))
        return Result(True)

    def copy(self, command_data: list[str]) -> Result:
        destination, sources = command_data[-1], command_data[:-1]
        self._fs_io_check(sources, destination).unwrap()
        for x in sources:
            try:    
                self._fs_io_real(x, destination, shutil.copytree, shutil.copyfile)
            except Exception as e:
                return Result(e)
        return Result(True)

    def run(self, _cmd_list: list[list[list[list[str]]]] = None) -> Result:
        result = Result(True)
        queue = self.queue if _cmd_list is None else _cmd_list
        printf(f"Current queue: {queue}", level='d')
        if len(queue) < 1:
            return result # Do nothing
        ign_count = 0 # It ignores upcoming commands
        for _, x in enumerate(queue):
            if ign_count > 0:
                ign_count -= 1
                continue
            command_p = self.gen_command_data(x)
            ign_count, result = self._real_run(command_p)
        return result
    
    def _real_run(self, command_p: list) -> tuple[int, Result]:
        ign_count = 0
        result = Result(Exception("Can't run: unknown error"))
        data = {
            "not_fatal": False,
            "no_message": False,
            "ignore": 0,
            "error_message": ""
        }
        try:
            wait_next = False
            section = ""
            result = self.command_registry[command_p[0][0]](command_p[0][1:])
            mods = command_p[1]
            printf(f"Mods: {mods}", level='d')
            printf(f"Result Ok: {result.is_ok()}", level='d')
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
                return ign_count, result
            else:
                error = str(result.data)
                ign_count = 0
                if len(data["error_message"]) > 0:
                    error = data["error_message"]
                if data["no_message"]:
                    error = None
                if data["not_fatal"]:
                    return ign_count, result
                if error is not None:
                    printf(error, level='f')
        except KeyError:
            printf(f"Unresolved command: {' '.join(command_p[0])}", level="e")
        return ign_count, result
    
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
        pregenerated = self.pregen(tokens)
        self.queue = pregenerated
    
    def gen_command_data(self, command_pregen: list[list[list[str]]]) -> list[list[str]]:
        out = [[""], [""]]
        for p_pos, part in enumerate(command_pregen):
            for _, string in enumerate(part):
                if len(out[p_pos][-1]) != 0:
                    out[p_pos].append("")
                variable = False
                variable_data = ""
                for _, token in enumerate(string):
                    if token[0] == "VARIABLE":
                        if variable:
                            if variable_data.startswith("(") and variable_data.endswith(")"):
                                variable_data = variable_data.strip("()")
                                _cmd_list = self.pregen(self.lex(variable_data))
                                result = self.run(_cmd_list=_cmd_list)
                                data = result.unwrap() if result.is_ok() else result.err_msg
                                out[p_pos][-1] += data if isinstance(data, str) else " ".join(data) if isinstance(data, Iterable) else str(data) if isinstance(data, bool) else ""
                            else:
                                try:
                                    out[p_pos][-1] += self.variables[variable_data]
                                except KeyError:
                                    printf(f"Unknown variable {variable_data}", level='e')
                            variable = False
                            variable_data = ""
                            continue
                        variable = True
                        continue
                    if variable:
                        variable_data += token[1]
                        continue
                    out[p_pos][-1] += token[1]
            out[p_pos] = strip_clean(out[p_pos])
        return out

    @staticmethod
    def pregen(tokens: list[list[str]]) -> list[list[list[list[str]]]]:
        out = [[[[]], [[]]]]
        write_to = 0
        dash = False
        skipped = False
        put = True
        quotes = False
        double = False
        nline_ignore = False
        variable = False
        variable_data = []
        parentess = 0
        parentess_ignore = False
        latest_left = 0
        for pos, x in enumerate(tokens):
            if nline_ignore or parentess_ignore:
                put = False
            if not pos == 0:
                if put:
                    if not variable:
                        out[-1][write_to][-1].append(tokens[pos-1])
                    else:
                        variable_data.append(tokens[pos-1])
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
                if parentess:
                    continue
                put = False
                if variable:
                    variable = False
                    variable_data[0] = ["IGNORED_VARIABLE", "?"]
                    out[-1][write_to][-1] += variable_data
                    variable_data = []
                if nline_ignore:
                    nline_ignore = False
                    continue
#                if len(tokens[-1][0]+tokens[-1][1]) > pos+1 and len(tokens) - 1 > pos:
                out[-1][0] = strip_clean(out[-1][0])
                out[-1][1] = strip_clean(out[-1][1])
                if len(out[-1][0]+out[-1][1]) == 0:
                    out.pop()
                out.append([[[]], [[]]])
                write_to = 0
                continue
            if x[0] == "QUOTA":
                if skipped:
                    skipped = False
                    continue
                put = False
                if quotes:
                    if double:
                        put = True
                        continue
                    quotes = False
                    if variable:
                        if parentess:
                            continue
                        variable = False
                        variable_data[0] = ["IGNORED_VARIABLE", "?"]
                        out[-1][write_to][-1] += variable_data
                        variable_data = []
                    continue
                quotes = True
                continue
            if x[0] == "DOUBLE_QUOTA":
                if skipped:
                    skipped = False
                    continue
                put = False
                if quotes:
                    if not double:
                        put = True
                        continue
                    quotes = False
                    double = False
                    if variable:
                        if parentess:
                            continue
                        variable = False
                        variable_data[0] = ["IGNORED_VARIABLE", "?"]
                        out[-1][write_to][-1] += variable_data
                        variable_data = []
                    continue
                quotes = True
                double = True
                continue
            if x[0] == "COMMENT":
                if not (skipped or quotes):
                    if skipped:
                        skipped = False
                    if parentess:
                        parentess_ignore = True
                    else:
                        nline_ignore = True
                if variable:
                    if parentess:
                        continue
                    variable = False
                    variable_data[0] = ["IGNORED_VARIABLE", "?"]
                    out[-1][write_to][-1] += variable_data
                    variable_data = []
                continue
            if x[0] == "WHITESPACE":
                if skipped or quotes:
                    if skipped:
                        skipped = False
                    continue
                put = False
                if len(out[-1][write_to][-1]) > 0:
                    out[-1][write_to].append([])
                if variable:
                    if parentess:
                        continue
                    variable = False
                    variable_data[0] = ["IGNORED_VARIABLE", "?"]
                    out[-1][write_to][-1] += variable_data
                    variable_data = []
                continue
            if x[0] == "VARIABLE":
                if quotes and not double:
                    continue
                if skipped:
                    continue
                put = False
                if variable:
                    variable_data.append(["VARIABLE", "?"])
                    out[-1][write_to][-1] += variable_data
                    variable = False
                    variable_data = []
                    continue
                variable_data.append(["VARIABLE", "?"])
                variable = True
                continue
            if x[0] == "PUNCTUATION":
                if variable:
                    if parentess:
                        continue
                    variable = False
                    variable_data[0] = ["IGNORED_VARIABLE", "?"]
                    out[-1][write_to][-1] += variable_data
                    variable_data = []
                continue
            if x[0] == "PARENTESS_LEFT":
                latest_left = pos
                parentess += 1
                continue
            if x[0] == "PARENTESS_RIGHT":
                if parentess_ignore:
                    parentess_ignore = False
                    put = True
                if parentess == 0:
                    printf(f"Oops! You have unresolved parentess at {pos}", level='e')
                    continue
                parentess -= 1
                continue
            if dash:
                if variable:
                    variable_data.append(["PUNCTUATION", "-"])
                else:
                    out[-1][write_to][-1].append(["PUNCTUATION", "-"])
                dash = False
        if parentess > 0:
            printf("You have unterminated parentess at {latest_left}", level='e')
        real_out = []
        for pos, y in enumerate(out):
            if not len(strip_clean(y[0])) + len(strip_clean(y[1])) == 0:
                real_out.append(y)
        return out

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

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", help="Switch to debug mode", default=False, action="store_true")
    parser.add_argument("--verbose", help="Switch to verbose mode", default=False, action="store_true")
    return parser.parse_args()

def main(args: argparse.Namespace) -> None:
    if not get_arch() in definitions["arch_support"]:
        printf("Arch not supported yet!", level="f")
    definitions["debug"] = args.debug
    definitions["verbose"] = args.verbose
    arch = ConfigRead(os.path.join(definitions["default_path_arch_support"], get_arch()))
    arch.run()

if __name__ == "__main__":
    main(parse_args())
