"""Estado del AgroBot.

Supuestos de diseño:
    3. `combustible`: -1 = aún no ha abordado la avioneta,
       1..30 = en la avioneta con ese combustible restante,
       0 = avioneta agotada. Mientras `combustible > 0`, cada movimiento
       cuesta 0.5 y resta 1 al combustible.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Estado:
    """Estado completo del agente (hasheable para detección de ciclos).

    Atributos:
        pos: tupla (fila, columna) con la posición actual del robot.
        fertilizante: unidades de fertilizante cargadas (0, 1 o 2).
        combustible: -1 si aún no aborda la avioneta, 1..30 si va en ella
            con ese combustible restante, 0 si ya se agotó.
        cultivos_pendientes: frozenset de (fila, columna) con los cultivos
            secos que aún faltan por tratar.

    Nota:
        Esta clase no contiene lógica de transición; solo datos. Las
        transiciones viven en :class:`core.problema.Problema`.
    """

    pos: tuple[int, int]
    fertilizante: int
    combustible: int
    cultivos_pendientes: frozenset[tuple[int, int]]
