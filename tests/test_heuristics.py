"""Pruebas de la heurística B del AgroBot.

Incluye la verificación exhaustiva de admisibilidad sobre `Prueba1` y dos
mundos pequeños: uno que obliga a recargar fertilizante y otro donde
conviene usar la avioneta.
"""

from __future__ import annotations

import heapq
import itertools
from pathlib import Path

import pytest

from algorithms.heuristics import HeuristicaAgroBot
from core.problem import Problema
from core.state import Estado
from core.world import World

RUTA_PRUEBA1 = Path(__file__).resolve().parent.parent / "worlds" / "Prueba1.txt"

# Cultivos de Prueba1 usados en los ejemplos del contexto.
A = (4, 3)
B = (5, 3)
C = (6, 8)


def _world_from_grid(grid: list[list[int]]) -> World:
    """Construye un World directamente desde una matriz (sin archivo)."""
    muros: set[tuple[int, int]] = set()
    cultivos: set[tuple[int, int]] = set()
    inicio = deposito = avioneta = None
    for fila, valores in enumerate(grid):
        for columna, valor in enumerate(valores):
            if valor == 1:
                muros.add((fila, columna))
            elif valor == 2:
                inicio = (fila, columna)
            elif valor == 3:
                cultivos.add((fila, columna))
            elif valor == 4:
                deposito = (fila, columna)
            elif valor == 5:
                avioneta = (fila, columna)
    return World(
        [list(fila) for fila in grid],
        frozenset(muros),
        inicio,
        deposito,
        avioneta,
        frozenset(cultivos),
    )


def _mundo_recarga() -> Problema:
    """Cuarto pequeño con tres cultivos y depósito; obliga a recargar."""
    grid = [[1] * 10 for _ in range(10)]
    for fila in range(3, 6):
        for columna in range(3, 6):
            grid[fila][columna] = 0
    grid[3][3] = 2  # robot
    grid[3][4] = 4  # depósito
    grid[3][5] = 3  # cultivo
    grid[4][3] = 3  # cultivo
    grid[4][4] = 3  # cultivo
    grid[0][0] = 5  # avioneta aislada, fuera del cuarto
    return Problema(_world_from_grid(grid))


def _mundo_pasillos() -> Problema:
    """Anillo de pasillos donde la avioneta abarata el recorrido."""
    grid = [[1] * 10 for _ in range(10)]
    for columna in range(1, 9):
        grid[1][columna] = 0
        grid[8][columna] = 0
    for fila in range(1, 9):
        grid[fila][1] = 0
        grid[fila][8] = 0
    grid[9][1] = 2  # robot
    grid[8][1] = 4  # depósito
    grid[8][2] = 5  # avioneta
    grid[1][7] = 3  # cultivo
    return Problema(_world_from_grid(grid))


def _enumerar_estados(
    problema: Problema,
) -> tuple[set[Estado], dict[Estado, list[tuple[str, Estado, float]]]]:
    """Enumera el cierre de estados alcanzables con el Estado completo."""
    inicial = problema.estado_inicial()
    estados = {inicial}
    pendientes = [inicial]
    aristas: dict[Estado, list[tuple[str, Estado, float]]] = {}

    while pendientes:
        estado = pendientes.pop()
        sucesores = problema.sucesores(estado)
        aristas[estado] = sucesores
        for _accion, hijo, _costo in sucesores:
            if hijo not in estados:
                estados.add(hijo)
                pendientes.append(hijo)

    return estados, aristas


def _distancias_a_meta(
    problema: Problema,
    estados: set[Estado],
    aristas: dict[Estado, list[tuple[str, Estado, float]]],
) -> dict[Estado, float]:
    """Dijkstra inverso multifuente desde todos los estados meta."""
    reverso: dict[Estado, list[tuple[Estado, float]]] = {
        estado: [] for estado in estados
    }
    for estado, sucesores in aristas.items():
        for _accion, hijo, costo in sucesores:
            reverso[hijo].append((estado, costo))

    distancias = {estado: float("inf") for estado in estados}
    contador = itertools.count()
    cola: list = []
    for estado in estados:
        if problema.es_meta(estado):
            distancias[estado] = 0.0
            heapq.heappush(cola, (0.0, next(contador), estado))

    while cola:
        distancia, _, estado = heapq.heappop(cola)
        if distancia > distancias[estado]:
            continue
        for anterior, costo in reverso[estado]:
            nueva = distancia + costo
            if nueva < distancias[anterior]:
                distancias[anterior] = nueva
                heapq.heappush(
                    cola, (nueva, next(contador), anterior)
                )

    return distancias


def _verificar_admisibilidad(
    problema: Problema,
) -> tuple[int, float, list[tuple[Estado, float, float]]]:
    """Devuelve (cantidad de estados, h*(inicial), violaciones)."""
    estados, aristas = _enumerar_estados(problema)
    distancias = _distancias_a_meta(problema, estados, aristas)
    heuristica = HeuristicaAgroBot(problema.world)

    violaciones: list[tuple[Estado, float, float]] = []
    for estado in estados:
        h = heuristica(estado)
        h_estrella = distancias[estado]
        if h > h_estrella + 1e-9:
            violaciones.append((estado, h, h_estrella))

    return len(estados), distancias[problema.estado_inicial()], violaciones


@pytest.fixture(scope="module")
def prueba1_admisibilidad():
    """Enumera Prueba1 una sola vez para todas las pruebas del módulo."""
    problema = Problema(World.desde_archivo(str(RUTA_PRUEBA1)))
    estados, aristas = _enumerar_estados(problema)
    distancias = _distancias_a_meta(problema, estados, aristas)
    return problema, estados, distancias


def test_h_meta_y_sin_pendientes():
    mundo = World.desde_archivo(str(RUTA_PRUEBA1))
    heuristica = HeuristicaAgroBot(mundo)
    for estado in (
        Estado((0, 0), 0, -1, frozenset()),
        Estado((4, 3), 2, 30, frozenset()),
        Estado((9, 9), 1, 0, frozenset()),
    ):
        assert heuristica(estado) == 0.0


def test_h_inicial_prueba1_y_sin_dependencia_del_combustible():
    mundo = World.desde_archivo(str(RUTA_PRUEBA1))
    heuristica = HeuristicaAgroBot(mundo)
    pendientes = frozenset({A, B, C})
    for combustible in (-1, 0, 7, 30):
        estado = Estado((4, 0), 0, combustible, pendientes)
        assert heuristica(estado) == 9.0


def test_h_casos_de_la_tabla():
    mundo = World.desde_archivo(str(RUTA_PRUEBA1))
    heuristica = HeuristicaAgroBot(mundo)
    casos = [
        (Estado((0, 2), 2, -1, frozenset({A, B, C})), 6.0),
        (Estado((5, 3), 1, -1, frozenset({A, C})), 6.0),
        (Estado((5, 3), 2, -1, frozenset({C})), 3.0),
    ]
    for estado, esperado in casos:
        assert heuristica(estado) == esperado


def test_admisibilidad_exhaustiva_prueba1(prueba1_admisibilidad):
    problema, estados, distancias = prueba1_admisibilidad
    heuristica = HeuristicaAgroBot(problema.world)

    assert len(estados) == 12_302
    assert distancias[problema.estado_inicial()] == pytest.approx(25.0)

    violaciones = [
        (estado, heuristica(estado), distancias[estado])
        for estado in estados
        if heuristica(estado) > distancias[estado] + 1e-9
    ]
    assert violaciones == []


@pytest.mark.parametrize(
    "constructor",
    [_mundo_recarga, _mundo_pasillos],
    ids=["recarga", "avioneta"],
)
def test_admisibilidad_en_mundos_pequenos(constructor):
    cantidad, h_inicial, violaciones = _verificar_admisibilidad(constructor())
    assert cantidad > 0
    assert h_inicial < float("inf")
    assert violaciones == []
