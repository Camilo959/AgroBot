"""Nodo de búsqueda para los algoritmos del AgroBot."""

from __future__ import annotations

from typing import ClassVar

from core.estado import Estado


class Nodo:
    """Nodo de un árbol de búsqueda.

    Atributos:
        estado: estado del problema que representa este nodo.
        padre: nodo padre (None en la raíz).
        accion: acción usada para llegar desde el padre (None en la raíz).
        g: costo acumulado desde el estado inicial hasta este nodo.
        profundidad: número de acciones desde la raíz.
    """

    __slots__ = ("estado", "padre", "accion", "g", "profundidad", "_seq")

    #: Contador de creación para desempate determinista en `heapq`.
    _proximo_seq: ClassVar[int] = 0

    def __init__(
        self,
        estado: Estado,
        padre: Nodo | None = None,
        accion: str | None = None,
        g: float = 0.0,
        profundidad: int = 0,
    ) -> None:
        """Crea un nodo de búsqueda."""
        self.estado: Estado = estado
        self.padre: Nodo | None = padre
        self.accion: str | None = accion
        self.g: float = g
        self.profundidad: int = profundidad
        self._seq: int = Nodo._proximo_seq
        Nodo._proximo_seq += 1

    def __lt__(self, otro: Nodo) -> bool:
        """Orden para `heapq`: desempatar por `g` y luego por orden de
        creación (`_seq`).

        Esto hace que los nodos sean comparables directamente y puedan
        meterse en una cola de prioridad como `(prioridad, nodo)` sin
        errores de comparación cuando las prioridades empatan. Si dos nodos
        tienen igual `g`, gana el creado primero (comportamiento FIFO).
        """
        if self.g != otro.g:
            return self.g < otro.g
        return self._seq < otro._seq

    def reconstruir_camino(self) -> list[str]:
        """Devuelve la lista de acciones desde el inicial hasta este nodo."""
        acciones: list[str] = []
        actual: Nodo | None = self
        while actual is not None and actual.padre is not None:
            assert actual.accion is not None
            acciones.append(actual.accion)
            actual = actual.padre
        acciones.reverse()
        return acciones

    def reconstruir_estados(self) -> list[Estado]:
        """Devuelve la lista de estados desde el inicial hasta este nodo
        (la usará la animación de la UI).
        """
        estados: list[Estado] = []
        actual: Nodo | None = self
        while actual is not None:
            estados.append(actual.estado)
            actual = actual.padre
        estados.reverse()
        return estados
