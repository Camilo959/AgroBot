"""Registro de pantallas de la aplicación.

Cambiar una pantalla = escribir otra clase con el mismo contrato
(`__init__(self, master, app)` y `al_mostrar(self)`) y editar una línea
de este diccionario.
"""

from __future__ import annotations

from ui.screens.juego import JuegoScreen
from ui.screens.resumen import ResumenScreen

PANTALLAS: dict[str, type] = {
    "juego": JuegoScreen,
    "resumen": ResumenScreen,
}

__all__ = ["PANTALLAS", "JuegoScreen", "ResumenScreen"]
