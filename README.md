# OURSPACY

Cálculo de **Language Style Matching (LSM)** sobre transcripciones de
diálogo, usando [spaCy](https://spacy.io/) para el análisis morfosintáctico.
El paquete de Python se llama `lsm_spacy` (así se importa en el código),
pero el proyecto/repo por ahora se llama **OURSPACY**.

LSM mide en qué medida dos personas que conversan igualan su uso de
palabras funcionales (pronombres, artículos, preposiciones, negaciones,
adverbios, verbos auxiliares y conjunciones) — ver Ireland & Pennebaker
(2010) para la definición original de la métrica.

## Índice

- [Instalación](#instalación)
- [Uso rápido (línea de comandos)](#uso-rápido-línea-de-comandos)
- [Uso desde Python](#uso-desde-python)
- [El parámetro `min_words`](#el-parámetro-min_words)
- [Formato del archivo/diálogo de entrada](#formato-del-archivodiálogo-de-entrada)
- [Cuándo devuelve `None`](#cuándo-devuelve-none)
- [Idiomas soportados](#idiomas-soportados)
- [Licencia](#licencia)

## Instalación

El paquete todavía no está publicado en PyPI, así que por ahora este es el
**único** proceso de instalación soportado:

```bash
git clone https://github.com/tototomygallo/OURSPACY
cd OURSPACY
pip install -e ".[dev]"
python -m spacy download es_core_news_md
python -m spacy download en_core_web_md
pytest
```

El modelo de idioma de spaCy **no** viaja con el paquete (pesa demasiado),
por eso hay que descargarlo aparte con `python -m spacy download ...`. Si
te olvidás este paso, `lsm-spacy` va a tirar un error explicando
exactamente qué comando correr para arreglarlo. El `pytest` final corre la
suite de tests para confirmar que la instalación quedó bien.

## Uso rápido (línea de comandos)

Instalar el paquete también instala el comando `lsm-spacy`, que calcula el
LSM directamente sobre un archivo `.txt`:

```bash
lsm-spacy mi_dialogo.txt
```

Ojo: por default se exige un mínimo de 20 palabras por hablante
(`min_words`, ver [más abajo](#el-parámetro-min_words)). Si tu archivo
tiene diálogos cortos (como los ejemplos de este README), vas a necesitar
bajar ese mínimo con `--min-words`, o el resultado va a dar `None`.

Opciones disponibles:


| Opción       | Default | Descripción                                                           |
| --------------- | --------- | ------------------------------------------------------------------------ |
| `--lang`      | `es`    | Idioma del diálogo (`es` o `en`).                                     |
| `--min-words` | `20`    | Mínimo de palabras por hablante para que el LSM se considere válido. |

Ejemplos:

```bash
# diálogo en inglés
lsm-spacy mi_dialogo.txt --lang en

# bajar el mínimo de palabras exigido por hablante a 5
lsm-spacy mi_dialogo.txt --min-words 5

# combinando ambas opciones
lsm-spacy mi_dialogo.txt --lang en --min-words 5
```

Salida esperada:

```text
LSM: 0.8734
```

o, si el resultado está indefinido (ver [más abajo](#cuándo-devuelve-none)):

```text
LSM: None (indefinido -- ver min_words=20 / cantidad de hablantes)
```

## Uso desde Python

```python
from lsm_spacy import calculo_LSM

dialogo = [
    "A: Creo que no vamos a poder ir hoy porque está complicado.",
    "B: Sí, creo que no vamos a poder ir hoy, está bastante complicado.",
]

# min_words=5 porque este diálogo de ejemplo es corto (~11 palabras por
# hablante); con el default (min_words=20) daría None. Ver la sección
# "El parámetro min_words" más abajo.
score = calculo_LSM(dialogo, lang="es", min_words=5)
print(score)  # ej: 0.87
```

Cada línea debe tener el formato `"HABLANTE: texto"`. Solo se usan los
dos primeros hablantes distintos que aparezcan en la conversación.

Si tu diálogo está en un archivo `.txt` (una intervención por línea, mismo
formato `"HABLANTE: texto"`), usá `leer_dialogo` para convertirlo en la
lista que espera `calculo_LSM`:

```python
from lsm_spacy import calculo_LSM, leer_dialogo

dialogo = leer_dialogo("mi_dialogo.txt")
score = calculo_LSM(dialogo, lang="es")
print(score)
```

## El parámetro `min_words`

`calculo_LSM` recibe un parámetro opcional `min_words` (default: `20`):
es la cantidad mínima de palabras que cada uno de los dos hablantes
principales tiene que tener contabilizadas para que el LSM se calcule. Si
alguno de los dos no llega a ese mínimo, la función devuelve `None`.

Para cambiarlo, se pasa como argumento con nombre en la llamada a
`calculo_LSM` (no hay que tocar `core.py`):

```python
from lsm_spacy import calculo_LSM

# exigir al menos 5 palabras por hablante en vez de 20
score = calculo_LSM(dialogo, lang="es", min_words=5)
```

Por línea de comandos es el flag `--min-words` (ver [arriba](#uso-rápido-línea-de-comandos)):

```bash
lsm-spacy mi_dialogo.txt --min-words 5
```

Bajar `min_words` permite calcular LSM sobre diálogos cortos, pero el
resultado se vuelve menos confiable cuantas menos palabras haya para
estimar los porcentajes por categoría.

## Formato del archivo/diálogo de entrada

- Una intervención por línea, con el formato `"HABLANTE: texto"`.
- Las líneas sin `:` se ignoran.
- Solo se tienen en cuenta los dos primeros hablantes distintos que
  aparecen; si hay un tercero, sus líneas se leen pero no participan del
  cálculo.

Ejemplo de archivo válido:

```text
A: Creo que no vamos a poder ir hoy porque está complicado.
B: Sí, creo que no vamos a poder ir hoy, está bastante complicado.
A: Bueno, lo intentamos mañana entonces.
```

## Cuándo devuelve `None`

`calculo_LSM` devuelve `None` (no `0.0`) cuando el valor de LSM está
**indefinido**, no cuando da bajo:

- si la conversación tiene menos de 2 hablantes distintos, o
- si alguno de los dos hablantes principales no llega a `min_words`
  palabras contabilizadas.

Esto es intencional: tratar `0.0` como "no se pudo calcular" mezclaría
esos casos con conversaciones que sí tienen un LSM real y bajo. Si vas a
guardar resultados en un CSV o DataFrame, filtrá con algo como
`df[df["lsm"].notna()]`, no con `df[df["lsm"] > 0]`.

## Idiomas soportados

```python
from lsm_spacy import idiomas_soportados
print(idiomas_soportados())  # ['es', 'en']
```

Agregar un idioma nuevo implica editar `src/lsm_spacy/core.py`, en los dos
lugares marcados con el comentario `[AGREGAR ACÁ UN NUEVO IDIOMA]`:

1. En `_get_model`, para cargar el modelo de spaCy correspondiente.
2. En `conteo_categorias`, agregando un nuevo `elif lang == "..."` con las
   reglas de conteo de ese idioma.

## Licencia

MIT
