"""Pantalla principal: cabecera de inicio, tablero y panel de control."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from core.world import World
from ui import assets_loader, animator, report_panel, runner, theme, textos
from ui.board_view import TableroCanvas
from ui.componentes import (
    BotonPeligro,
    BotonPrimario,
    BotonSecundario,
    CampoTexto,
    Contenedor,
    Etiqueta,
    EtiquetaPequena,
    Imagen,
    Opcion,
    SelectorSegmentado,
    Separador,
    Tarjeta,
    Titulo,
)

ALGORITMOS_NO_INFORMADA: list[tuple[str, str]] = [
    ("amplitud", "alg_amplitud"),
    ("costo_uniforme", "alg_costo_uniforme"),
    ("profundidad", "alg_profundidad"),
]

ALGORITMOS_INFORMADA: list[tuple[str, str]] = [
    ("avara", "alg_avara"),
    ("astar", "alg_astar"),
]


class JuegoScreen(ctk.CTkFrame):
    """Pantalla principal: portada, tablero y panel de control."""

    def __init__(self, master: object, app: object) -> None:
        super().__init__(master, fg_color=theme.COLOR_FONDO)
        self.app = app
        self._poll_id: str | None = None
        self._poll_animacion_id: str | None = None
        self._var_algoritmo = tk.StringVar(value="")
        self._var_limite = tk.StringVar(value=str(theme.LIMITE_NODOS_DEFECTO))
        self._radios: list[Opcion] = []
        self._construir()

    @property
    def sesion(self) -> object:
        return self.app.sesion

    def _construir(self) -> None:
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        cabecera = Tarjeta(self)
        cabecera.grid(
            row=0, column=0, columnspan=2, sticky="ew",
            padx=theme.PADDING,
            pady=(theme.PADDING, theme.PADDING_CHICO),
        )
        interior_cabecera = Contenedor(cabecera)
        interior_cabecera.pack(
            fill="x", padx=theme.PADDING, pady=theme.PADDING_CHICO
        )
        imagen = assets_loader.cargar_robot(theme.TAM_ROBOT_JUEGO)
        self._imagen_robot = ctk.CTkImage(
            light_image=imagen,
            size=(theme.TAM_ROBOT_JUEGO, theme.TAM_ROBOT_JUEGO),
        )
        Imagen(interior_cabecera, image=self._imagen_robot).pack(
            side="left", padx=(0, theme.PADDING)
        )
        textos_cabecera = Contenedor(interior_cabecera)
        textos_cabecera.pack(side="left", fill="x", expand=True)
        Titulo(
            textos_cabecera, text=textos.t("inicio_titulo")
        ).pack(anchor="w")
        EtiquetaPequena(
            textos_cabecera,
            text=textos.t("inicio_subtitulo"),
            wraplength=700,
            anchor="w",
            justify="left",
        ).pack(anchor="w")

        tarjeta_tablero = Tarjeta(self)
        tarjeta_tablero.grid(
            row=1, column=0, sticky="nsew",
            padx=(theme.PADDING, theme.PADDING_CHICO),
            pady=(theme.PADDING_CHICO, theme.PADDING),
        )
        tarjeta_tablero.grid_rowconfigure(0, weight=1)
        tarjeta_tablero.grid_columnconfigure(0, weight=1)
        self.tablero = TableroCanvas(tarjeta_tablero)
        self.tablero.grid(
            row=0, column=0, sticky="nsew",
            padx=theme.PADDING_CHICO, pady=theme.PADDING_CHICO,
        )

        panel = Tarjeta(self, width=theme.ANCHO_PANEL_JUEGO)
        panel.grid(
            row=1, column=1, sticky="ns",
            padx=(theme.PADDING_CHICO, theme.PADDING),
            pady=(theme.PADDING_CHICO, theme.PADDING),
        )
        panel.pack_propagate(False)

        interior = Contenedor(panel)
        interior.pack(
            fill="both", expand=True,
            padx=theme.PADDING, pady=theme.PADDING,
        )

        Titulo(interior, text=textos.t("juego_titulo")).pack(anchor="w")

        self.boton_cargar = BotonSecundario(
            interior,
            text=textos.t("boton_cargar_mundo"),
            command=self._cargar_mundo,
        )
        self.boton_cargar.pack(fill="x", pady=(theme.PADDING, theme.PADDING_CHICO))

        self.lbl_archivo = EtiquetaPequena(
            interior,
            text=textos.t("archivo_sin_cargar"),
            wraplength=theme.ANCHO_PANEL_JUEGO - 3 * theme.PADDING,
            anchor="w",
            justify="left",
        )
        self.lbl_archivo.pack(fill="x")

        Separador(interior).pack(fill="x", pady=theme.PADDING_CHICO)

        Etiqueta(interior, text=textos.t("tipo_busqueda")).pack(anchor="w")
        self.selector_tipo = SelectorSegmentado(
            interior,
            values=[
                textos.t("tipo_no_informada"),
                textos.t("tipo_informada"),
            ],
            command=self._al_cambiar_tipo,
        )
        self.selector_tipo.set(textos.t("tipo_no_informada"))
        self.selector_tipo.pack(fill="x", pady=(2, theme.PADDING_CHICO))

        Etiqueta(interior, text=textos.t("algoritmo")).pack(anchor="w")
        self._frame_algoritmos = Contenedor(interior)
        self._frame_algoritmos.pack(fill="x", pady=(2, theme.PADDING_CHICO))

        Etiqueta(interior, text=textos.t("limite_nodos")).pack(anchor="w")
        self.entry_limite = CampoTexto(
            interior, textvariable=self._var_limite, justify="center"
        )
        self.entry_limite.pack(fill="x", pady=(2, 2))
        EtiquetaPequena(
            interior,
            text=textos.t("limite_ayuda"),
            wraplength=theme.ANCHO_PANEL_JUEGO - 3 * theme.PADDING,
            anchor="w",
            justify="left",
        ).pack(fill="x")

        self.lbl_estado = Etiqueta(
            interior,
            text=textos.t("estado_inactivo"),
            wraplength=theme.ANCHO_PANEL_JUEGO - 3 * theme.PADDING,
            anchor="w",
            justify="left",
        )
        self.lbl_estado.pack(fill="x", pady=theme.PADDING)

        self._frame_acciones = Contenedor(interior)
        self._frame_acciones.pack(fill="x")
        self.boton_ejecutar = BotonPrimario(
            self._frame_acciones,
            text=textos.t("boton_ejecutar"),
            command=self._ejecutar,
        )
        self.boton_ejecutar.pack(side="left", fill="x", expand=True)
        self.boton_cancelar = BotonPeligro(
            self._frame_acciones,
            text=textos.t("boton_cancelar"),
            command=self._cancelar,
        )

        self.boton_resultados = BotonPrimario(
            interior,
            text=textos.t("boton_resultados"),
            command=self._ver_resultados,
        )

        self.boton_volver = BotonSecundario(
            interior,
            text=textos.t("boton_salir"),
            command=self.app.cerrar,
        )
        self.boton_volver.pack(fill="x", pady=(theme.PADDING_CHICO, 0))

        self._reconstruir_algoritmos()

    # --- Utilidades ---------------------------------------------------------

    def _poner_estado(self, texto: str) -> None:
        self.lbl_estado.configure(text=texto)

    def _actualizar_ejecutar(self) -> None:
        valido = (
            self.sesion.world is not None
            and self.sesion.algoritmo in runner.ALGORITMOS
            and self.sesion.estado_busqueda != "buscando"
            and not animator.en_ejecucion()
        )
        self.boton_ejecutar.configure(state="normal" if valido else "disabled")

    def _reconstruir_algoritmos(self) -> None:
        for widget in self._frame_algoritmos.winfo_children():
            widget.destroy()
        self._radios = []
        self._var_algoritmo.set("")
        self.sesion.algoritmo = None

        lista = (
            ALGORITMOS_INFORMADA
            if self.sesion.tipo_busqueda == "informada"
            else ALGORITMOS_NO_INFORMADA
        )
        for clave, clave_texto in lista:
            radio = Opcion(
                self._frame_algoritmos,
                text=textos.t(clave_texto),
                variable=self._var_algoritmo,
                value=clave,
                command=self._al_elegir_algoritmo,
            )
            radio.pack(anchor="w", pady=2)
            self._radios.append(radio)

        self._actualizar_ejecutar()

    def _al_elegir_algoritmo(self) -> None:
        self.sesion.algoritmo = self._var_algoritmo.get() or None
        self._actualizar_ejecutar()

    def _al_cambiar_tipo(self, valor: str) -> None:
        informada = valor == textos.t("tipo_informada")
        self.sesion.tipo_busqueda = "informada" if informada else "no_informada"
        self._reconstruir_algoritmos()
        self._poner_estado(textos.t("estado_inactivo"))

    # --- Acciones -----------------------------------------------------------

    def _cargar_mundo(self) -> None:
        ruta = filedialog.askopenfilename(
            title=textos.t("boton_cargar_mundo"),
            initialdir=str(theme.RUTA_MUNDOS),
            filetypes=[
                (textos.t("filtro_mundos"), "*.txt"),
                (textos.t("filtro_todos"), "*.*"),
            ],
        )
        if not ruta:
            return
        try:
            world = World.desde_archivo(ruta)
        except (ValueError, FileNotFoundError) as exc:
            self._poner_estado(textos.t("estado_error", mensaje=str(exc)))
            return

        self.sesion.ruta_mundo = ruta
        self.sesion.world = world
        self.sesion.reiniciar_busqueda()
        self.tablero.mostrar_mundo(world)
        self.lbl_archivo.configure(
            text=textos.t("archivo_cargado", nombre=Path(ruta).name)
        )
        self._poner_estado(textos.t("estado_mundo_cargado"))
        self._actualizar_ejecutar()

    def _ejecutar(self) -> None:
        if self.sesion.world is None or self.sesion.ruta_mundo is None:
            self._poner_estado(textos.t("error_sin_mundo"))
            return
        if self.sesion.algoritmo not in runner.ALGORITMOS:
            self._poner_estado(textos.t("error_sin_algoritmo"))
            return
        try:
            limite = int(self._var_limite.get().strip())
            if limite <= 0:
                raise ValueError
        except ValueError:
            self._poner_estado(textos.t("error_limite"))
            return

        self.sesion.limite_nodos = limite
        self.sesion.resultado = None
        self.sesion.error = None
        self.sesion.estado_busqueda = "buscando"
        self._ocultar_resultados()
        runner.iniciar(
            self.sesion.ruta_mundo, self.sesion.algoritmo, limite
        )
        self._poner_estado(textos.t("estado_buscando"))
        self._modo_buscando(True)
        self._programar_consulta()

    def _cancelar(self) -> None:
        runner.cancelar()
        self.sesion.estado_busqueda = "cancelado"
        self._modo_buscando(False)
        self._poner_estado(textos.t("estado_cancelado"))

    def _programar_consulta(self) -> None:
        self._poll_id = self.after(
            theme.INTERVALO_CONSULTA_MS, self._consultar
        )

    def _consultar(self) -> None:
        self._poll_id = None
        if self.sesion.estado_busqueda != "buscando":
            return

        resultado = runner.consultar()
        if resultado is not None:
            self.sesion.resultado = resultado
            self.sesion.estado_busqueda = "listo"
            self._modo_buscando(False)
            if resultado.exito:
                self._lanzar_animacion()
            else:
                self._mostrar_resultados()
                self._poner_estado(textos.t("estado_sin_animacion"))
            return

        if not runner.en_ejecucion():
            mensaje = runner.ultimo_error() or textos.t("error_busqueda")
            self.sesion.estado_busqueda = "error"
            self.sesion.error = mensaje
            self._modo_buscando(False)
            self._poner_estado(textos.t("estado_error", mensaje=mensaje))
            return

        self._programar_consulta()

    def _lanzar_animacion(self) -> None:
        """Lanza la animación sin abrir todavía el reporte."""
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
        self._poner_estado(textos.t("estado_animando"))
        self._programar_consulta_animacion()
        self._actualizar_ejecutar()

    def _programar_consulta_animacion(self) -> None:
        self._poll_animacion_id = self.after(
            theme.INTERVALO_CONSULTA_MS, self._consultar_animacion
        )

    def _consultar_animacion(self) -> None:
        self._poll_animacion_id = None
        if animator.solicita_resultados():
            animator.detener_animacion()
            self._ver_resultados()
            return
        if not animator.en_ejecucion():
            self._mostrar_resultados()
            self._poner_estado(textos.t("estado_animacion_cerrada"))
            self._actualizar_ejecutar()
            return
        self._programar_consulta_animacion()

    def _mostrar_resultados(self) -> None:
        self.boton_resultados.pack(
            fill="x",
            pady=(theme.PADDING, 0),
            before=self.boton_volver,
        )

    def _ocultar_resultados(self) -> None:
        self.boton_resultados.pack_forget()

    def _ver_resultados(self) -> None:
        self._ocultar_resultados()
        if self._poll_animacion_id is not None:
            self.after_cancel(self._poll_animacion_id)
            self._poll_animacion_id = None
        self.app.ir_a("resumen")

    def _modo_buscando(self, activo: bool) -> None:
        self.boton_ejecutar.pack_forget()
        self.boton_cancelar.pack_forget()
        if activo:
            self.boton_cancelar.pack(side="left", fill="x", expand=True)
        else:
            self.boton_ejecutar.pack(side="left", fill="x", expand=True)

        estado = "disabled" if activo else "normal"
        self.boton_cargar.configure(state=estado)
        self.entry_limite.configure(state=estado)
        self.boton_volver.configure(state=estado)
        try:
            self.selector_tipo.configure(state=estado)
        except ValueError:
            pass
        for radio in self._radios:
            habilitado = not activo
            radio.configure(state="normal" if habilitado else "disabled")

        self._actualizar_ejecutar()

    # --- Ciclo de vida ------------------------------------------------------

    def al_mostrar(self) -> None:
        """Sincroniza la pantalla con el estado compartido."""
        if self.sesion.world is not None:
            self.tablero.mostrar_mundo(self.sesion.world)
        if self.sesion.ruta_mundo:
            self.lbl_archivo.configure(
                text=textos.t(
                    "archivo_cargado",
                    nombre=Path(self.sesion.ruta_mundo).name,
                )
            )

        informada = self.sesion.tipo_busqueda == "informada"
        self.selector_tipo.set(
            textos.t("tipo_informada" if informada else "tipo_no_informada")
        )
        self._reconstruir_algoritmos()
        if self.sesion.estado_busqueda != "buscando":
            self._actualizar_ejecutar()
