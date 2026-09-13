from lsm_spacy.io_utils import leer_dialogo
from src.lsm_spacy.core import calculo_LSM

ARCHIVO = "/home/tgallo/Documents/Proyecto_modular/output/sw2007-ms98-a.txt"

lineas = leer_dialogo(ARCHIVO)
print("Líneas leídas del archivo:")
for l in lineas:
    print(" ", repr(l))

score = calculo_LSM(lineas, lang="en")
print("\nLSM:", score)