import pytest

from lsm_spacy import calculate_lsm


def test_lsm_basic_spanish():
    dialogue = [
        "A: Creo que no vamos a poder ir hoy porque está complicado.",
        "B: Sí, creo que no vamos a poder ir hoy, está bastante complicado.",
    ]
    result = calculate_lsm(dialogue, lang="es", min_words=5)
    assert result is not None
    assert 0.0 <= result <= 1.0001  # the score usually falls in [0,1], with numeric margin


def test_lsm_basic_english():
    dialogue = [
        "A: I do not think we can go today because it is complicated.",
        "B: Yes I think we cannot go today it is quite complicated.",
    ]
    result = calculate_lsm(dialogue, lang="en", min_words=5)
    assert result is not None
    assert 0.0 <= result <= 1.0001


def test_fewer_than_two_speakers_returns_none():
    dialogue = [
        "A: Hola, ¿cómo estás?",
        "A: Espero que bien.",
    ]
    assert calculate_lsm(dialogue, lang="es") is None


def test_empty_conversation_returns_none():
    assert calculate_lsm([], lang="es") is None


def test_speaker_with_no_words_returns_none():
    # The second speaker has no real text, only punctuation.
    dialogue = [
        "A: Hola, ¿cómo estás?",
        "B: ...",
    ]
    result = calculate_lsm(dialogue, lang="es")
    assert result is None


def test_unsupported_language_raises_valueerror():
    dialogue = [
        "A: Bonjour, comment ça va?",
        "B: Ça va bien, merci.",
    ]
    with pytest.raises(ValueError):
        calculate_lsm(dialogue, lang="fr")


def test_lines_without_separator_are_ignored():
    dialogue = [
        "esto no tiene separador de hablante",
        "A: Hola, ¿cómo estás?",
        "B: Muy bien, gracias.",
    ]
    result = calculate_lsm(dialogue, lang="es", min_words=1)
    assert result is not None
