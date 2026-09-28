"""
Language Style Matching (LSM) computation over dialogue transcripts,
using spaCy for morphosyntactic analysis.

Everything lives in a single file on purpose: model loading, the
per-language category counting (dispatched with an if/elif on the
language) and the main calculate_lsm function. To add a new language it's
enough to touch this file in the two spots marked below.
"""

from collections import defaultdict
from typing import Optional


import spacy

# ==========================================
# MODEL LOADING (lazy loading + cache)
# ==========================================

_MODELS = {}


def _get_model(lang: str):
    """Loads the spaCy model for the requested language, caching it so it
    isn't reloaded on every call."""

    if lang == "es":
        if "es" not in _MODELS:
            _MODELS["es"] = spacy.load("es_core_news_md")
        return _MODELS["es"]

    elif lang == "en":
        if "en" not in _MODELS:
            _MODELS["en"] = spacy.load("en_core_web_md")
        return _MODELS["en"]

    elif lang == "gm":
        if "gm" not in _MODELS:
            _MODELS["gm"] = spacy.load("de_core_news_md")
        return _MODELS["gm"]

    elif lang == "pt":
        if "pt" not in _MODELS:
            _MODELS["pt"] = spacy.load("pt_core_news_md")
        return _MODELS["pt"]

    # [ADD A NEW LANGUAGE HERE]
    # elif lang == "jp":
    #     if "jp" not in _MODELS:
    #         _MODELS["jp"] = spacy.load("ja_core_news_md")
    #     return _MODELS["jp"]

    else:
        raise ValueError(f"No model configured for language '{lang}'.")


def supported_languages() -> list[str]:
    """List of currently supported language codes."""
    return ["es", "en", "gm", "pt"]  # + ["jp"] if you add Japanese support


# ==========================================
# PER-LANGUAGE CATEGORY COUNTING
# ==========================================

CATEGORIES = [
    "ppron",    # personal pronouns
    "ipron",    # impersonal/indefinite pronouns
    "article",  # articles
    "prep",     # prepositions
    "negate",   # negations
    "adverb",   # adverbs
    "auxverb",  # auxiliary verbs
    "conj",     # conjunctions
]


def _is_negation_es(t) -> bool:
    return (
        t.lemma_.lower() == "no"
        or t.dep_ == "neg"
        or "Neg" in t.morph.get("PronType")
        or "Neg" in t.morph.get("Polarity")
    )


def count_categories(text: str, lang: str = "es"):
    """
    Analyzes a text and returns (count_per_category, word_count)
    according to the morphosyntactic rules of the chosen language.

    Each category's rules depend on the spaCy tagset of each language
    (e.g. how negation is marked), which is why counting is done with an
    if/elif per language instead of a single shared piece of logic.
    """
    nlp = _get_model(lang)
    counts = defaultdict(int)
    doc = nlp(text)

    # ------------------------------------------
    # 1. SPANISH
    # ------------------------------------------
    if lang == "es":
        for t in doc:
            if t.is_punct or t.is_space:
                continue
            if _is_negation_es(t):
                counts["negate"] += 1
            elif t.pos_ == "PRON":
                if "Prs" in t.morph.get("PronType"):
                    counts["ppron"] += 1
                else:
                    counts["ipron"] += 1
            elif t.pos_ == "DET":
                if "Art" in t.morph.get("PronType"):
                    counts["article"] += 1
            elif t.pos_ == "ADP":
                counts["prep"] += 1
            elif t.pos_ == "ADV":
                counts["adverb"] += 1
            elif t.pos_ == "AUX":
                counts["auxverb"] += 1
            elif t.pos_ in ("CCONJ", "SCONJ"):
                counts["conj"] += 1

        total_words = len([t for t in doc if not (t.is_space or t.is_punct)])
        return counts, total_words

    # ------------------------------------------
    # 2. ENGLISH
    # ------------------------------------------
    elif lang == "en":
        for t in doc:
            if t.is_punct or t.is_space:
                continue

            if t.dep_ == "neg":
                counts["negate"] += 1
            elif t.pos_ == "PRON":
                if t.tag_ in ("PRP", "PRP$"):
                    counts["ppron"] += 1
                else:
                    counts["ipron"] += 1
            elif t.pos_ == "DET":
                counts["article"] += 1
            elif t.pos_ == "ADP":
                counts["prep"] += 1
            elif t.pos_ == "ADV":
                counts["adverb"] += 1
            elif t.pos_ == "AUX":
                counts["auxverb"] += 1
            elif t.pos_ in ("CCONJ", "SCONJ"):
                counts["conj"] += 1

        total_words = len([t for t in doc if not (t.is_space or t.is_punct)])
        return counts, total_words

    # ------------------------------------------
    # 3. GERMAN
    # ------------------------------------------
    elif lang == "gm":
            # Lemas de auxiliares principales en alemán
        LEMAS_AUX = {"sein", "haben", "werden"}

        for t in doc:
            if t.is_punct or t.is_space:
                continue

            tag = t.tag_  # Etiqueta STTS fina para alemán
            lemma = t.lemma_.lower()

            # 1. Negaciones ('nicht' o determinantes negativos como 'kein/keine')
            if tag == "PTKNEG" or lemma == "kein":
                counts["negate"] += 1

            # 2. Pronombres Personales (ich, du, er, sich, mein, dein...)
            elif tag in ["PPER", "PRF", "POSS"]:
                counts["ppron"] += 1

            # 3. Pronombres Impersonales/Demostrativos (das, dies, jemand, wer...)
            elif tag in ["PIS", "PDS", "PDAT", "PWS", "PWAT", "PRELS"]:
                counts["ipron"] += 1

            # 4. Artículos (der, die, das, ein, eine...)
            elif tag == "ART":
                counts["article"] += 1

            # 5. Preposiciones (in, auf, mit y fusiones como im, am, zum)
            elif tag in ["APPR", "APPRART", "APPO"]:
                counts["prep"] += 1

            # 6. Adverbios (hier, da, schnell, damit, darüber...)
            elif tag in ["ADV", "PAV"]:
                counts["adverb"] += 1

            # 7. Verbos Auxiliares (formas conjugadas de sein, haben, werden)
            elif tag.startswith("VA") or (
                t.pos_ in ["VERB", "AUX"] and lemma in LEMAS_AUX
            ):
                counts["auxverb"] += 1

            # 8. Conjunciones (und, oder, aber, weil, dass...)
            elif tag in ["KON", "KOUS", "KOUI"] or t.pos_ in ["CCONJ", "SCONJ"]:
                counts["conj"] += 1

        total_words = len([t for t in doc if not (t.is_space or t.is_punct)])
        return counts, total_words

    elif lang == "pt":
        for t in doc:
            if t.is_punct or t.is_space:
                continue
            # Atributo morfológico en dict o lista para verificar claves/valores
            polarity = t.morph.get("Polarity")
            prontype = t.morph.get("PronType")
            definite = t.morph.get("Definite")

            # 1. Negaciones (Estricto por marcador morfológico UD)
            if "Neg" in polarity:
                counts["negate"] += 1

            # 2 y 3. Pronombres (Personales/Poseedores vs Impersonales/Otros)
            elif t.pos_ == "PRON":
                if "Prs" in prontype:
                    counts["ppron"] += 1
                else:
                    counts["ipron"] += 1

            # 4. Artículos (Definidos e Indefinidos)
            elif t.pos_ == "DET" and any(d in definite for d in ["Def", "Ind"]):
                counts["article"] += 1

            # 5. Preposiciones
            elif t.pos_ == "ADP":
                counts["prep"] += 1

            # 6. Adverbios (Evaluado tras negate)
            elif t.pos_ == "ADV":
                counts["adverb"] += 1

            # 7. Verbos Auxiliares
            elif t.pos_ == "AUX":
                counts["auxverb"] += 1

            # 8. Conjunciones (Coordinantes y Subordinantes)
            elif t.pos_ in ["CCONJ", "SCONJ"]:
                counts["conj"] += 1

        total_words = len([t for t in doc if not (t.is_space or t.is_punct)])
        return counts, total_words
    # ------------------------------------------
    # [ADD A NEW LANGUAGE HERE]
    # E.g.: elif lang == "jp": ...
    # ------------------------------------------

    else:
        raise ValueError(f"Support not implemented for language: '{lang}'")


# ==========================================
# MAIN LSM COMPUTATION
# ==========================================

def calculate_lsm(conversation: list[str], lang: str = "es", min_words: int = 20) -> Optional[float]:
    """
    Takes a list of strings ["SPEAKER_A: text", "SPEAKER_B: text"] and
    computes the LSM metric for the specified language ('es' or 'en').

    Returns None (not a float) when the LSM value is undefined: if there
    are fewer than 2 speakers, or if either of the two main speakers has
    no words counted.
    """
    speaker_data = defaultdict(lambda: defaultdict(int))
    speaker_word_count = defaultdict(int)

    # 1. Group all the text by speaker
    for line in conversation:
        if ":" not in line:
            continue
        speaker, text = line.split(":", 1)
        speaker = speaker.strip()

        counts, wc = count_categories(text.strip(), lang=lang)
        for cat, val in counts.items():
            speaker_data[speaker][cat] += val
        speaker_word_count[speaker] += wc

    # 2. Check that there are at least 2 speakers
    speaker_ids = list(speaker_data.keys())
    if len(speaker_ids) < 2:
        return None

    p1, p2 = speaker_ids[0], speaker_ids[1]

    # If either speaker has no words counted, the percentages would be
    # 0/0 (undefined).
    if (speaker_word_count[p1] < min_words or
        speaker_word_count[p2] < min_words):
        return None

    # 3. Compute percentages and LSM
    lsm_scores = []

    for c in CATEGORIES:
        pct1 = (speaker_data[p1][c] / speaker_word_count[p1]) * 100
        pct2 = (speaker_data[p2][c] / speaker_word_count[p2]) * 100

        score = 1 - (abs(pct1 - pct2) / (pct1 + pct2 + 0.0001))
        lsm_scores.append(score)

    return sum(lsm_scores) / len(lsm_scores)


if __name__ == "__main__":

    dialogue_es = [
        "A: Creo que no vamos a poder ir hoy porque está complicado.",
        "B: Sí, creo que no vamos a poder ir hoy, está bastante complicado."
    ]
    print("LSM Spanish:", calculate_lsm(dialogue_es, lang="es"))

    dialogue_en = [
        "A: I do not think we can go today because it is complicated.",
        "B: Yes I think we cannot go today it is quite complicated."
    ]
    print("LSM English:", calculate_lsm(dialogue_en, lang="en"))
