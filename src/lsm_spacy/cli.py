"""
Command-line interface for lsm_spacy.

Installed as the `lsm-spacy` command (see [project.scripts] in
pyproject.toml). Doesn't change the logic in core.py: it just reads a
file, passes it to calculate_lsm as-is, and prints the result.
"""

import argparse
import sys

from .core import calculate_lsm, supported_languages
from .io_utils import read_dialogue


def main():
    parser = argparse.ArgumentParser(
        prog="lsm-spacy",
        description="Computes the LSM (Language Style Matching) of a dialogue in a .txt file.",
    )
    parser.add_argument(
        "file",
        help="Path to the .txt file with the dialogue (one 'SPEAKER: text' line per turn).",
    )
    parser.add_argument(
        "--lang",
        default="es",
        choices=supported_languages(),
        help="Language of the dialogue (default: es).",
    )
    parser.add_argument(
        "--min-words",
        type=int,
        default=20,
        help="Minimum number of words each speaker must have for the LSM to be computed (default: 20).",
    )

    args = parser.parse_args()

    try:
        lines = read_dialogue(args.file)
    except FileNotFoundError:
        print(f"✗ File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    if not lines:
        print(f"✗ File is empty: {args.file}", file=sys.stderr)
        sys.exit(1)

    score = calculate_lsm(lines, lang=args.lang, min_words=args.min_words)

    if score is None:
        print(f"LSM: None (undefined -- see min_words={args.min_words} / number of speakers)")
    else:
        print(f"LSM: {score:.4f}")


if __name__ == "__main__":
    main()
