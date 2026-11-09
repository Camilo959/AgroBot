"""Ejecución de búsquedas en un proceso aparte (contexto "spawn").

La ventana de customtkinter nunca ejecuta la búsqueda: la lanza aquí, la
consulta con `consultar()` y puede cancelarla con `terminate()`.
"""

from __future__ import annotations

import multiprocessing
from multiprocessing.context import BaseContext
from multiprocessing.process import BaseProcess
from queue import Empty
from typing import Callable

from algorithms.astar import busqueda_a_estrella
from algorithms.base import Resultado
from algorithms.bfs import busqueda_amplitud
from algorithms.dfs import busqueda_profundidad
from algorithms.greedy import busqueda_avara
from algorithms.heuristics import HeuristicaAgroBot
from algorithms.ucs import busqueda_costo_uniforme
from core.problem import Problema
from core.world import World

ALGORITMOS_NO_INFORMADOS: dict[str, Callable[..., Resultado]] = {
    "amplitud": busqueda_amplitud,
    "costo_uniforme": busqueda_costo_uniforme,
    "profundidad": busqueda_profundidad,
}

ALGORITMOS_INFORMADOS: dict[str, Callable[..., Resultado]] = {
    "avara": busqueda_avara,
    "astar": busqueda_a_estrella,
}

ALGORITMOS: dict[str, Callable[..., Resultado]] = {
    **ALGORITMOS_NO_INFORMADOS,
    **ALGORITMOS_INFORMADOS,
}

_contexto: BaseContext = multiprocessing.get_context("spawn")
_proceso: BaseProcess | None = None
_cola: object | None = None
_error: str | None = None


def _ejecutar_busqueda(cola: object, ruta: str, algoritmo: str,
                       limite_nodos: int | None) -> None:
    """Función objetivo del proceso hijo (debe estar a nivel de módulo)."""
    try:
        mundo = World.desde_archivo(ruta)
        problema = Problema(mundo)
        if algoritmo in ALGORITMOS_INFORMADOS:
            heuristica = HeuristicaAgroBot(mundo)
            resultado = ALGORITMOS_INFORMADOS[algoritmo](
                problema, heuristica, limite_nodos=limite_nodos
            )
        else:
            resultado = ALGORITMOS_NO_INFORMADOS[algoritmo](
                problema, limite_nodos=limite_nodos
            )
        cola.put(("ok", resultado))
    except Exception as exc:  # pragma: no cover - se informa en la interfaz
        cola.put(("error", f"{type(exc).__name__}: {exc}"))


def iniciar(ruta: str, algoritmo: str, limite_nodos: int | None) -> None:
    """Lanza una búsqueda en un proceso hijo nuevo."""
    global _proceso, _cola, _error
    cancelar()
    if algoritmo not in ALGORITMOS:
        raise ValueError(f"Algoritmo no soportado: {algoritmo!r}")
    _error = None
    _cola = _contexto.Queue()
    _proceso = _contexto.Process(
        target=_ejecutar_busqueda,
        args=(_cola, ruta, algoritmo, limite_nodos),
        daemon=True,
    )
    _proceso.start()


def _limpiar() -> None:
    """Cierra la cola y olvida el proceso terminado."""
    global _proceso, _cola
    if _cola is not None:
        try:
            _cola.close()
        except (OSError, ValueError):
            pass
    _cola = None
    _proceso = None


def consultar() -> Resultado | None:
    """Devuelve el `Resultado` si terminó; si no, `None` (no bloquea)."""
    global _error
    if _cola is None:
        return None
    try:
        tipo, carga = _cola.get_nowait()
    except Empty:
        return None
    except (OSError, ValueError):
        return None

    if tipo == "error":
        _error = str(carga)
        _limpiar()
        return None

    _limpiar()
    return carga


def cancelar() -> None:
    """Termina el proceso hijo si sigue vivo y limpia el estado."""
    global _proceso
    if _proceso is not None:
        if _proceso.is_alive():
            _proceso.terminate()
        _proceso.join(timeout=2)
    _limpiar()


def en_ejecucion() -> bool:
    """Indica si hay una búsqueda en curso."""
    return _proceso is not None and _proceso.is_alive()


def ultimo_error() -> str | None:
    """Último error reportado por el proceso de búsqueda, si lo hubo."""
    return _error


def limpiar_error() -> None:
    """Borra el último error de búsqueda."""
    global _error
    _error = None
