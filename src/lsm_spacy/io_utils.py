"""
Utilidad para leer un archivo .txt de diálogo y convertirlo en la lista
de strings que espera calculo_LSM (["A: texto", "B: texto", ...]).

No modifica ni toca la lógica de core.py.
"""

from pathlib import Path


def leer_dialogo(path: str | Path) -> list[str]:
    """
    Lee un archivo .txt con líneas del formato "HABLANTE: texto" (una
    intervención por línea) y devuelve la lista de strings lista para
    pasarle a calculo_LSM.

    Ignora líneas vacías. No valida el formato "HABLANTE:" en sí --
    eso ya lo maneja calculo_LSM (las líneas sin ":" se descartan ahí).
    """
    path = Path(path)

    with open(path, "r", encoding="utf8") as f:
        lineas = [linea.strip() for linea in f if linea.strip()]

    return lineas