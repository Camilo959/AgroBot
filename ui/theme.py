"""Tema visual centralizado del AgroBot.

Todo lo visual (colores, tamaños, fuentes, bordes, assets y velocidades)
vive aquí. Cambiar el aspecto de la aplicación debe requerir editar solo
este archivo o reemplazar los archivos de `ui/assets/`.
"""

from __future__ import annotations

from pathlib import Path

RUTA_PROYECTO: Path = Path(__file__).resolve().parent.parent
RUTA_UI: Path = RUTA_PROYECTO / "ui"
RUTA_ASSETS: Path = RUTA_UI / "assets"
RUTA_ASSETS_GENERADOS: Path = RUTA_ASSETS / "generados"
RUTA_FUENTES: Path = RUTA_ASSETS / "fuentes"
RUTA_MUNDOS: Path = RUTA_PROYECTO / "worlds"

# --- Paleta -----------------------------------------------------------------
COLOR_FONDO: str = "#f7e9c9"
COLOR_PANEL: str = "#fff6e0"
COLOR_BORDE: str = "#3f2631"
COLOR_TEXTO: str = "#3f2631"
COLOR_TEXTO_SUAVE: str = "#6b5147"
COLOR_ACCION: str = "#84c669"
COLOR_ACCION_HOVER: str = "#6fae55"
COLOR_ACENTO: str = "#eaa56c"
COLOR_ACENTO_HOVER: str = "#d98f55"
COLOR_PELIGRO: str = "#bd6c4a"
COLOR_PELIGRO_HOVER: str = "#a65a3c"
COLOR_VERDE_CLARO: str = "#b6d53c"
COLOR_VERDE_MEDIO: str = "#92b115"
COLOR_VERDE_OSCURO: str = "#345551"
COLOR_TABLERO: str = "#8aa86a"
COLOR_SOMBRA: tuple[int, int, int, int] = (0, 0, 0, 90)

# --- Tipografía -------------------------------------------------------------
FUENTES_SISTEMA: tuple[str, ...] = ("Trebuchet MS", "Verdana", "Segoe UI", "Arial")


def _detectar_familia_fuente() -> str:
    """Usa una .ttf de `ui/assets/fuentes/` si existe; si no, la del sistema."""
    if RUTA_FUENTES.is_dir():
        candidatas = sorted(RUTA_FUENTES.glob("*.ttf"))
        if candidatas:
            return candidatas[0].stem
    return FUENTES_SISTEMA[0]


FAMILIA_FUENTE: str = _detectar_familia_fuente()
TAM_FUENTE_TITULO_GRANDE: int = 46
TAM_FUENTE_TITULO: int = 28
TAM_FUENTE_SUBTITULO: int = 18
TAM_FUENTE_TEXTO: int = 15
TAM_FUENTE_PEQUENA: int = 13
TAM_FUENTE_HUD: int = 16
TAM_FUENTE_HUD_GRANDE: int = 24

# --- Geometría y estilo -----------------------------------------------------
TAM_CELDA: int = 48
MULTIPLO_CELDA: int = 16
GROSOR_BORDE: int = 3
GROSOR_BORDE_FINO: int = 2
RADIO_ESQUINA: int = 8
PADDING: int = 16
PADDING_CHICO: int = 8
ANCHO_PANEL_JUEGO: int = 380
ANCHO_HUD_ANIMACION: int = 420
ALTO_MINIMO_ANIMACION: int = 700
TAM_ROBOT_INICIO: int = 220
TAM_VENTANA_INICIO: tuple[int, int] = (900, 640)
TAM_VENTANA_JUEGO: tuple[int, int] = (1180, 760)
TAM_VENTANA_RESUMEN: tuple[int, int] = (980, 700)

# --- Comportamiento ---------------------------------------------------------
LIMITE_NODOS_DEFECTO: int = 500_000
VELOCIDAD_ANIMACION: float = 4.0  # pasos por segundo
SOMBRA_AVIONETA: bool = True
INTERVALO_CONSULTA_MS: int = 120

# --- Assets -----------------------------------------------------------------
# nombre lógico -> archivo. Cambiar un asset = reemplazar el archivo o esta línea.
ARCHIVOS_ASSETS: dict[str, str] = {
    "casilla": "0_casilla.png",
    "muro": "1_muro.png",
    "robot": "2_agrobot.png",
    "cultivo_seco": "3_cultivoseco.png",
    "cultivo_tratado": "3b_cultivotratado.png",
    "fertilizante": "4_fertilizante.png",
    "avioneta": "5_avioneta.png",
}

# Colores de reemplazo si falta un asset (nunca debe romper la aplicación).
COLORES_REEMPLAZO: dict[str, tuple[int, int, int, int]] = {
    "casilla": (182, 213, 60, 255),
    "muro": (52, 85, 81, 255),
    "robot": (132, 198, 105, 255),
    "cultivo_seco": (234, 165, 108, 255),
    "cultivo_tratado": (146, 177, 21, 255),
    "fertilizante": (189, 108, 74, 255),
    "avioneta": (250, 250, 245, 255),
}


def celda_a_pixeles(fila: int, columna: int, tam_celda: int = TAM_CELDA) -> tuple[int, int]:
    """Convierte (fila, columna) a la posición (x, y) en píxeles."""
    return columna * tam_celda, fila * tam_celda


def ajustar_tam_celda(
    ancho: int,
    alto: int,
    filas: int,
    columnas: int,
    multiplo: int = MULTIPLO_CELDA,
) -> int:
    """Calcula la mayor celda que cabe, redondeada a un múltiplo de `multiplo`."""
    if filas <= 0 or columnas <= 0:
        return multiplo
    candidato = min(ancho // columnas, alto // filas)
    candidato = (candidato // multiplo) * multiplo
    return max(multiplo, candidato)


def ruta_asset(nombre_logico: str) -> Path:
    """Devuelve la ruta del archivo asociado a un nombre lógico."""
    return RUTA_ASSETS / ARCHIVOS_ASSETS[nombre_logico]
