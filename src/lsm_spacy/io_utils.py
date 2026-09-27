"""
Utility for reading a dialogue .txt file and turning it into the list of
strings that calculate_lsm expects (["A: text", "B: text", ...]).

Does not modify or touch the logic in core.py.
"""

from pathlib import Path


def read_dialogue(path: str | Path) -> list[str]:
    """
    Reads a .txt file with lines in the format "SPEAKER: text" (one turn
    per line) and returns the list of strings ready to pass to
    calculate_lsm.

    Ignores empty lines. Does not validate the "SPEAKER:" format itself --
    that's already handled by calculate_lsm (lines without ":" are
    discarded there).
    """
    path = Path(path)

    with open(path, "r", encoding="utf8") as f:
        lines = [line.strip() for line in f if line.strip()]

    return lines
