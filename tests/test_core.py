import pytest

from lsm_spacy import calculo_LSM


def test_lsm_basico_espanol():
    dialogo = [
        "A: Creo que no vamos a poder ir hoy porque está complicado.",
        "B: Sí, creo que no vamos a poder ir hoy, está bastante complicado.",
    ]
    resultado = calculo_LSM(dialogo, lang="es")
    assert resultado is not None
    assert 0.0 <= resultado <= 1.0001  # el score suele caer en [0,1], con margen numérico


def test_lsm_basico_ingles():
    dialogo = [
        "A: I do not think we can go today because it is complicated.",
        "B: Yes I think we cannot go today it is quite complicated.",
    ]
    resultado = calculo_LSM(dialogo, lang="en")
    assert resultado is not None
    assert 0.0 <= resultado <= 1.0001


def test_menos_de_dos_hablantes_devuelve_none():
    dialogo = [
        "A: Hola, ¿cómo estás?",
        "A: Espero que bien.",
    ]
    assert calculo_LSM(dialogo, lang="es") is None


def test_conversacion_vacia_devuelve_none():
    assert calculo_LSM([], lang="es") is None


def test_hablante_sin_palabras_devuelve_none():
    # El segundo hablante no tiene texto real, solo puntuación.
    dialogo = [
        "A: Hola, ¿cómo estás?",
        "B: ...",
    ]
    resultado = calculo_LSM(dialogo, lang="es")
    assert resultado is None


def test_idioma_no_soportado_lanza_valueerror():
    dialogo = [
        "A: Bonjour, comment ça va?",
        "B: Ça va bien, merci.",
    ]
    with pytest.raises(ValueError):
        calculo_LSM(dialogo, lang="fr")


def test_lineas_sin_separador_se_ignoran():
    dialogo = [
        "esto no tiene separador de hablante",
        "A: Hola, ¿cómo estás?",
        "B: Muy bien, gracias.",
    ]
    resultado = calculo_LSM(dialogo, lang="es")
    assert resultado is not None
