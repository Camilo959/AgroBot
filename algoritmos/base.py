"""Base común de los algoritmos de búsqueda no informada (AgroBot).

Contiene el `Resultado`, la clave de ciclo relajada, la detección de
ciclos en rama y los constructores de `Resultado` con y sin solución.

Convenciones (ver `docs/CONTEXTO_BUSQUEDA_NO_INFORMADA.md`):
    - El test de meta se hace al extraer el nodo; el nodo meta cuenta
      como expandido.
    - Los ciclos se detectan solo por rama: se comparan los ancestros del
      nodo, incluido el padre.
    - Clave relajada: `(pos, fertilizante, cultivos_pendientes,
      fase_avioneta)`, donde la fase se deriva de `combustible` (-1: sin
      abordar, 1..30: en vuelo, 0: agotada). La relajada evita la
      oscilación en la avioneta.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Hashable
from dataclasses import dataclass, field

from core.nodo import Nodo
from core.estado import Estado


@dataclass
class Resultado:
    """Resultado de una búsqueda.

    Atributos:
        exito: si se encontró solución.
        camino: acciones desde el estado inicial (vacío si no hay solución).
        estados: estados recorridos, incluido el inicial (para la animación).
        nodos_expandidos: nodos extraídos y expandidos, incluido el meta.
        nodos_generados: nodos `Nodo` creados, incluida la raíz. Los hijos
            descartados por ciclo no se crean ni se cuentan.
        profundidad: profundidad del nodo solución (0 si no hay solución).
        profundidad_maxima: mayor profundidad entre los nodos creados.
        tiempo: segundos con `time.perf_counter`, solo alrededor de la búsqueda.
        costo: costo `g` de la solución; `None` si no hay solución.
        limite_alcanzado: si la búsqueda se cortó por `limite_nodos`.
    """

    exito: bool
    camino: list[str] = field(default_factory=list)
    estados: list[Estado] = field(default_factory=list)
    nodos_expandidos: int = 0
    nodos_generados: int = 0
    profundidad: int = 0
    profundidad_maxima: int = 0
    tiempo: float = 0.0
    costo: float | None = None
    limite_alcanzado: bool = False


def clave_relajada(estado: Estado) -> tuple:
    """Devuelve la clave relajada: sin el valor exacto de `combustible`.

    La fase de la avioneta se deriva de `combustible`: -1 es "sin_abordar",
    1..30 es "en_vuelo" y 0 es "agotada". Dentro de una misma fase el
    combustible nunca sube, así que un descendiente con igual clave relajada
    es igual o peor que su ancestro y descartarlo no pierde soluciones.
    """
    if estado.combustible == -1:
        fase = "sin_abordar"
    elif estado.combustible == 0:
        fase = "agotada"
    else:
        fase = "en_vuelo"
    return (estado.pos, estado.fertilizante, estado.cultivos_pendientes, fase)


def crea_ciclo_en_rama(
    nodo_padre: Nodo,
    estado_hijo: Estado,
    clave: Callable[[Estado], Hashable],
) -> bool:
    """Indica si `estado_hijo` repite un estado de su propia rama.

    Recorre la cadena de `padre` hacia arriba, incluyendo `nodo_padre`,
    y compara las claves. No basta con comparar con el padre: hay que
    revisar toda la rama.
    """
    clave_hijo = clave(estado_hijo)
    actual: Nodo | None = nodo_padre
    while actual is not None:
        if clave(actual.estado) == clave_hijo:
            return True
        actual = actual.padre
    return False


def construir_exito(
    nodo_solucion: Nodo,
    nodos_expandidos: int,
    nodos_generados: int,
    profundidad_maxima: int,
    segundos: float,
) -> Resultado:
    """Construye el `Resultado` de una búsqueda exitosa."""
    return Resultado(
        exito=True,
        camino=nodo_solucion.reconstruir_camino(),
        estados=nodo_solucion.reconstruir_estados(),
        nodos_expandidos=nodos_expandidos,
        nodos_generados=nodos_generados,
        profundidad=nodo_solucion.profundidad,
        profundidad_maxima=profundidad_maxima,
        tiempo=segundos,
        costo=nodo_solucion.g,
        limite_alcanzado=False,
    )


def construir_fracaso(
    nodos_expandidos: int,
    nodos_generados: int,
    profundidad_maxima: int,
    segundos: float,
    limite_alcanzado: bool = False,
) -> Resultado:
    """Construye el `Resultado` sin solución (agotada o por límite)."""
    return Resultado(
        exito=False,
        camino=[],
        estados=[],
        nodos_expandidos=nodos_expandidos,
        nodos_generados=nodos_generados,
        profundidad=0,
        profundidad_maxima=profundidad_maxima,
        tiempo=segundos,
        costo=None,
        limite_alcanzado=limite_alcanzado,
    )


def ahora() -> float:
    """Devuelve la marca de tiempo actual (`time.perf_counter`)."""
    return time.perf_counter()
