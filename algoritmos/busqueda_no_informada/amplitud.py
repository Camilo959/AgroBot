"""Búsqueda en amplitud (BFS) para el AgroBot.

Estructura: cola FIFO (`collections.deque`). Completo y óptimo en número
de pasos, pero no en costo (los pasos cuestan 1 o 0.5). Los ciclos se
detectan solo por rama con la clave relajada.
"""

from __future__ import annotations

from collections import deque

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


def busqueda_amplitud(
    problema: Problema,
    limite_nodos: int | None = None,
) -> Resultado:
    """Busca con BFS: expande por niveles con cola FIFO.

    Args:
        problema: problema a resolver.
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
    cola: deque[Nodo] = deque([raiz])

    while cola:
        if limite_nodos is not None and nodos_expandidos >= limite_nodos:
            return construir_fracaso(
                nodos_expandidos, nodos_generados, profundidad_maxima,
                ahora() - t0, limite_alcanzado=True,
            )
        n = cola.popleft()
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
            cola.append(hijo)

    return construir_fracaso(
        nodos_expandidos, nodos_generados, profundidad_maxima, ahora() - t0
    )
