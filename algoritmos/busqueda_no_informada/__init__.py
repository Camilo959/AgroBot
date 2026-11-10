"""Búsquedas no informadas del AgroBot."""

from algoritmos.busqueda_no_informada.amplitud import busqueda_amplitud
from algoritmos.busqueda_no_informada.costo_uniforme import (
    busqueda_costo_uniforme,
)
from algoritmos.busqueda_no_informada.profundidad import busqueda_profundidad

__all__ = [
    "busqueda_amplitud",
    "busqueda_costo_uniforme",
    "busqueda_profundidad",
]
