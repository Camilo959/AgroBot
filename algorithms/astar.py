"""Búsqueda A* para el AgroBot.

Expande el nodo con menor f(n) = g(n) + h(n). Con una heurística
admisible es completa y óptima. La heurística se recibe como callable
h(estado) -> float.
"""

from __future__ import annotations

import heapq
import itertools
from collections.abc import Callable

from algorithms.base import (
    Resultado,
    ahora,
    clave_relajada,
    construir_exito,
    construir_fracaso,
    crea_ciclo_en_rama,
)
from core.node import Nodo
from core.problem import Problema
from core.state import Estado


def busqueda_a_estrella(
    problema: Problema,
    heuristica: Callable[[Estado], float],
    limite_nodos: int | None = None,
) -> Resultado:
    """Busca con A*: expande el nodo de menor g(n) + h(n).

    Args:
        problema: problema a resolver.
        heuristica: función h(estado) -> float.
        limite_nodos: máximo de nodos a expandir. Al alcanzarlo se
            devuelve `exito=False` con `limite_alcanzado=True`.

    Returns:
        El `Resultado` de la búsqueda.
    """
    t0 = ahora()

    raiz = Nodo(problema.estado_inicial())
    nodos_generados = 1
    profundidad_maxima = 0
    nodos_expandidos = 0
    contador = itertools.count()
    frontera: list = [
        (raiz.g + heuristica(raiz.estado), next(contador), raiz)
    ]

    while frontera:
        if limite_nodos is not None and nodos_expandidos >= limite_nodos:
            return construir_fracaso(
                nodos_expandidos, nodos_generados, profundidad_maxima,
                ahora() - t0, limite_alcanzado=True,
            )
        _, _, n = heapq.heappop(frontera)
        # Expandir = verificar si es meta + crear hijos. El meta cuenta.
        nodos_expandidos += 1
        if problema.es_meta(n.estado):
            return construir_exito(
                n, nodos_expandidos, nodos_generados, profundidad_maxima,
                ahora() - t0,
            )
        for accion, estado_hijo, costo in problema.sucesores(n.estado):
            if crea_ciclo_en_rama(n, estado_hijo, clave_relajada):
                continue
            hijo = Nodo(
                estado_hijo, n, accion, n.g + costo, n.profundidad + 1
            )
            nodos_generados += 1
            if hijo.profundidad > profundidad_maxima:
                profundidad_maxima = hijo.profundidad
            prioridad = hijo.g + heuristica(estado_hijo)
            heapq.heappush(
                frontera, (prioridad, next(contador), hijo)
            )

    return construir_fracaso(
        nodos_expandidos, nodos_generados, profundidad_maxima, ahora() - t0
    )
