# OURSPACY

Computation of **Language Style Matching (LSM)** over dialogue
transcripts, using [spaCy](https://spacy.io/) for morphosyntactic
analysis. The Python package is called `lsm_spacy` (that's what you
import in code), but the project/repo is called **OURSPACY** for now.

LSM measures how much two people in a conversation match each other's use
of function words (pronouns, articles, prepositions, negations, adverbs,
auxiliary verbs, and conjunctions) — see Ireland & Pennebaker (2010) for
the original definition of the metric.

## Table of contents

- [Installation](#installation)
- [Quick usage (command line)](#quick-usage-command-line)
- [Usage from Python](#usage-from-python)
- [The `min_words` parameter](#the-min_words-parameter)
- [Input dialogue/file format](#input-dialoguefile-format)
- [When it returns `None`](#when-it-returns-none)
- [Supported languages](#supported-languages)
- [License](#license)

## Installation

The package isn't published on PyPI yet, so for now this is the **only**
supported installation process:

```bash
git clone https://github.com/tototomygallo/OURSPACY
cd OURSPACY
pip install -e ".[dev]"
python -m spacy download es_core_news_md
python -m spacy download en_core_web_md
pytest
```

The spaCy language model does **not** ship with the package (it's too
heavy), which is why it has to be downloaded separately with
`python -m spacy download ...`. If you skip this step, `lsm-spacy` will
raise an error explaining exactly which command to run. The final
`pytest` run runs the test suite to confirm the install went well.

## Quick usage (command line)

Installing the package also installs the `lsm-spacy` command, which
computes LSM directly over a `.txt` file:

```bash
lsm-spacy my_dialogue.txt
```

Heads up: by default a minimum of 20 words per speaker is required
(`min_words`, see [below](#the-min_words-parameter)). If your file has
short dialogues (like the examples in this README), you'll need to lower
that minimum with `--min-words`, or the result will be `None`.

Available options:

| Option        | Default | Description                                                     |
| ------------- | ------- | ---------------------------------------------------------------- |
| `--lang`      | `es`    | Language of the dialogue (`es` or `en`).                          |
| `--min-words` | `20`    | Minimum words per speaker for the LSM to be considered valid.     |

Examples:

```bash
# dialogue in English
lsm-spacy my_dialogue.txt --lang en

# lower the required minimum words per speaker to 5
lsm-spacy my_dialogue.txt --min-words 5

# combining both options
lsm-spacy my_dialogue.txt --lang en --min-words 5
```

Expected output:

```text
LSM: 0.8734
```

or, if the result is undefined (see [below](#when-it-returns-none)):

```text
LSM: None (undefined -- see min_words=20 / number of speakers)
```

## Usage from Python

```python
from lsm_spacy import calculate_lsm

dialogue = [
    "A: Creo que no vamos a poder ir hoy porque está complicado.",
    "B: Sí, creo que no vamos a poder ir hoy, está bastante complicado.",
]

# min_words=5 because this sample dialogue is short (~11 words per
# speaker); with the default (min_words=20) it would return None. See the
# "The min_words parameter" section below.
score = calculate_lsm(dialogue, lang="es", min_words=5)
print(score)  # e.g.: 0.87
```

Each line must have the format `"SPEAKER: text"`. Only the first two
distinct speakers that appear in the conversation are used.

If your dialogue is in a `.txt` file (one turn per line, same
`"SPEAKER: text"` format), use `read_dialogue` to turn it into the list
that `calculate_lsm` expects:

```python
from lsm_spacy import calculate_lsm, read_dialogue

dialogue = read_dialogue("my_dialogue.txt")
score = calculate_lsm(dialogue, lang="es")
print(score)
```

## The `min_words` parameter

`calculate_lsm` takes an optional `min_words` parameter (default: `20`):
the minimum number of words each of the two main speakers must have
counted for the LSM to be computed. If either of them doesn't reach that
minimum, the function returns `None`.

To change it, pass it as a keyword argument to `calculate_lsm` (no need
to touch `core.py`):

```python
from lsm_spacy import calculate_lsm

# require at least 5 words per speaker instead of 20
score = calculate_lsm(dialogue, lang="es", min_words=5)
```

From the command line it's the `--min-words` flag (see
[above](#quick-usage-command-line)):

```bash
lsm-spacy my_dialogue.txt --min-words 5
```

Lowering `min_words` allows computing LSM over short dialogues, but the
result becomes less reliable the fewer words there are to estimate the
per-category percentages.

## Input dialogue/file format

- One turn per line, in the format `"SPEAKER: text"`.
- Lines without `:` are ignored.
- Only the first two distinct speakers that appear are taken into
  account; if there's a third one, their lines are read but don't
  participate in the computation.

Example of a valid file:

```text
A: Creo que no vamos a poder ir hoy porque está complicado.
B: Sí, creo que no vamos a poder ir hoy, está bastante complicado.
A: Bueno, lo intentamos mañana entonces.
```

## When it returns `None`

`calculate_lsm` returns `None` (not `0.0`) when the LSM value is
**undefined**, not when it's simply low:

- if the conversation has fewer than 2 distinct speakers, or
- if either of the two main speakers doesn't reach `min_words` counted
  words.

This is intentional: treating `0.0` as "couldn't be computed" would mix
those cases up with conversations that do have a real, low LSM. If you're
saving results to a CSV or DataFrame, filter with something like
`df[df["lsm"].notna()]`, not `df[df["lsm"] > 0]`.

## Supported languages

```python
from lsm_spacy import supported_languages
print(supported_languages())  # ['es', 'en']
```

Adding a new language means editing `src/lsm_spacy/core.py`, in the two
spots marked with the `[ADD A NEW LANGUAGE HERE]` comment:

1. In `_get_model`, to load the corresponding spaCy model.
2. In `count_categories`, adding a new `elif lang == "..."` with that
   language's counting rules.

## License

MIT
