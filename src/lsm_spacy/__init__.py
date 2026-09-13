"""
lsm_spacy: cálculo de Language Style Matching (LSM) sobre transcripciones
de diálogo, usando spaCy para el análisis morfosintáctico.
"""

from .core import CATEGORIAS, calculo_LSM, conteo_categorias, idiomas_soportados

from .io_utils import leer_dialogo


__all__ = [
    "calculo_LSM",
    "conteo_categorias",
    "CATEGORIAS",
    "idiomas_soportados",
    "leer_dialogo"
]

__version__ = "0.1.0"
