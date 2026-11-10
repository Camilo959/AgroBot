"""Búsqueda en profundidad evitando ciclos (DFS) para el AgroBot.

Estructura: pila (lista con `append`/`pop`), iterativo. Solo se revisan
los ancestros de la rama actual. Los hijos se apilan en orden inverso para
que el primer operador quede arriba de la pila. No es óptimo y puede dar
soluciones largas: es lo esperado.
"""

from __future__ import annotations

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


def busqueda_profundidad(
    problema: Problema,
    limite_nodos: int | None = None,
) -> Resultado:
    """Busca con DFS iterativo evitando ciclos en la rama.

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
    pila: list[Nodo] = [raiz]

    while pila:
        if limite_nodos is not None and nodos_expandidos >= limite_nodos:
            return construir_fracaso(
                nodos_expandidos, nodos_generados, profundidad_maxima,
                ahora() - t0, limite_alcanzado=True,
            )
        n = pila.pop()
        # Expandir = verificar si es meta + crear hijos. El meta cuenta.
        nodos_expandidos += 1
        if problema.es_meta(n.estado):
            return construir_exito(
                n, nodos_expandidos, nodos_generados, profundidad_maxima,
                ahora() - t0,
            )
        hijos: list[Nodo] = []
        for accion, estado_hijo, costo in problema.sucesores(n.estado):
            if crea_ciclo_en_rama(n, estado_hijo, clave_relajada):
                continue
            hijo = Nodo(
                estado_hijo, n, accion, n.g + costo, n.profundidad + 1
            )
            nodos_generados += 1
            if hijo.profundidad > profundidad_maxima:
                profundidad_maxima = hijo.profundidad
            hijos.append(hijo)
        # Orden inverso: el primer operador queda arriba de la pila.
        pila.extend(reversed(hijos))

    return construir_fracaso(
        nodos_expandidos, nodos_generados, profundidad_maxima, ahora() - t0
    )
