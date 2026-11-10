"""Pruebas del World: lectura de Prueba1, validación, es_libre y __str__."""

from pathlib import Path

import pytest

from core.mundo import World

RUTA_PRUEBA1 = Path(__file__).resolve().parent.parent / "worlds" / "Prueba1.txt"

BASE_VALIDA = [
    "1 1 4 1 1 1 5 1 1 1",
    "0 0 0 0 0 0 0 0 0 0",
    "0 1 1 0 1 1 1 1 1 0",
    "0 1 1 0 0 0 0 0 0 0",
    "2 0 0 3 1 1 0 1 1 1",
    "0 1 1 3 1 1 0 1 1 1",
    "0 1 1 0 1 1 0 0 3 1",
    "0 0 0 0 1 1 0 1 0 1",
    "1 1 1 0 1 1 0 1 0 1",
    "1 1 1 0 0 0 0 0 0 1",
]


def _escribir_mundo(tmp_path, filas):
    ruta = tmp_path / "mundo.txt"
    ruta.write_text("\n".join(filas) + "\n", encoding="utf-8")
    return str(ruta)


def test_lee_prueba1():
    w = World.desde_archivo(str(RUTA_PRUEBA1))
    assert w.filas == 10
    assert w.columnas == 10
    assert w.inicio == (4, 0)
    assert w.deposito == (0, 2)
    assert w.avioneta == (0, 6)
    assert w.cultivos == frozenset({(4, 3), (5, 3), (6, 8)})
    assert (0, 0) in w.muros
    assert w.inicio not in w.muros


def test_archivo_inexistente():
    with pytest.raises(FileNotFoundError):
        World.desde_archivo(" mundos/no_existe.txt")


def test_error_dos_robots(tmp_path):
    filas = list(BASE_VALIDA)
    # Agrega un segundo robot en (1, 0), que era libre.
    filas[1] = "2 0 0 0 0 0 0 0 0 0"
    with pytest.raises(ValueError, match="robot"):
        World.desde_archivo(_escribir_mundo(tmp_path, filas))


def test_error_sin_deposito(tmp_path):
    filas = list(BASE_VALIDA)
    # Quita el depósito (0, 2) poniéndolo libre.
    filas[0] = "1 1 0 1 1 1 5 1 1 1"
    with pytest.raises(ValueError, match="depósito"):
        World.desde_archivo(_escribir_mundo(tmp_path, filas))


def test_error_valor_invalido(tmp_path):
    filas = list(BASE_VALIDA)
    filas[1] = "0 0 0 0 0 0 0 7 0 0"
    with pytest.raises(ValueError, match="inválido"):
        World.desde_archivo(_escribir_mundo(tmp_path, filas))


def test_error_fila_tamano_incorrecto(tmp_path):
    filas = list(BASE_VALIDA)
    filas[1] = "0 0 0 0 0 0 0 0 0"  # 9 columnas en vez de 10
    with pytest.raises(ValueError, match="columnas"):
        World.desde_archivo(_escribir_mundo(tmp_path, filas))


def test_es_libre():
    w = World.desde_archivo(str(RUTA_PRUEBA1))
    assert w.es_libre(1, 0)  # casilla libre
    assert w.es_libre(4, 0)  # inicio transitable
    assert w.es_libre(0, 2)  # depósito transitable
    assert w.es_libre(0, 6)  # avioneta transitable
    assert w.es_libre(4, 3)  # cultivo transitable
    assert not w.es_libre(0, 0)  # muro
    assert not w.es_libre(-1, 0)  # fuera de rango
    assert not w.es_libre(10, 0)  # fuera de rango
    assert not w.es_libre(0, 10)  # fuera de rango


def test_str_reproduce_matriz():
    w = World.desde_archivo(str(RUTA_PRUEBA1))
    lineas = str(w).strip().split("\n")
    assert len(lineas) == 10
    assert lineas[0] == BASE_VALIDA[0]
    assert lineas[4] == BASE_VALIDA[4]
