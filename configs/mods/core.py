import sys

try:
    _build_py = sys.modules["build_py"]
except KeyError:
    raise Exception("build_py not found, exit!")

_ConfigRead = _build_py.ConfigRead
_Result = _build_py.Result
_execute = _build_py.execute

def export(self: _ConfigRead, command_data: list[str]) -> _Result:
    first, second = "", ""
    if len(command_data) >= 3:
        first, second = command_data[0], command_data[2]
    elif len(command_data) == 0:
        return _Result(Exception("No given variable"))
    else:
        first, second = "".join(command_data).strip().split("=")
    self._variables[first] = second
    return _Result(True)

def debug(self: _ConfigRead, command_data: list[str]) -> _Result:
    if len(command_data) == 0:
        _build_py.definitions["debug"] = not _build_py.definitions["debug"]
        return _Result(True)
    if not command_data[0] in ["on", "off"]:
        return _Result(Exception(f"Invalid argument {command_data[0]}"))
    _build_py.definitions["debug"] = True if command_data[0] == "on" else False
    return _Result(True)

def echo(_: _ConfigRead, command_data: list[str]) -> _Result:
    print(" ".join(command_data))
    return _Result(True)

def exec(_: _ConfigRead, command_data: list[str]) -> _Result:
    data = " ".join(command_data)
    code = _execute(data)
    if code == 0:
        return _Result(True)
    return _Result(Exception(f"Command ended with code {code}!"))

def check_cmd(self: _ConfigRead, command_data: list[str]) -> _Result:
    for x in command_data:
        result = self.exec(self, [f"command -v {x}>/dev/null"])
        if result.is_err():
            return _Result(Exception(f"No command {x} found "))
    return _Result(True)

