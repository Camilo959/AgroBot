"""Búsqueda de costo uniforme (UCS) para el AgroBot.

Estructura: cola de prioridad (`heapq`) con prioridad `g(n)`. Completo y
óptimo. El test de meta va al extraer: hacerlo al generar perdería la
optimalidad. Los ciclos se detectan solo por rama con la clave relajada.
Desempate por orden de creación (FIFO) entre nodos con el mismo costo `g`.
"""

from __future__ import annotations

import heapq
import itertools

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


def busqueda_costo_uniforme(
    problema: Problema,
    limite_nodos: int | None = None,
) -> Resultado:
    """Busca con UCS: expande el nodo de menor `g` con `heapq`.

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
    contador = itertools.count()
    frontera: list = [(raiz.g, next(contador), raiz)]

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
            heapq.heappush(frontera, (hijo.g, next(contador), hijo))

    return construir_fracaso(
        nodos_expandidos, nodos_generados, profundidad_maxima, ahora() - t0
    )
