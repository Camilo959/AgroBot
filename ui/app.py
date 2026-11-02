"""Ventana principal y gestor de pantallas del AgroBot."""

from __future__ import annotations

import customtkinter as ctk

from ui import animator, runner, theme, textos
from ui.screens import PANTALLAS
from ui.sesion import SesionJuego

TAMANOS: dict[str, tuple[int, int]] = {
    "inicio": theme.TAM_VENTANA_INICIO,
    "juego": theme.TAM_VENTANA_JUEGO,
    "resumen": theme.TAM_VENTANA_RESUMEN,
}


class AgroBotApp(ctk.CTk):
    """Ventana principal que apila las pantallas y navega entre ellas."""

    def __init__(self) -> None:
        ctk.set_appearance_mode("light")
        super().__init__()
        self.title(textos.t("app_titulo"))
        self.configure(fg_color=theme.COLOR_FONDO)
        self.minsize(820, 600)

        self.sesion = SesionJuego()
        self._pantalla_actual: ctk.CTkFrame | None = None

        self.contenedor = ctk.CTkFrame(self, fg_color=theme.COLOR_FONDO)
        self.contenedor.pack(fill="both", expand=True)
        self.contenedor.grid_rowconfigure(0, weight=1)
        self.contenedor.grid_columnconfigure(0, weight=1)

        self.pantallas: dict[str, ctk.CTkFrame] = {}
        for nombre, clase in PANTALLAS.items():
            pantalla = clase(self.contenedor, self)
            pantalla.grid(row=0, column=0, sticky="nsew")
            pantalla.grid_remove()
            self.pantallas[nombre] = pantalla

        self.protocol("WM_DELETE_WINDOW", self.cerrar)
        self.ir_a("inicio")

    def ir_a(self, nombre: str) -> None:
        """Muestra la pantalla indicada y llama a su `al_mostrar`."""
        pantalla = self.pantallas[nombre]
        if self._pantalla_actual is not None:
            self._pantalla_actual.grid_remove()
        self._pantalla_actual = pantalla
        pantalla.grid()
        pantalla.tkraise()
        tamano = TAMANOS.get(nombre)
        if tamano is not None:
            self.geometry(f"{tamano[0]}x{tamano[1]}")
        pantalla.al_mostrar()

    def cerrar(self) -> None:
        """Termina procesos hijos vivos y cierra la ventana."""
        runner.cancelar()
        animator.detener_animacion()
        self.destroy()
