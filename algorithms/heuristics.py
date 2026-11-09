"""Heurística B del AgroBot (Manhattan + MST).

La heurística estima el costo mínimo de terminar la misión desde un
estado. No depende del combustible exacto: solo de la posición, el
fertilizante y los cultivos pendientes.

Idea general:
    - Todo movimiento cuesta al menos 0.5 (la avioneta reduce el costo a
      la mitad), así que h = 0.5 * L, donde L es una cota inferior del
      número de movimientos que faltan.
    - L se calcula con distancias Manhattan (que ignoran muros y por eso
      nunca sobreestiman) y con un árbol de expansión mínima (MST) sobre
      los puntos que el robot todavía debe visitar.

El 0.5 sigue la idea del ejemplo del profesor: "Manhattan / 2 para que
sea admisible" (d.187), adaptada a varios cultivos y al depósito.
"""

from __future__ import annotations

from core.state import Estado
from core.world import World


class HeuristicaAgroBot:
    """Heurística admisible para Avara y A*.

    Args:
        world: mundo ya validado; se guarda la posición del depósito.
    """

    def __init__(self, world: World) -> None:
        self.deposito: tuple[int, int] = world.deposito

    @staticmethod
    def _manhattan(a: tuple[int, int], b: tuple[int, int]) -> int:
        """Distancia Manhattan entre dos casillas."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    @classmethod
    def _mst(cls, puntos: set[tuple[int, int]]) -> float:
        """Costo del árbol de expansión mínima con Prim (O(k²)).

        Los puntos se deduplican para cubrir casos como posición igual al
        depósito o a un cultivo pendiente.
        """
        lista = list(puntos)
        cantidad = len(lista)
        if cantidad <= 1:
            return 0.0

        visitado = [False] * cantidad
        distancia = [float("inf")] * cantidad
        distancia[0] = 0.0
        total = 0.0

        for _ in range(cantidad):
            # Elegir el nodo no visitado de menor distancia al árbol.
            u = -1
            mejor = float("inf")
            for i in range(cantidad):
                if not visitado[i] and distancia[i] < mejor:
                    mejor = distancia[i]
                    u = i
            visitado[u] = True
            total += mejor

            # Actualizar las distancias de los nodos aún no visitados.
            for v in range(cantidad):
                if not visitado[v]:
                    d = cls._manhattan(lista[u], lista[v])
                    if d < distancia[v]:
                        distancia[v] = d

        return total

    def __call__(self, estado: Estado) -> float:
        """Devuelve h(estado) = 0.5 * L."""
        pendientes = estado.cultivos_pendientes
        if not pendientes:
            # No quedan cultivos por tratar: la meta ya se alcanzó.
            return 0.0

        posicion = estado.pos
        fertilizante = estado.fertilizante
        cantidad = len(pendientes)

        if fertilizante == 0:
            # Sin fertilizante hay que ir primero al depósito y luego
            # recorrer todos los cultivos.
            puntos = {self.deposito} | set(pendientes)
            longitud = self._manhattan(posicion, self.deposito)
            longitud += self._mst(puntos)
        elif fertilizante < cantidad:
            # Alcanza para algunos cultivos, pero habrá que pasar por el
            # depósito al menos una vez; se conectan posición, depósito y
            # cultivos en un solo árbol.
            longitud = self._mst(
                {posicion} | set(pendientes) | {self.deposito}
            )
        else:
            # Hay fertilizante suficiente para todos los cultivos; el
            # depósito no es necesario.
            longitud = self._mst({posicion} | set(pendientes))

        return 0.5 * longitud
