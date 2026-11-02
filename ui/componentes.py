"""Widgets reutilizables con el estilo del tema.

Las pantallas deben componer la interfaz solo con estos widgets y nunca
usar colores o fuentes directas. Así, cambiar el tema no obliga a tocar
las pantallas.
"""

from __future__ import annotations

import customtkinter as ctk

from ui import theme


def _fuente(tam: int, negrita: bool = False) -> ctk.CTkFont:
    return ctk.CTkFont(
        family=theme.FAMILIA_FUENTE,
        size=tam,
        weight="bold" if negrita else "normal",
    )


class BotonPrimario(ctk.CTkButton):
    """Acción principal (verde hoja)."""

    def __init__(self, master: object, **kwargs: object) -> None:
        opciones = {
            "fg_color": theme.COLOR_ACCION,
            "hover_color": theme.COLOR_ACCION_HOVER,
            "text_color": theme.COLOR_TEXTO,
            "border_color": theme.COLOR_BORDE,
            "border_width": theme.GROSOR_BORDE_FINO,
            "corner_radius": theme.RADIO_ESQUINA,
            "font": _fuente(theme.TAM_FUENTE_TEXTO, True),
            "height": 42,
            "text": "",
        }
        opciones.update(kwargs)
        super().__init__(master, **opciones)


class BotonSecundario(ctk.CTkButton):
    """Acción secundaria (crema con borde)."""

    def __init__(self, master: object, **kwargs: object) -> None:
        opciones = {
            "fg_color": theme.COLOR_PANEL,
            "hover_color": theme.COLOR_ACENTO,
            "text_color": theme.COLOR_TEXTO,
            "border_color": theme.COLOR_BORDE,
            "border_width": theme.GROSOR_BORDE_FINO,
            "corner_radius": theme.RADIO_ESQUINA,
            "font": _fuente(theme.TAM_FUENTE_TEXTO, True),
            "height": 42,
            "text": "",
        }
        opciones.update(kwargs)
        super().__init__(master, **opciones)


class BotonPeligro(ctk.CTkButton):
    """Acción de peligro o cancelación (terracota)."""

    def __init__(self, master: object, **kwargs: object) -> None:
        opciones = {
            "fg_color": theme.COLOR_PELIGRO,
            "hover_color": theme.COLOR_PELIGRO_HOVER,
            "text_color": theme.COLOR_PANEL,
            "border_color": theme.COLOR_BORDE,
            "border_width": theme.GROSOR_BORDE_FINO,
            "corner_radius": theme.RADIO_ESQUINA,
            "font": _fuente(theme.TAM_FUENTE_TEXTO, True),
            "height": 42,
            "text": "",
        }
        opciones.update(kwargs)
        super().__init__(master, **opciones)


class Tarjeta(ctk.CTkFrame):
    """Panel crema con borde marrón, estilo retro."""

    def __init__(self, master: object, **kwargs: object) -> None:
        opciones = {
            "fg_color": theme.COLOR_PANEL,
            "border_color": theme.COLOR_BORDE,
            "border_width": theme.GROSOR_BORDE,
            "corner_radius": theme.RADIO_ESQUINA,
        }
        opciones.update(kwargs)
        super().__init__(master, **opciones)


class Titulo(ctk.CTkLabel):
    """Título grande de pantalla."""

    def __init__(self, master: object, **kwargs: object) -> None:
        opciones = {
            "text_color": theme.COLOR_TEXTO,
            "font": _fuente(theme.TAM_FUENTE_TITULO, True),
            "text": "",
        }
        opciones.update(kwargs)
        super().__init__(master, **opciones)


class TituloGrande(ctk.CTkLabel):
    """Título de portada."""

    def __init__(self, master: object, **kwargs: object) -> None:
        opciones = {
            "text_color": theme.COLOR_TEXTO,
            "font": _fuente(theme.TAM_FUENTE_TITULO_GRANDE, True),
            "text": "",
        }
        opciones.update(kwargs)
        super().__init__(master, **opciones)


class Subtitulo(ctk.CTkLabel):
    """Texto de apoyo bajo un título."""

    def __init__(self, master: object, **kwargs: object) -> None:
        opciones = {
            "text_color": theme.COLOR_TEXTO_SUAVE,
            "font": _fuente(theme.TAM_FUENTE_SUBTITULO),
            "text": "",
            "wraplength": 460,
            "justify": "center",
        }
        opciones.update(kwargs)
        super().__init__(master, **opciones)


class Etiqueta(ctk.CTkLabel):
    """Texto normal."""

    def __init__(self, master: object, **kwargs: object) -> None:
        opciones = {
            "text_color": theme.COLOR_TEXTO,
            "font": _fuente(theme.TAM_FUENTE_TEXTO),
            "text": "",
        }
        opciones.update(kwargs)
        super().__init__(master, **opciones)


class EtiquetaPequena(ctk.CTkLabel):
    """Texto auxiliar pequeño."""

    def __init__(self, master: object, **kwargs: object) -> None:
        opciones = {
            "text_color": theme.COLOR_TEXTO_SUAVE,
            "font": _fuente(theme.TAM_FUENTE_PEQUENA),
            "text": "",
        }
        opciones.update(kwargs)
        super().__init__(master, **opciones)


class CampoTexto(ctk.CTkEntry):
    """Campo de texto con el estilo del tema."""

    def __init__(self, master: object, **kwargs: object) -> None:
        opciones = {
            "fg_color": theme.COLOR_FONDO,
            "text_color": theme.COLOR_TEXTO,
            "border_color": theme.COLOR_BORDE,
            "border_width": theme.GROSOR_BORDE_FINO,
            "corner_radius": theme.RADIO_ESQUINA,
            "font": _fuente(theme.TAM_FUENTE_TEXTO),
            "height": 36,
        }
        opciones.update(kwargs)
        super().__init__(master, **opciones)


class SelectorSegmentado(ctk.CTkSegmentedButton):
    """Selector de pocas opciones con el estilo del tema."""

    def __init__(self, master: object, **kwargs: object) -> None:
        opciones = {
            "selected_color": theme.COLOR_ACCION,
            "selected_hover_color": theme.COLOR_ACCION_HOVER,
            "unselected_color": theme.COLOR_PANEL,
            "unselected_hover_color": theme.COLOR_ACENTO,
            "text_color": theme.COLOR_TEXTO,
            "font": _fuente(theme.TAM_FUENTE_TEXTO, True),
            "corner_radius": theme.RADIO_ESQUINA,
        }
        opciones.update(kwargs)
        super().__init__(master, **opciones)


class Opcion(ctk.CTkRadioButton):
    """Opción de algoritmo (radio) con el estilo del tema."""

    def __init__(self, master: object, **kwargs: object) -> None:
        opciones = {
            "fg_color": theme.COLOR_ACCION,
            "hover_color": theme.COLOR_ACCION_HOVER,
            "text_color": theme.COLOR_TEXTO,
            "border_color": theme.COLOR_BORDE,
            "font": _fuente(theme.TAM_FUENTE_TEXTO),
        }
        opciones.update(kwargs)
        super().__init__(master, **opciones)


class Separador(ctk.CTkFrame):
    """Línea horizontal fina con el color del borde."""

    def __init__(self, master: object, **kwargs: object) -> None:
        opciones = {"fg_color": theme.COLOR_BORDE, "height": 2}
        opciones.update(kwargs)
        super().__init__(master, **opciones)


class Contenedor(ctk.CTkFrame):
    """Frame transparente para agrupar widgets."""

    def __init__(self, master: object, **kwargs: object) -> None:
        opciones = {"fg_color": "transparent"}
        opciones.update(kwargs)
        super().__init__(master, **opciones)


class Imagen(ctk.CTkLabel):
    """Etiqueta que solo muestra una imagen."""

    def __init__(self, master: object, **kwargs: object) -> None:
        opciones = {
            "text": "",
            "fg_color": "transparent",
        }
        opciones.update(kwargs)
        super().__init__(master, **opciones)


class FilaClaveValor(ctk.CTkFrame):
    """Fila de reporte: etiqueta a la izquierda y valor a la derecha."""

    def __init__(self, master: object, clave: str, valor: str = "", **kwargs: object) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_columnconfigure(1, weight=1)
        self._clave = Etiqueta(self, text=clave)
        self._clave.grid(row=0, column=0, sticky="w", padx=(0, theme.PADDING_CHICO))
        self._valor = Etiqueta(self, text=valor, anchor="e")
        self._valor.grid(row=0, column=1, sticky="e")

    def establecer_valor(self, valor: str) -> None:
        """Actualiza el valor mostrado."""
        self._valor.configure(text=valor)
