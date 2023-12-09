import sys

try:
    _build_py = sys.modules["build_py"]
except KeyError:
    raise Exception("build_py not found, exit!")

_ConfigRead = _build_py.ConfigRead
_Result = _build_py.Result
_execute = _build_py.execute

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

