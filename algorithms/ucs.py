"""Búsqueda de costo uniforme (UCS) para el AgroBot.

Estructura: cola de prioridad (`heapq`) con prioridad `g(n)`. Completo y
óptimo. El test de meta va al extraer: hacerlo al generar perdería la
optimalidad. Desempate por orden de creación (FIFO), como supuesto
documentado (el profesor no lo especifica).
"""

from __future__ import annotations

import heapq
import itertools

from algorithms.base import (
    Resultado,
    ahora,
    clave_completa,
    clave_relajada,
    construir_exito,
    construir_fracaso,
    crea_ciclo_en_rama,
    validar_modo_ciclos,
)
from core.node import Nodo
from core.problem import Problema


def busqueda_costo_uniforme(
    problema: Problema,
    modo_ciclos: str = "rama",
    limite_nodos: int | None = None,
) -> Resultado:
    """Busca con UCS: expande el nodo de menor `g` con `heapq`.

    Args:
        problema: problema a resolver.
        modo_ciclos: "rama" (por defecto; ancestros con clave relajada)
            o "global" (cerrados con clave completa: preserva la
            optimalidad).
        limite_nodos: máximo de nodos a expandir. Al alcanzarlo se
            devuelve `exito=False` con `limite_alcanzado=True`.

    Returns:
        El `Resultado` de la búsqueda.
    """
    validar_modo_ciclos(modo_ciclos)
    t0 = ahora()
    clave = clave_completa if modo_ciclos == "global" else clave_relajada

    raiz = Nodo(problema.estado_inicial())
    nodos_generados = 1
    profundidad_maxima = 0
    nodos_expandidos = 0
    cerrados: set = set()
    contador = itertools.count()
    frontera: list = [(raiz.g, next(contador), raiz)]

    while frontera:
        if limite_nodos is not None and nodos_expandidos >= limite_nodos:
            return construir_fracaso(
                nodos_expandidos, nodos_generados, profundidad_maxima,
                ahora() - t0, limite_alcanzado=True,
            )
        _, _, n = heapq.heappop(frontera)
        if modo_ciclos == "global":
            # Un repetido descartado al extraer no cuenta como expandido.
            k = clave(n.estado)
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
            heapq.heappush(frontera, (hijo.g, next(contador), hijo))

    return construir_fracaso(
        nodos_expandidos, nodos_generados, profundidad_maxima, ahora() - t0
    )
