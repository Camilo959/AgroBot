"""Carga y preprocesado de sprites del AgroBot.

Reglas:
    - Los sprites de 16 px y 32 px se escalan siempre con `Image.NEAREST`.
    - El robot se preprocesa una vez (fondo -> transparente) y se cachea en
      `ui/assets/generados/agrobot_128.png`; luego se escala con LANCZOS.
    - Si falta un asset se devuelve una imagen de reemplazo del color del
      tema, sin romper la aplicación.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from ui import theme

#: Resolución del sprite de robot cacheado (cuadrado).
TAM_ROBOT_CACHE: int = 128
#: Color mágico para el relleno por inundación del fondo del robot.
COLOR_MAGICO: tuple[int, int, int] = (255, 0, 255)

_cache_sprites: dict[tuple[str, int], Image.Image] = {}


def ruta_cache_robot() -> Path:
    """Ruta del PNG cacheado del robot preprocesado."""
    return theme.RUTA_ASSETS_GENERADOS / f"agrobot_{TAM_ROBOT_CACHE}.png"


def _imagen_reemplazo(nombre: str, tam: int) -> Image.Image:
    """Crea una imagen sólida de reemplazo cuando falta un asset."""
    color = theme.COLORES_REEMPLAZO.get(nombre, (200, 200, 200, 255))
    return Image.new("RGBA", (tam, tam), color)


def cargar_imagen(nombre_logico: str) -> Image.Image:
    """Carga un asset como RGBA; si falta, devuelve un reemplazo sólido."""
    ruta = theme.ruta_asset(nombre_logico)
    try:
        with Image.open(ruta) as imagen:
            return imagen.convert("RGBA")
    except (FileNotFoundError, OSError):
        return _imagen_reemplazo(nombre_logico, theme.TAM_CELDA)


def escalar_nearest(imagen: Image.Image, tam: int) -> Image.Image:
    """Escala un sprite pixel art conservando los píxeles duros (NEAREST)."""
    return imagen.resize((tam, tam), Image.NEAREST)


def preprocesar_robot(
    ruta_origen: Path | None = None,
    ruta_destino: Path | None = None,
) -> Path:
    """Quita el fondo del robot y guarda un PNG RGBA cuadrado de 128×128.

    Pasos:
        1. Abrir en RGB y hacer relleno por inundación con color mágico
           desde 8 puntos del borde (`thresh=38`).
        2. Los píxeles mágicos pasan a alfa 0; el resto a alfa 255.
        3. Recortar al contenido, centrar en un lienzo cuadrado y reducir
           a 128×128 con LANCZOS.
    """
    origen = ruta_origen or theme.ruta_asset("robot")
    destino = ruta_destino or ruta_cache_robot()

    with Image.open(origen) as abierta:
        rgb = abierta.convert("RGB")
    ancho, alto = rgb.size

    puntos = [
        (0, 0),
        (ancho - 1, 0),
        (0, alto - 1),
        (ancho - 1, alto - 1),
        (ancho // 2, 0),
        (ancho // 2, alto - 1),
        (0, alto // 2),
        (ancho - 1, alto // 2),
    ]
    for punto in puntos:
        try:
            ImageDraw.floodfill(rgb, punto, COLOR_MAGICO, thresh=38)
        except ValueError:
            continue

    pixeles = rgb.load()
    alfa = Image.new("L", rgb.size)
    pixeles_alfa = alfa.load()
    for y in range(alto):
        for x in range(ancho):
            pixeles_alfa[x, y] = 0 if pixeles[x, y] == COLOR_MAGICO else 255

    recortado = rgb.convert("RGBA")
    recortado.putalpha(alfa)
    caja = alfa.getbbox()
    if caja is not None:
        recortado = recortado.crop(caja)

    lado = max(recortado.size)
    lienzo = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    desplazamiento = (
        (lado - recortado.width) // 2,
        (lado - recortado.height) // 2,
    )
    lienzo.paste(recortado, desplazamiento, recortado)

    final = lienzo.resize(
        (TAM_ROBOT_CACHE, TAM_ROBOT_CACHE), Image.LANCZOS
    )
    destino.parent.mkdir(parents=True, exist_ok=True)
    final.save(destino, "PNG")
    return destino


def cargar_robot(tam: int = theme.TAM_CELDA) -> Image.Image:
    """Carga el robot preprocesado (generándolo la primera vez) y lo escala."""
    ruta = ruta_cache_robot()
    if not ruta.is_file():
        try:
            preprocesar_robot(ruta_destino=ruta)
        except (FileNotFoundError, OSError):
            return _imagen_reemplazo("robot", tam)
    try:
        with Image.open(ruta) as imagen:
            robot = imagen.convert("RGBA")
    except (FileNotFoundError, OSError):
        return _imagen_reemplazo("robot", tam)
    return robot.resize((tam, tam), Image.LANCZOS)


def obtener_sprite(nombre_logico: str, tam: int = theme.TAM_CELDA) -> Image.Image:
    """Devuelve el sprite escalado y cacheado para el tamaño pedido."""
    clave = (nombre_logico, tam)
    if clave in _cache_sprites:
        return _cache_sprites[clave]

    if nombre_logico == "robot":
        sprite = cargar_robot(tam)
    else:
        sprite = escalar_nearest(cargar_imagen(nombre_logico), tam)

    _cache_sprites[clave] = sprite
    return sprite


def cargar_todos(tam: int = theme.TAM_CELDA) -> dict[str, Image.Image]:
    """Carga todos los sprites lógicos a un tamaño dado."""
    return {nombre: obtener_sprite(nombre, tam) for nombre in theme.ARCHIVOS_ASSETS}


def limpiar_cache() -> None:
    """Vacía la caché en memoria (útil para pruebas)."""
    _cache_sprites.clear()


def sombra_avioneta(tam: int = theme.TAM_CELDA) -> Image.Image:
    """Genera una sombra elíptica semitransparente para la avioneta."""
    imagen = Image.new("RGBA", (tam, tam), (0, 0, 0, 0))
    dibujo = ImageDraw.Draw(imagen)
    dibujo.ellipse(
        [tam * 0.12, tam * 0.62, tam * 0.88, tam * 0.92],
        fill=theme.COLOR_SOMBRA,
    )
    return imagen
