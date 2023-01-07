try:
    from typing import Any, Tuple

    WriteCommand = Tuple[int, int, str, bool]
except ImportError:
    Any = ...
    WriteCommand = ...


def write(row: int, col: int, text: str, *, cond: Any = True) -> WriteCommand:
    return row, col, text, bool(cond)
