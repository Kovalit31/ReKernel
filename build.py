#!/usr/bin/env python3
import signal
import sys
import os
import shutil
import time
from argparse import ArgumentParser

DEBUG = False
VERBOSE = False
MAJOR_VER = 0
MINOR_VER = 1
PATCH_LEVEL = 2
EXTRA = "alpha"
VERSION = ".".join([str(x) for x in [MAJOR_VER, MINOR_VER, PATCH_LEVEL]])+(f"-{EXTRA}" if EXTRA != None else "")
LOGDIR = os.path.join(os.path.dirname(__file__), "logs")
LOGFILE = os.path.join(LOGDIR, f'{time.strftime("%Y-%m-%d %H:%M:%S")}.log')
SCR_LOG = os.path.join(LOGDIR, 'logger')

class ExecutingInterrupt:
    interrupt = False
    
    def __init__(self, exit_msg=None) -> None:
        self.msg = exit_msg
    
    def _handler(self, signum, frame) -> None:
        self.interrupt = True
        self.signal = signum
        self.frame = frame
    
    def __enter__(self) -> None:
        self.old_sigint = signal.signal(signal.SIGINT, self._handler)
        self.old_sigterm = signal.signal(signal.SIGTERM, self._handler)
    
    def __exit__(self, type, value, traceback) -> None:
        signal.signal(signal.SIGINT, self.old_sigint)
        signal.signal(signal.SIGTERM, self.old_sigterm)
        if self.interrupt:
            printf(self.msg, level='e') if not self.msg == None else printf("Output of script: " + read_log(script_log=True), level='e')
            save_logs()
            remove_log(script_log=True)
            sys.exit(self.signal)

def do_nothing() -> None:
    pass

def printf(*message, level="*"):
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
    msg = f"[{'*' if _level == 'i' else '!' if _level == 'w' else '@' if _level == 'e' else '~' if _level == 'd' else '.' if _level == 'v' else '&' if _level == 'f' else '?'}] {string}"
    print(msg)
    write_log(msg)
    if _level == 'f':
        raise Exception(string)

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

def read_log(script_log=False) -> str:
    return ("".join(read(LOGFILE)) if not script_log else "".join(read(SCR_LOG)))

def write_log(something: str) -> None:
    write(LOGFILE, f'[{time.strftime("%Y-%m-%d %H:%M:%S")} ({time.process_time()} from start)] ' + something, append=True)

def remove_log(script_log=False) -> None:
    remove(LOGFILE if not script_log else SCR_LOG)

def save_logs() -> None:
    data = read_log(script_log=True)
    write_log("Output of previous script: " + data) if data != "" and data != None and type(data) == str else do_nothing()

def execute(script: str, args="", exit_msg=None) -> True:
    '''
    Runner of scripts under scripts folder.
    If script fails, it might to kill parent (this script) by $1 argument
    Basedir can be accessed by $2.
    Logging file is on $3 argument.
    '''
    SCR_FOLDER = os.path.join(os.path.dirname(__file__), "scripts")
    SCRIPT = os.path.join(SCR_FOLDER, f"{script}.sh")
    if not os.path.exists(SCRIPT):
        raise Exception(f"No script found {SCRIPT}")
    create_file(SCR_LOG)
    with ExecutingInterrupt() as ei:
        os.system(f"chmod 755 {SCRIPT}")
        os.system(f"\"{SCRIPT}\" {os.getpid()} \"{os.path.dirname(__file__)}\" \"{SCR_LOG}\" {'' if args == None else args if type(args) != list else ' '.join(args)}")
    save_logs()
    remove_log(script_log=True)
    

def arg_parse():
    parser =  ArgumentParser(description="Build system for UnOS kernel", epilog="Under GNU v3 Public license. UnOS is not new OS, it is Linux rewrite to Rust")
    parser.add_argument("target", help="Build terget (clean will clear logs and data)", default="default", choices=["default", "clean"], metavar="TARGET", nargs="?")
    parser.add_argument("-v", "--verbose", help="Be verbose", action="store_true")
    parser.add_argument("--debug", help="Switch into debug configuration", action='store_true')
    parser.add_argument("-a", "--arch", help="Build for ARCH", default="x86_64", choices=["x86_64"])
    args = parser.parse_args()
    return args

def main(args):
    DEBUG = args.debug
    VERBOSE = args.verbose
    create_dir(LOGDIR)
    create_file(LOGFILE)
    if args.target == "clean":
        remove(LOGDIR, recursive=True)
        sys.exit(0)
    execute("check_cmd", args="grkerg", exit_msg="Preparing failed! Dirs can't be created! Abort")

if __name__ == "__main__":
    main(arg_parse())