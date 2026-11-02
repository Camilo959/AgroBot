"""Búsqueda en amplitud (BFS) para el AgroBot.

Estructura: cola FIFO (`collections.deque`). Completo y óptimo en número
de pasos, pero no en costo (los pasos cuestan 1 o 0.5).
"""

from __future__ import annotations

from collections import deque

from algorithms.base import (
    Resultado,
    ahora,
    clave_relajada,
    construir_exito,
    construir_fracaso,
    crea_ciclo_en_rama,
    validar_modo_ciclos,
)
from core.node import Nodo
from core.problem import Problema


def busqueda_amplitud(
    problema: Problema,
    modo_ciclos: str = "rama",
    limite_nodos: int | None = None,
) -> Resultado:
    """Busca con BFS: expande por niveles con cola FIFO.

    Args:
        problema: problema a resolver.
        modo_ciclos: "rama" (por defecto; ancestros con clave relajada)
            o "global" (cerrados con clave relajada).
        limite_nodos: máximo de nodos a expandir. Al alcanzarlo se
            devuelve `exito=False` con `limite_alcanzado=True`.

    Returns:
        El `Resultado` de la búsqueda.
    """
    validar_modo_ciclos(modo_ciclos)
    t0 = ahora()

    raiz = Nodo(problema.estado_inicial())
    nodos_generados = 1
    profundidad_maxima = 0
    nodos_expandidos = 0
    cerrados: set = set()
    cola: deque[Nodo] = deque([raiz])

    while cola:
        if limite_nodos is not None and nodos_expandidos >= limite_nodos:
            return construir_fracaso(
                nodos_expandidos, nodos_generados, profundidad_maxima,
                ahora() - t0, limite_alcanzado=True,
            )
        n = cola.popleft()
        if modo_ciclos == "global":
            # Un repetido descartado al extraer no cuenta como expandido.
            k = clave_relajada(n.estado)
            if k in cerrados:
                continue
            cerrados.add(k)
        # Expandir = verificar si es meta + crear hijos. El meta cuenta.
        nodos_expandidos += 1
        if problema.es_meta(n.estado):
            return construir_exito(
                n, nodos_expandidos, nodos_generados, profundidad_maxima,
                ahora() - t0,
            )
        for accion, estado_hijo, costo in problema.sucesores(n.estado):
            if modo_ciclos == "rama" and crea_ciclo_en_rama(
                n, estado_hijo, clave_relajada
            ):
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
