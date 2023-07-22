#!/usr/bin/env python3
import selectors
import signal
import sys
import os
import shutil
import termios
import time
import pty
import platform
from argparse import ArgumentParser

# Versions
MAJOR_VER = 0
MINOR_VER = 1
PATCH_LEVEL = 2
EXTRA = "alpha"
VERSION = ".".join([str(x) for x in [MAJOR_VER, MINOR_VER, PATCH_LEVEL]])+(f"-{EXTRA}" if EXTRA != None else "")

# Runtime folders
BASE_DIR = os.path.dirname(__file__)
SCRIPT_DIR = os.path.join(BASE_DIR, "scripts")

# Supported targets/archs

TARGETS = ["clean", "efi", "bios", "legacy"]
ARCHS = ["x86_64"]

DEFAULT_TARGET = 3
DEFAULT_ARCH = 0 # TODO Create func, what detects arch

class ExecutingInterrupt:
    '''
    Configurable script interrupt handler
    '''
    
    def __init__(self, exit_msg=None, exit=True) -> None:
        self.interrupt = False
    
    def _handler(self, signum, frame) -> None:
        self.interrupt = True
        self.signal = signum
        self.frame = frame
    
    def __enter__(self) -> None:
        self.old_sigint = signal.signal(signal.SIGINT, self._handler)
        self.old_sigterm = signal.signal(signal.SIGTERM, self._handler)
        return self
    
    def __exit__(self, type, value, traceback) -> None:
        signal.signal(signal.SIGINT, self.old_sigint)
        signal.signal(signal.SIGTERM, self.old_sigterm)

class LogFile:
    def __init__(self, file: str, parent=None) -> None:
        self.file = file
        self.have_parent = parent != None
        self.parent = parent
        if not check_dir(os.path.dirname(file)):
            create_dir(os.path.dirname(file))
        if not check_path(file):
            create_file(file)
            self.clear()
        if not check_file(file):
            printf(f"Given path '{file}' is not a file!", level='f')
        if type(parent) != type(self) and parent != None:
            printf(f"Parent log is not a LogFile object!", level='f')

    def read(self) -> str:
        return "".join(read(self.file)).rstrip()

    def write(self, data: str) -> None:
        write(self.file, f'\n[{time.strftime("%Y-%m-%d %H:%M:%S")} ({time.process_time()} from start)] ' + data.replace("\n\n", "\n").rstrip().replace("\n", f'\n[{time.strftime("%Y-%m-%d %H:%M:%S")} ({time.process_time()} from start)] '), append=True)

    def clear(self) -> None:
        write(self.file, "# START OF LOGGING\n", append=False)

    def save_to_parent(self, prevscr: str = None) -> None:
        self.parent.write(f'Output of {"previous script" if prevscr == None else prevscr}:\n{self.read()}') if self.have_parent else do_nothing()

    def remove(self) -> None:
        remove(self.path)
        del(self)

class RecipeNode:
    def __init__(self, script: str, args: str, exit_msg: str = None) -> None:
        self.script = script
        self.args = args
        self.exit = exit_msg
    
    def execute(self, plus_args: str = None) -> None:
        return execute(self.script, args = self.args if plus_args == None else self.args + plus_args if self.args != None else plus_args, exit_msg = self.exit)

class Recipes:
    def __init__(self) -> None:
        self.recipes = dict()
    
    def load_recipe(self, recipe: RecipeNode, group: str) -> int:
        '''
        Loads recipe type RecipeNode and return index in group
        '''
        self.recipes[group].append(recipe) if group in (lambda diction: [ x for x in diction.keys() ])(self.recipes) else self.recipes.update({group: [recipe]})
        return self.recipes[group].index(recipe)
    
    def unload_recipe(self, group: str, index: int) -> None:
        if not group in (lambda diction: [ x for x in diction.keys() ])(self.recipes):
            return
        self.recipes[group].pop(index)
        if len(self.recipes[group]) == 0:
            self.recipes.pop(group)

    def get_recipes(self) -> list[str]:
        return (lambda diction: [ x for x in diction.keys() ])(self.recipes)
    
    def get_recipe_group(self, group: str) -> list[RecipeNode]:
        if not group in (lambda diction: [ x for x in diction.keys() ])(self.recipes):
            return []
        return self.recipes[group]
    
# Thanks for inputimeout project
class TimeoutOccurred(Exception):
    pass

def _raw_print(string):
    sys.stdout.write(string)
    sys.stdout.flush()

def posix_inputimeout(prompt='', timeout=30):
    _raw_print(prompt)
    sel = selectors.DefaultSelector()
    sel.register(sys.stdin, selectors.EVENT_READ)
    events = sel.select(timeout)

    if events:
        key, _ = events[0]
        return key.fileobj.readline().rstrip("\n")
    else:
        _raw_print("\n")
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
        raise TimeoutOccurred()

# END

def debug_executor(executor):
    def wrap(*args, **kwargs):
        if DEBUG:
            try:
                _input = posix_inputimeout(prompt=f"Executor console is ACTIVE\nYou can debug executor with your own commands.\nPress ENTER on {INPUT_TIMEOUT} seconds or skip to continue...", timeout=INPUT_TIMEOUT)
            except TimeoutOccurred:
                _input = None
            if _input != None:
                printf("Now you will get a console. Type 'exit' when done.")
                pty.spawn("/bin/bash")
                while True:
                    _exec = input(f"Execute executor with args {args} {kwargs}? [y/n] ")
                    if _exec == None or _exec == "":
                        _exec = " "
                    break
                if _exec[0].lower() == 'n':
                    return
        return executor(*args, **kwargs)
    return wrap

def do_nothing() -> None:
    pass

def check_sys() -> bool:
    return platform.system().lower().startswith('linux')

def printf(*message, level="i"):
    '''
    Formats message with level.
    Exit, when fatal. Like in customcmd.
    @param string (str): Output string
    @param level (str): Info level ([d]ebug|[v]erbose|[i]nfo|[e]rror|[w]arning|[f]atal) (Default: i)
    '''
    string = " ".join(message)
    _level = level[0].lower().strip()
    if _level == 'd' and not DEBUG:
        return
    if _level == 'v' and not VERBOSE:
        return
    msg = f"[{'*' if _level == 'i' else '!' if _level == 'w' else '@' if _level == 'e' else '~' if _level == 'd' else '.' if _level == 'v' else '&' if _level == 'f' else '?'}] {string}".replace("\n", "\n[`] ")
    print(msg)
    GLOBAL_LOG.write(msg)
    if _level == 'f':
        raise Exception(string)

# Check paths
def check_path(path: str) -> bool:
    return os.path.exists(path)

def check_dir(path: str) -> bool:
    if not check_path(path):
        return False
    if not os.path.isdir(os.path.realpath(path)):
        return False
    return True

def check_file(path) -> bool:
    if not check_path(path):
        return False
    if not os.path.isfile(os.path.realpath(path)):
        return False
    return True

# rm*
def remove(path: str, recursive=False) -> None:
    if check_dir(path) and not recursive:
        printf(f"Ommiting {path} because not recursive deletion", level='w')
        return
    if not check_path(path):
        printf(f"Path not exists: {path}", level='e')
        return
    if not recursive and not check_dir(path):
        if os.path.islink(path):
            os.unlink(path)
        else:
            os.remove(path)
    else:
        shutil.rmtree(path)

# Create file/dir
def create_file(path: str) -> None:
    if check_dir(path):
        remove(path, recursive=True)
    if check_file(path):
        return
    try:
        file = open(path, "x", encoding="utf-8")
        file.close()
    except:
        return

def create_dir(path: str) -> None:
    if check_file(path):
        remove(path)
    if check_dir(path):
        return
    os.makedirs(path)

# File I/O
def write(path: str, data: str, append=False) -> None:
    try:
        create_file(path)
        file = open(path, "w" if not append else "a", encoding="utf-8")
        file.write(data)
        file.close()
    except:
        return

def read(path: str) -> list:
    try:
        file = open(path, "r", encoding="utf-8")
        data = file.readlines()
        file.close()
        return data
    except:
        return ""

@debug_executor
def execute(script: str, args="", exit_msg=None):
    '''
    Runner of scripts under scripts folder.
    If script fails, it might to kill parent (this script) by $1 argument
    Basedir can be accessed by $2.
    Logging file is on $3 argument.
    '''
    script = os.path.join(SCRIPT_DIR, f"{script}.sh")
    if not os.path.exists(script):
        raise Exception(f"No script found {script}")
    with ExecutingInterrupt() as ei:
        os.system(f"chmod 755 {script}")
        os.system(f"\"{script}\" {os.getpid()} \"{BASE_DIR}\" \"{SCRIPT_LOG.file}\" {'' if args == None else args if type(args) != list else ' '.join(args)}")
        interrupt = ei.interrupt
    SCRIPT_LOG.save_to_parent(prevscr=script)
    logs = SCRIPT_LOG.read()
    SCRIPT_LOG.clear()
    if interrupt:
        printf(f"Error occured at {script}\n{logs}" if exit_msg == None else exit_msg, level='f')

def arg_parse():
    parser =  ArgumentParser(description="Build system for UnOS kernel", epilog="Under GNU v3 Public license. UnOS is not new OS, it is Linux rewrite to Rust")
    parser.add_argument("target", help="Build terget (clean will clear logs and data)", metavar="TARGET", nargs="?", default=TARGETS[DEFAULT_TARGET], choices=TARGETS)
    parser.add_argument("-v", "--verbose", help="Be verbose", action="store_true")
    parser.add_argument("-d", "--debug", help="Switch into debug configuration", action='store_true')
    parser.add_argument('-n', "--norun", help="Don't run after build", action='store_true')
    parser.add_argument("--timeout", help="Timeout for input (for debug console)", type=int, default=5, metavar="TIMEOUT")
    parser.add_argument("--logdir", help="Logging directory", type=str, metavar="LOGDIR", default=os.path.join(BASE_DIR, "logs"))
    parser.add_argument("-a", "--arch", help="Build for ARCH", default=ARCHS[DEFAULT_ARCH], choices=ARCHS, metavar="ARCH")
    args = parser.parse_args()
    return args

def recipe_runner(recipe_list: list[RecipeNode]):
    for x in recipe_list:
        x.execute()

if __name__ != "__main__":
    exit()

args = arg_parse()
logdir = args.logdir

global DEBUG
global VERBOSE
global INPUT_TIMEOUT
global GLOBAL_LOG
global SCRIPT_LOG

DEBUG = args.debug
VERBOSE = args.verbose
INPUT_TIMEOUT = args.timeout
GLOBAL_LOG = LogFile(os.path.join(logdir, f'{time.strftime("%Y-%m-%d %H:%M:%S")}.log'))
SCRIPT_LOG = LogFile(os.path.join(logdir, 'script_logger.log'), parent=GLOBAL_LOG)

if not check_sys() and not DEBUG:
    printf('Program can\'t be run on non-linux os!', level='f')

# Inititalize recipes
RECIPE_BUILD__PREPARE = RecipeNode("build/prepare", f"{args.arch} {args.target}")
RECIPE_BUILD__CLEAN = RecipeNode("build/clean", f"{logdir}")
RECIPE_BUILD__BUILD = RecipeNode("build/build", "release" if not DEBUG else "debug")
RECIPE_BUILD__RUN = RecipeNode("build/run", "release" if not DEBUG else "debug")
RECIPE_BUILD_SYS_INSTALL__RUSTUP = RecipeNode("build_sys_install/rustup", None)
RECIPE_BUILD_SYS_INSTALL__COMPONENTS = RecipeNode("build_sys_install/components", None)
RECIPE_BUILD_SYS_INSTALL__TOOLCHAIN = RecipeNode("build_sys_install/toolchain", f"{args.arch}")
RECIPE_CORE__CMD_CHK = RecipeNode("core/cmd_chk", None) # NOTE Use it with additional args
RECIPE_EXAMPLE = RecipeNode("example", None) # NOTE It's just a example

# Load recipes
recipes = Recipes()
recipes.load_recipe(RECIPE_BUILD__CLEAN, "clean")
recipes.load_recipe(RECIPE_BUILD__PREPARE, "build")
recipes.load_recipe(RECIPE_BUILD_SYS_INSTALL__RUSTUP, "build")
recipes.load_recipe(RECIPE_BUILD_SYS_INSTALL__TOOLCHAIN, "build")
recipes.load_recipe(RECIPE_BUILD_SYS_INSTALL__COMPONENTS, "build")
recipes.load_recipe(RECIPE_BUILD__BUILD, "build")
recipes.load_recipe(RECIPE_BUILD__RUN, "build") if not args.norun else do_nothing()

# Duplicate build group as base of other builds
for x in TARGETS:
    if x != "clean":
        recipes.recipes[x] = recipes.get_recipe_group("build")

recipe_runner(recipes.get_recipe_group(args.target))