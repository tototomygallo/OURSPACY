"""
Cálculo de Language Style Matching (LSM) sobre transcripciones de diálogo,
usando spaCy para el análisis morfosintáctico.

Todo el cálculo vive en un solo archivo a propósito: la carga de modelos,
el conteo de categorías por idioma (con un if/elif que despacha según el
idioma) y la función principal calculo_LSM. Para agregar un idioma nuevo
alcanza con tocar este archivo en los dos lugares marcados más abajo.
"""

from collections import defaultdict
from typing import Optional


import spacy

# ==========================================
# CARGA DE MODELOS (lazy loading + cache)
# ==========================================

_MODELS = {}


def _get_model(lang: str):
    """Carga el modelo de spaCy del idioma pedido, cacheándolo para no
    volver a cargarlo en cada llamada."""

    if lang == "es":
        if "es" not in _MODELS:
            _MODELS["es"] = spacy.load("es_core_news_md")
        return _MODELS["es"]

    elif lang == "en":
        if "en" not in _MODELS:
            _MODELS["en"] = spacy.load("en_core_web_md")
        return _MODELS["en"]

    # [AGREGAR ACÁ UN NUEVO IDIOMA]
    # elif lang == "pt":
    #     if "pt" not in _MODELS:
    #         _MODELS["pt"] = spacy.load("pt_core_news_md")
    #     return _MODELS["pt"]

    else:
        raise ValueError(f"Modelo para el idioma '{lang}' no configurado.")


def idiomas_soportados() -> list[str]:
    """Lista de códigos de idioma actualmente soportados."""
    return ["es", "en"]


# ==========================================
# CONTEO DE CATEGORÍAS POR IDIOMA
# ==========================================

CATEGORIAS = [
    "ppron",    # pronombres personales
    "ipron",    # pronombres impersonales/indefinidos
    "article",  # artículos
    "prep",     # preposiciones
    "negate",   # negaciones
    "adverb",   # adverbios
    "auxverb",  # verbos auxiliares
    "conj",     # conjunciones
]


def _es_negacion_es(t) -> bool:
    return (
        t.lemma_.lower() == "no"
        or t.dep_ == "neg"
        or "Neg" in t.morph.get("PronType")
        or "Neg" in t.morph.get("Polarity")
    )


def conteo_categorias(text: str, lang: str = "es"):
    """
    Analiza un texto y devuelve (conteo_por_categoria, cantidad_de_palabras)
    según las reglas morfosintácticas del idioma elegido.

    Las reglas de cada categoría dependen del tagset de spaCy de cada
    idioma (por ejemplo, cómo se marca la negación), por eso el conteo se
    hace con un if/elif por idioma en vez de una única lógica compartida.
    """
    nlp = _get_model(lang)
    contador = defaultdict(int)
    doc = nlp(text)

    # ------------------------------------------
    # 1. ESPAÑOL
    # ------------------------------------------
    if lang == "es":
        for t in doc:
            if t.is_punct or t.is_space:
                continue

            if _es_negacion_es(t):
                contador["negate"] += 1
            elif t.pos_ == "PRON":
                if "Prs" in t.morph.get("PronType"):
                    contador["ppron"] += 1
                else:
                    contador["ipron"] += 1
            elif t.pos_ == "DET":
                if "Art" in t.morph.get("PronType"):
                    contador["article"] += 1
            elif t.pos_ == "ADP":
                contador["prep"] += 1
            elif t.pos_ == "ADV":
                contador["adverb"] += 1
            elif t.pos_ == "AUX":
                contador["auxverb"] += 1
            elif t.pos_ in ("CCONJ", "SCONJ"):
                contador["conj"] += 1

        palabras_totales = len([t for t in doc if not (t.is_space or t.is_punct)])
        return contador, palabras_totales

    # ------------------------------------------
    # 2. INGLÉS
    # ------------------------------------------
    elif lang == "en":
        for t in doc:
            if t.is_punct or t.is_space:
                continue

            if t.dep_ == "neg":
                contador["negate"] += 1
            elif t.pos_ == "PRON":
                if t.tag_ in ("PRP", "PRP$"):
                    contador["ppron"] += 1
                else:
                    contador["ipron"] += 1
            elif t.pos_ == "DET":
                contador["article"] += 1
            elif t.pos_ == "ADP":
                contador["prep"] += 1
            elif t.pos_ == "ADV":
                contador["adverb"] += 1
            elif t.pos_ == "AUX":
                contador["auxverb"] += 1
            elif t.pos_ in ("CCONJ", "SCONJ"):
                contador["conj"] += 1

        palabras_totales = len(text.split())
        return contador, palabras_totales

    # ------------------------------------------
    # [AGREGAR ACÁ UN NUEVO IDIOMA]
    # Ej: elif lang == "pt": ...
    # ------------------------------------------

    else:
        raise ValueError(f"Soporte no implementado para el idioma: '{lang}'")


# ==========================================
# CÁLCULO PRINCIPAL DE LSM
# ==========================================

def calculo_LSM(conversation: list[str], lang: str = "es", min_words: int = 20) -> Optional[float]:
    """
    Recibe una lista de strings ["HABLANTE_A: texto", "HABLANTE_B: texto"]
    y calcula la métrica de LSM para el idioma especificado ('es' o 'en').

    Devuelve None (no un float) cuando el valor de LSM está indefinido:
    si hay menos de 2 hablantes, o si alguno de los dos hablantes
    principales no tiene palabras contabilizadas.
    """
    Data_hablante = defaultdict(lambda: defaultdict(int))
    contador_palabras_hablante = defaultdict(int)

    # 1. Agrupar todo el texto por usuario
    for line in conversation:
        if ":" not in line:
            continue
        user, text = line.split(":", 1)
        user = user.strip()

        counts, wc = conteo_categorias(text.strip(), lang=lang)
        for cat, val in counts.items():
            Data_hablante[user][cat] += val
        contador_palabras_hablante[user] += wc

    # 2. Verificar que haya al menos 2 hablantes
    hablantes_ids = list(Data_hablante.keys())
    if len(hablantes_ids) < 2:
        return None

    p1, p2 = hablantes_ids[0], hablantes_ids[1]

    # Si alguno de los hablantes no tiene palabras contadas, los
    # porcentajes serían 0/0 (indefinidos).
    if (contador_palabras_hablante[p1] < min_words or
        contador_palabras_hablante[p2] < min_words):
        return None

    # 3. Calcular porcentajes y LSM
    lsm_scores = []

    for c in CATEGORIAS:
        pct1 = (Data_hablante[p1][c] / contador_palabras_hablante[p1]) * 100
        pct2 = (Data_hablante[p2][c] / contador_palabras_hablante[p2]) * 100

        score = 1 - (abs(pct1 - pct2) / (pct1 + pct2 + 0.0001))
        lsm_scores.append(score)

    return sum(lsm_scores) / len(lsm_scores) 


if __name__ == "__main__":

    dialogo_es = [
        "A: Creo que no vamos a poder ir hoy porque está complicado.",
        "B: Sí, creo que no vamos a poder ir hoy, está bastante complicado."
    ]
    print("LSM Español:", calculo_LSM(dialogo_es, lang="es"))

    dialogo_en = [
        "A: I do not think we can go today because it is complicated.",
        "B: Yes I think we cannot go today it is quite complicated."
    ]
    print("LSM Inglés: ", calculo_LSM(dialogo_en, lang="en"))
