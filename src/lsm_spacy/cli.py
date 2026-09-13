"""
Interfaz de línea de comandos para lsm_spacy.

Se instala como el comando `lsm-spacy` (ver [project.scripts] en
pyproject.toml). No modifica la lógica de core.py: solo lee un archivo,
se lo pasa a calculo_LSM tal cual está, y muestra el resultado.
"""

import argparse
import sys

from .core import calculo_LSM, idiomas_soportados
from .io_utils import leer_dialogo


def main():
    parser = argparse.ArgumentParser(
        prog="lsm-spacy",
        description="Calcula el LSM (Language Style Matching) de un diálogo en un archivo .txt.",
    )
    parser.add_argument(
        "archivo",
        help="Ruta al archivo .txt con el diálogo (formato 'HABLANTE: texto' por línea).",
    )
    parser.add_argument(
        "--lang",
        default="es",
        choices=idiomas_soportados(),
        help="Idioma del diálogo (default: es).",
    )

    args = parser.parse_args()

    try:
        lineas = leer_dialogo(args.archivo)
    except FileNotFoundError:
        print(f"✗ No se encontró el archivo: {args.archivo}", file=sys.stderr)
        sys.exit(1)

    if not lineas:
        print(f"✗ El archivo está vacío: {args.archivo}", file=sys.stderr)
        sys.exit(1)

    score = calculo_LSM(lineas, lang=args.lang)

    if score is None:
        print("LSM: None (indefinido -- ver min_words / cantidad de hablantes)")
    else:
        print(f"LSM: {score:.4f}")


if __name__ == "__main__":
    main()