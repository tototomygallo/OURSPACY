"""
lsm_spacy: computation of Language Style Matching (LSM) over dialogue
transcripts, using spaCy for morphosyntactic analysis.
"""

from .core import CATEGORIES, calculate_lsm, count_categories, supported_languages

from .io_utils import read_dialogue


__all__ = [
    "calculate_lsm",
    "count_categories",
    "CATEGORIES",
    "supported_languages",
    "read_dialogue"
]

__version__ = "0.1.0"
