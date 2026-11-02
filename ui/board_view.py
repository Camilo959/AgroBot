"""Tablero del AgroBot dibujado sobre un `tkinter.Canvas`."""

from __future__ import annotations

import tkinter as tk

from PIL import ImageTk

from core.world import World
from ui import assets_loader, theme


class TableroCanvas(tk.Canvas):
    """Canvas que dibuja un mundo estático con los sprites del tema.

    Capas (de abajo hacia arriba): casilla libre, muro, cultivo seco,
    depósito, avioneta (con sombra) y robot.
    """

    def __init__(self, master: object, **kwargs: object) -> None:
        opciones = {
            "bg": theme.COLOR_TABLERO,
            "highlightthickness": 0,
            "bd": 0,
        }
        opciones.update(kwargs)
        super().__init__(master, **opciones)
        self.world: World | None = None
        self._fotos: dict[tuple[str, int], ImageTk.PhotoImage] = {}
        self._ultimo_tamano: tuple[int, int] = (0, 0)
        self.bind("<Configure>", self._al_redimensionar)

    def mostrar_mundo(self, world: World | None) -> None:
        """Establece el mundo a dibujar y lo redibuja."""
        self.world = world
        self.redibujar()

    def _al_redimensionar(self, evento: tk.Event) -> None:
        tamano = (evento.width, evento.height)
        if tamano != self._ultimo_tamano:
            self._ultimo_tamano = tamano
            self.redibujar()

    def _foto(self, nombre: str, tam: int) -> ImageTk.PhotoImage:
        clave = (nombre, tam)
        if clave not in self._fotos:
            if nombre == "__sombra_avioneta__":
                imagen = assets_loader.sombra_avioneta(tam)
            else:
                imagen = assets_loader.obtener_sprite(nombre, tam)
            self._fotos[clave] = ImageTk.PhotoImage(imagen)
        return self._fotos[clave]

    def _dibujar(self, nombre: str, fila: int, columna: int, tam: int,
                 dx: int, dy: int) -> None:
        x = dx + columna * tam
        y = dy + fila * tam
        self.create_image(x, y, anchor="nw", image=self._foto(nombre, tam))

    def redibujar(self) -> None:
        """Redibuja el mundo completo ajustando la celda al espacio disponible."""
        self.delete("all")
        if self.world is None:
            return

        ancho = self.winfo_width()
        alto = self.winfo_height()
        if ancho <= 1 or alto <= 1:
            return

        margen = theme.PADDING_CHICO
        tam = theme.ajustar_tam_celda(
            max(1, ancho - 2 * margen),
            max(1, alto - 2 * margen),
            self.world.filas,
            self.world.columnas,
        )
        dx = (ancho - self.world.columnas * tam) // 2
        dy = (alto - self.world.filas * tam) // 2

        for fila in range(self.world.filas):
            for columna in range(self.world.columnas):
                nombre = "muro" if (fila, columna) in self.world.muros else "casilla"
                self._dibujar(nombre, fila, columna, tam, dx, dy)

        for fila, columna in self.world.cultivos:
            self._dibujar("cultivo_seco", fila, columna, tam, dx, dy)

        fila, columna = self.world.deposito
        self._dibujar("fertilizante", fila, columna, tam, dx, dy)

        fila, columna = self.world.avioneta
        if theme.SOMBRA_AVIONETA:
            self._dibujar(
                "__sombra_avioneta__", fila, columna, tam, dx,
                dy + int(tam * 0.08),
            )
        self._dibujar("avioneta", fila, columna, tam, dx, dy)

        fila, columna = self.world.inicio
        self._dibujar("robot", fila, columna, tam, dx, dy)
