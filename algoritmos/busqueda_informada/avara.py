"""Búsqueda Avara (Greedy Best-First) para el AgroBot.

Expande el nodo con menor h(n), sin importar la profundidad. No es óptima
ni completa en general, pero con ciclos por rama explora un árbol finito.
La heurística se recibe como callable h(estado) -> float.
"""

from __future__ import annotations

import heapq
import itertools
from collections.abc import Callable

from algoritmos.base import (
    Resultado,
    ahora,
    clave_relajada,
    construir_exito,
    construir_fracaso,
    crea_ciclo_en_rama,
)
from core.nodo import Nodo
from core.problema import Problema
from core.estado import Estado


def busqueda_avara(
    problema: Problema,
    heuristica: Callable[[Estado], float],
    limite_nodos: int | None = None,
) -> Resultado:
    """Busca con Avara: expande el nodo de menor h(n).

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
    frontera: list = [(heuristica(raiz.estado), next(contador), raiz)]

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
            heapq.heappush(
                frontera,
                (heuristica(estado_hijo), next(contador), hijo),
            )

    return construir_fracaso(
        nodos_expandidos, nodos_generados, profundidad_maxima, ahora() - t0
    )
