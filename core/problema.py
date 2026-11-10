"""Problema de búsqueda del AgroBot: estado inicial, meta y sucesores.

Supuestos de diseño (ver README):
    1. El movimiento que llega a la casilla de la avioneta cuesta 1 (el costo
       se determina por el combustible ANTES de moverse). El 0.5 aplica desde
       el movimiento siguiente, y el combustible pasa a 30 al subirse.
    2. No hay bajada voluntaria. Una vez abordada, va en la avioneta hasta
       agotar el combustible. Después, pasar por su casilla no hace nada.
    3. `combustible`: -1 = aún no ha abordado, 1..30 = en la avioneta con ese
       combustible restante, 0 = agotada. Mientras `combustible > 0`, cada
       movimiento cuesta 0.5 y resta 1.
    4. Tratar el cultivo es automático y obligatorio. Sin fertilizante, el
       robot pasa por encima y el cultivo sigue seco.
    6. Orden fijo de operadores: arriba, abajo, izquierda, derecha.
"""

from __future__ import annotations

from core.estado import Estado
from core.mundo import World


class Problema:
    """Define el espacio de estados del AgroBot sobre un mundo dado."""

    #: Orden fijo de operadores: (nombre_accion, delta_fila, delta_columna).
    MOVIMIENTOS: tuple[tuple[str, int, int], ...] = (
        ("arriba", -1, 0),
        ("abajo", 1, 0),
        ("izquierda", 0, -1),
        ("derecha", 0, 1),
    )

    #: Capacidad máxima de fertilizante.
    CAPACIDAD_FERTILIZANTE: int = 2
    #: Combustible inicial al abordar la avioneta.
    COMBUSTIBLE_INICIAL: int = 30

    def __init__(self, world: World) -> None:
        """Crea el problema asociado a un mundo.

        Args:
            world: mundo ya validado sobre el que se mueve el robot.
        """
        self.world: World = world

    def estado_inicial(self) -> Estado:
        """Devuelve el estado inicial: en `inicio`, sin fertilizante,
        sin haber abordado (`combustible = -1`) y con todos los cultivos
        pendientes.
        """
        return Estado(
            pos=self.world.inicio,
            fertilizante=0,
            combustible=-1,
            cultivos_pendientes=self.world.cultivos,
        )

    def es_meta(self, s: Estado) -> bool:
        """Indica si el estado es meta: no quedan cultivos pendientes."""
        return len(s.cultivos_pendientes) == 0

    def sucesores(self, s: Estado) -> list[tuple[str, Estado, float]]:
        """Genera los sucesores en el orden arriba, abajo, izquierda, derecha.

        Orden de eventos al llegar a una casilla:
            1. Calcular costo/combustible por el movimiento (según el
               combustible ANTES de moverse: si > 0, cuesta 0.5 y resta 1;
               en otro caso cuesta 1 y el combustible no cambia).
            2. Si es el depósito: recarga fertilizante a 2. Si es un cultivo
               pendiente y hay fertilizante > 0: lo trata (fertilizante -1
               y lo quita de pendientes).
            3. Si es la casilla de la avioneta y `combustible == -1`
               (aún no abordada): subirse (`combustible = 30`).

        Args:
            s: estado actual.

        Returns:
            Lista de tuplas (accion, estado_nuevo, costo) en el orden fijo
            de operadores. Se omiten los movimientos hacia muros o fuera
            de la cuadrícula.
        """
        resultado: list[tuple[str, Estado, float]] = []

        for accion, df, dc in self.MOVIMIENTOS:
            nr, nc = s.pos[0] + df, s.pos[1] + dc
            if not self.world.es_libre(nr, nc):
                continue

            # 1. Costo y combustible por el movimiento.
            if s.combustible > 0:
                costo = 0.5
                nuevo_combustible = s.combustible - 1
            else:
                costo = 1.0
                nuevo_combustible = s.combustible  # -1 (sin abordar) o 0 (agotada)

            # 2. Depósito o cultivo.
            nuevo_fertilizante = s.fertilizante
            nuevos_pendientes = s.cultivos_pendientes
            if (nr, nc) == self.world.deposito:
                nuevo_fertilizante = self.CAPACIDAD_FERTILIZANTE
            elif (nr, nc) in nuevos_pendientes and nuevo_fertilizante > 0:
                # Tratar es automático y obligatorio si hay fertilizante.
                # El robot puede tratar incluso yendo en la avioneta.
                nuevos_pendientes = nuevos_pendientes - {(nr, nc)}
                nuevo_fertilizante = nuevo_fertilizante - 1

            # 3. Abordar la avioneta (solo la primera vez).
            if (nr, nc) == self.world.avioneta and s.combustible == -1:
                nuevo_combustible = self.COMBUSTIBLE_INICIAL

            nuevo_estado = Estado(
                pos=(nr, nc),
                fertilizante=nuevo_fertilizante,
                combustible=nuevo_combustible,
                cultivos_pendientes=nuevos_pendientes,
            )
            resultado.append((accion, nuevo_estado, costo))

        return resultado
