"""Pantalla de resumen con el reporte y el acceso a la animación."""

from __future__ import annotations

import customtkinter as ctk

from ui import animator, report_panel, theme, textos
from ui.componentes import (
    BotonPrimario,
    Contenedor,
    BotonSecundario,
    Etiqueta,
    EtiquetaPequena,
    FilaClaveValor,
    Separador,
    Tarjeta,
    Titulo,
)


class ResumenScreen(ctk.CTkFrame):
    """Muestra las métricas de la búsqueda y permite ver la animación."""

    def __init__(self, master: object, app: object) -> None:
        super().__init__(master, fg_color=theme.COLOR_FONDO)
        self.app = app
        self._animado: object | None = None
        self._construir()

    @property
    def sesion(self) -> object:
        return self.app.sesion

    def _construir(self) -> None:
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        tarjeta = Tarjeta(self)
        tarjeta.grid(row=0, column=0, padx=theme.PADDING * 2, pady=theme.PADDING * 2)
        interior = Contenedor(tarjeta)
        interior.pack(
            padx=theme.PADDING * 2,
            pady=theme.PADDING * 2,
        )

        Titulo(interior, text=textos.t("resumen_titulo")).pack(anchor="w")
        self.lbl_estado = Etiqueta(interior, text="")
        self.lbl_estado.pack(anchor="w", pady=(theme.PADDING_CHICO, 0))
        self.lbl_detalle = EtiquetaPequena(
            interior, text="", wraplength=620, anchor="w", justify="left"
        )
        self.lbl_detalle.pack(anchor="w", pady=(2, theme.PADDING_CHICO))

        Separador(interior).pack(fill="x", pady=theme.PADDING_CHICO)

        self._frame_filas = Contenedor(interior)
        self._frame_filas.pack(fill="x")

        Separador(interior).pack(fill="x", pady=theme.PADDING)

        acciones = Contenedor(interior)
        acciones.pack(fill="x")
        acciones.grid_columnconfigure(0, weight=1)
        acciones.grid_columnconfigure(1, weight=1)
        acciones.grid_columnconfigure(2, weight=1)

        self.boton_animacion = BotonPrimario(
            acciones,
            text=textos.t("boton_animacion"),
            command=self._lanzar_animacion,
        )
        self.boton_animacion.grid(row=0, column=0, padx=4, sticky="ew")

        BotonSecundario(
            acciones,
            text=textos.t("boton_otro_algoritmo"),
            command=lambda: self.app.ir_a("juego"),
        ).grid(row=0, column=1, padx=4, sticky="ew")

        BotonSecundario(
            acciones,
            text=textos.t("boton_inicio"),
            command=lambda: self.app.ir_a("inicio"),
        ).grid(row=0, column=2, padx=4, sticky="ew")

    def _limpiar_filas(self) -> None:
        for widget in self._frame_filas.winfo_children():
            widget.destroy()

    def _actualizar(self) -> None:
        self._limpiar_filas()
        resultado = self.sesion.resultado

        if resultado is None:
            self.lbl_estado.configure(text=textos.t("resumen_sin_resultado"))
            self.lbl_detalle.configure(text="")
            self.boton_animacion.grid_remove()
            return

        for clave, valor in report_panel.construir_reporte_completo(
            resultado, self.sesion.algoritmo, self.sesion.ruta_mundo
        ):
            FilaClaveValor(self._frame_filas, clave, valor).pack(fill="x", pady=2)

        if resultado.exito:
            self.lbl_estado.configure(text=textos.t("resumen_exito"))
            self.lbl_detalle.configure(text="")
            self.boton_animacion.grid()
        elif resultado.limite_alcanzado:
            self.lbl_estado.configure(text=textos.t("resumen_limite"))
            self.lbl_detalle.configure(text=textos.t("resumen_limite_detalle"))
            self.boton_animacion.grid_remove()
        else:
            self.lbl_estado.configure(text=textos.t("resumen_sin_solucion"))
            self.lbl_detalle.configure(
                text=textos.t("resumen_sin_solucion_detalle")
            )
            self.boton_animacion.grid_remove()

    def _lanzar_animacion(self) -> None:
        resultado = self.sesion.resultado
        if (
            resultado is None
            or not resultado.exito
            or self.sesion.ruta_mundo is None
        ):
            return
        titulo = textos.t(
            "anim_titulo",
            algoritmo=report_panel.nombre_algoritmo(self.sesion.algoritmo),
        )
        resumen = report_panel.construir_reporte_completo(
            resultado, self.sesion.algoritmo, self.sesion.ruta_mundo
        )
        animator.lanzar_animacion(
            self.sesion.ruta_mundo, resultado.estados, titulo, resumen
        )
        self.boton_animacion.configure(
            text=textos.t("boton_repetir_animacion")
        )

    def al_mostrar(self) -> None:
        """Refresca el reporte y lanza la animación una vez si hubo solución."""
        self._actualizar()
        resultado = self.sesion.resultado
        if (
            resultado is not None
            and resultado.exito
            and resultado is not self._animado
        ):
            self._animado = resultado
            self._lanzar_animacion()
