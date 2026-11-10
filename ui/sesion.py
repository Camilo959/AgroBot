"""Estado compartido entre las pantallas del AgroBot."""

from __future__ import annotations

from dataclasses import dataclass

from algoritmos.base import Resultado
from core.mundo import World
from ui import theme


@dataclass
class SesionJuego:
    """Datos que comparten la pantalla principal y la de resumen.

    Atributos:
        ruta_mundo: ruta del archivo del mundo cargado.
        world: mundo ya validado.
        tipo_busqueda: "no_informada" o "informada".
        algoritmo: identificador del algoritmo elegido ("amplitud",
            "costo_uniforme", "profundidad", ...).
        limite_nodos: tope de nodos a expandir.
        resultado: resultado de la última búsqueda.
        estado_busqueda: "inactivo", "buscando", "listo", "cancelado" o
            "error".
        error: mensaje de error legible, si lo hay.
    """

    ruta_mundo: str | None = None
    world: World | None = None
    tipo_busqueda: str = "no_informada"
    algoritmo: str | None = None
    limite_nodos: int = theme.LIMITE_NODOS_DEFECTO
    resultado: Resultado | None = None
    estado_busqueda: str = "inactivo"
    error: str | None = None

    def reiniciar_busqueda(self) -> None:
        """Limpia el resultado y el error de búsqueda, sin tocar el mundo."""
        self.resultado = None
        self.estado_busqueda = "inactivo"
        self.error = None
