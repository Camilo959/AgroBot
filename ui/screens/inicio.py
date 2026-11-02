"""Pantalla de inicio del AgroBot."""

from __future__ import annotations

import customtkinter as ctk

from ui import assets_loader, theme, textos
from ui.componentes import (
    BotonPrimario,
    BotonSecundario,
    Contenedor,
    Imagen,
    Subtitulo,
    Tarjeta,
    TituloGrande,
)


class InicioScreen(ctk.CTkFrame):
    """Portada con el robot y los botones Comenzar / Salir."""

    def __init__(self, master: object, app: object) -> None:
        super().__init__(master, fg_color=theme.COLOR_FONDO)
        self.app = app
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        tarjeta = Tarjeta(self)
        tarjeta.grid(row=0, column=0)
        interior = Contenedor(tarjeta)
        interior.pack(
            padx=theme.PADDING * 3,
            pady=theme.PADDING * 2,
        )

        TituloGrande(interior, text=textos.t("inicio_titulo")).pack()
        Subtitulo(interior, text=textos.t("inicio_subtitulo")).pack(
            pady=(theme.PADDING_CHICO, theme.PADDING)
        )

        imagen = assets_loader.cargar_robot(theme.TAM_ROBOT_INICIO)
        self._imagen_robot = ctk.CTkImage(
            light_image=imagen,
            size=(theme.TAM_ROBOT_INICIO, theme.TAM_ROBOT_INICIO),
        )
        Imagen(interior, image=self._imagen_robot).pack(
            pady=theme.PADDING_CHICO
        )

        BotonPrimario(
            interior,
            text=textos.t("boton_comenzar"),
            width=240,
            command=lambda: self.app.ir_a("juego"),
        ).pack(pady=(theme.PADDING, theme.PADDING_CHICO))

        BotonSecundario(
            interior,
            text=textos.t("boton_salir"),
            width=240,
            command=self.app.cerrar,
        ).pack(pady=theme.PADDING_CHICO)

    def al_mostrar(self) -> None:
        """No hay nada que refrescar en la portada."""
        return None
