"""Animación del AgroBot en pygame (se ejecuta en un proceso aparte).

La función `ejecutar_animacion` es la función objetivo del proceso hijo;
`lanzar_animacion` la arranca con contexto "spawn" y `detener_animacion`
termina el proceso si sigue vivo.
"""

from __future__ import annotations

import multiprocessing
from multiprocessing.process import BaseProcess

from core.state import Estado
from core.world import World
from ui import assets_loader, report_panel, theme, textos

_proceso: BaseProcess | None = None
_contexto = multiprocessing.get_context("spawn")


def _superficie(pygame: object, imagen: object) -> object:
    """Convierte una imagen PIL RGBA a una superficie de pygame."""
    return pygame.image.fromstring(
        imagen.tobytes(), imagen.size, "RGBA"
    ).convert_alpha()


def _cargar_sprites(pygame: object, tam: int) -> dict[str, object]:
    """Carga todos los sprites (incluida la sombra) como superficies."""
    sprites = {
        nombre: _superficie(pygame, assets_loader.obtener_sprite(nombre, tam))
        for nombre in theme.ARCHIVOS_ASSETS
    }
    sprites["__sombra__"] = _superficie(
        pygame, assets_loader.sombra_avioneta(tam)
    )
    return sprites


def _fuente(pygame: object, tam: int, negrita: bool = False) -> object:
    """Devuelve una fuente de pygame (ttf del proyecto o del sistema)."""
    if theme.RUTA_FUENTES.is_dir():
        candidatas = sorted(theme.RUTA_FUENTES.glob("*.ttf"))
        if candidatas:
            return pygame.font.Font(str(candidatas[0]), tam)
    return pygame.font.SysFont(theme.FAMILIA_FUENTE, tam, bold=negrita)


def _texto(pantalla: object, fuente: object, texto: str, color: tuple[int, int, int],
           pos: tuple[int, int]) -> None:
    """Dibuja un texto en pantalla."""
    superficie = fuente.render(texto, True, color)
    pantalla.blit(superficie, pos)


def _dibujar_tablero(pygame: object, pantalla: object, world: World,
                     estado: Estado, sprites: dict[str, object],
                     tam: int, dx: int, dy: int) -> None:
    """Dibuja el mundo en un estado concreto, respetando las capas."""
    for fila in range(world.filas):
        for columna in range(world.columnas):
            x = dx + columna * tam
            y = dy + fila * tam
            nombre = "muro" if (fila, columna) in world.muros else "casilla"
            pantalla.blit(sprites[nombre], (x, y))

    for fila, columna in world.cultivos:
        nombre = (
            "cultivo_seco"
            if (fila, columna) in estado.cultivos_pendientes
            else "cultivo_tratado"
        )
        pantalla.blit(
            sprites[nombre], (dx + columna * tam, dy + fila * tam)
        )

    fila, columna = world.deposito
    pantalla.blit(
        sprites["fertilizante"], (dx + columna * tam, dy + fila * tam)
    )

    fila, columna = estado.pos
    en_vuelo = estado.combustible > 0
    if estado.combustible == -1:
        fila, columna = world.avioneta
        en_vuelo = False
        mostrar_avioneta = True
    elif en_vuelo:
        mostrar_avioneta = True
    else:
        mostrar_avioneta = False

    if mostrar_avioneta:
        x = dx + columna * tam
        y = dy + fila * tam
        if theme.SOMBRA_AVIONETA:
            pantalla.blit(sprites["__sombra__"], (x, y + int(tam * 0.08)))
        pantalla.blit(sprites["avioneta"], (x, y))
        if en_vuelo:
            pantalla.blit(sprites["robot"], (x, y))

    if not en_vuelo:
        fila, columna = estado.pos
        pantalla.blit(
            sprites["robot"], (dx + columna * tam, dy + fila * tam)
        )


def _dibujar_resumen(pygame: object, pantalla: object,
                     resumen: list[tuple[str, str]], x: int, y: int,
                     ancho: int, fuente_titulo: object,
                     fuente_fila: object) -> int:
    """Dibuja el resumen estático de la búsqueda y devuelve la nueva `y`."""
    _texto(
        pantalla, fuente_titulo, textos.t("anim_resumen"),
        theme.COLOR_TEXTO, (x, y),
    )
    y += theme.TAM_FUENTE_HUD + 4
    for clave, valor in resumen:
        _texto(
            pantalla, fuente_fila, clave, theme.COLOR_TEXTO_SUAVE, (x, y)
        )
        ancho_valor = fuente_fila.size(valor)[0]
        _texto(
            pantalla, fuente_fila, valor, theme.COLOR_TEXTO,
            (x + ancho - ancho_valor, y),
        )
        y += theme.TAM_FUENTE_PEQUENA + 5
    return y


def _dibujar_hud(pygame: object, pantalla: object, alto: int, world: World,
                 estado: Estado, paso: int, total: int, costo: float,
                 velocidad: float, pausado: bool, sprites: dict[str, object],
                 tam: int,
                 resumen: list[tuple[str, str]] | None = None) -> None:
    """Dibuja el panel lateral: resumen arriba y estado en vivo abajo."""
    x0 = world.columnas * tam
    ancho = theme.ANCHO_HUD_ANIMACION
    alto_hud = alto
    pygame.draw.rect(
        pantalla, theme.COLOR_PANEL,
        (x0, 0, ancho, alto_hud),
    )
    pygame.draw.rect(
        pantalla, theme.COLOR_BORDE,
        (x0, 0, ancho - 1, alto_hud - 1), theme.GROSOR_BORDE,
    )

    titulo = _fuente(pygame, theme.TAM_FUENTE_HUD_GRANDE, True)
    negrita = _fuente(pygame, theme.TAM_FUENTE_HUD, True)
    normal = _fuente(pygame, theme.TAM_FUENTE_HUD)
    pequena = _fuente(pygame, theme.TAM_FUENTE_PEQUENA)

    px = x0 + theme.PADDING
    ancho_util = ancho - 2 * theme.PADDING
    py = theme.PADDING
    _texto(pantalla, titulo, textos.t("app_titulo"), theme.COLOR_TEXTO, (px, py))
    py += theme.TAM_FUENTE_HUD_GRANDE + theme.PADDING_CHICO

    if resumen:
        py = _dibujar_resumen(
            pygame, pantalla, resumen, px, py, ancho_util, negrita, pequena
        )
        pygame.draw.line(
            pantalla, theme.COLOR_BORDE,
            (px, py), (x0 + ancho - theme.PADDING, py), 2,
        )
        py += theme.PADDING_CHICO

    _texto(
        pantalla, negrita, textos.t("anim_en_vivo"),
        theme.COLOR_TEXTO, (px, py),
    )
    py += theme.TAM_FUENTE_HUD + 2
    _texto(
        pantalla, normal,
        textos.t("anim_paso", actual=paso + 1, total=total),
        theme.COLOR_TEXTO_SUAVE, (px, py),
    )

    py += theme.TAM_FUENTE_HUD + theme.PADDING
    _texto(
        pantalla, normal, textos.t("anim_fertilizante"),
        theme.COLOR_TEXTO, (px, py),
    )
    py += theme.TAM_FUENTE_HUD + 2
    icono = _superficie(
        pygame, assets_loader.obtener_sprite("fertilizante", 24)
    )
    for i in range(estado.fertilizante):
        pantalla.blit(icono, (px + i * 28, py))
    _texto(
        pantalla, pequena, f"{estado.fertilizante} / 2",
        theme.COLOR_TEXTO_SUAVE, (px + 60, py + 2),
    )

    py += 34 + theme.PADDING_CHICO
    _texto(
        pantalla, normal, textos.t("anim_combustible"),
        theme.COLOR_TEXTO, (px, py),
    )
    py += theme.TAM_FUENTE_HUD + 2
    if estado.combustible == -1:
        _texto(
            pantalla, pequena, textos.t("anim_sin_abordar"),
            theme.COLOR_TEXTO_SUAVE, (px, py),
        )
    elif estado.combustible == 0:
        _texto(
            pantalla, pequena, textos.t("anim_agotada"),
            theme.COLOR_TEXTO_SUAVE, (px, py),
        )
    else:
        ancho_barra = 180
        alto_barra = 14
        proporcion = estado.combustible / 30
        pygame.draw.rect(
            pantalla, theme.COLOR_FONDO,
            (px, py, ancho_barra, alto_barra),
        )
        pygame.draw.rect(
            pantalla, theme.COLOR_BORDE,
            (px, py, ancho_barra, alto_barra), 2,
        )
        pygame.draw.rect(
            pantalla, theme.COLOR_ACCION,
            (px + 2, py + 2, int((ancho_barra - 4) * proporcion), alto_barra - 4),
        )
        _texto(
            pantalla, pequena, str(estado.combustible),
            theme.COLOR_TEXTO, (px + ancho_barra + theme.PADDING_CHICO, py - 3),
        )

    py += 34 + theme.PADDING
    _texto(
        pantalla, normal, textos.t("anim_costo"),
        theme.COLOR_TEXTO, (px, py),
    )
    py += theme.TAM_FUENTE_HUD + 2
    _texto(
        pantalla, titulo, f"{costo:.1f}", theme.COLOR_TEXTO, (px, py),
    )

    py += theme.TAM_FUENTE_HUD_GRANDE + theme.PADDING
    _texto(
        pantalla, pequena,
        textos.t("anim_velocidad", valor=f"{velocidad:.1f}"),
        theme.COLOR_TEXTO_SUAVE, (px, py),
    )
    if pausado:
        py += theme.TAM_FUENTE_PEQUENA + 2
        _texto(
            pantalla, normal, textos.t("anim_pausa"),
            theme.COLOR_PELIGRO, (px, py),
        )

    py = alto_hud - 150
    pygame.draw.line(
        pantalla, theme.COLOR_BORDE, (px, py), (x0 + ancho - theme.PADDING, py), 2
    )
    py += theme.PADDING_CHICO
    if total > 0 and paso >= total - 1:
        _texto(
            pantalla, normal, textos.t("anim_meta"),
            theme.COLOR_VERDE_OSCURO, (px, py),
        )
        py += theme.TAM_FUENTE_HUD + 2
        _texto(
            pantalla, pequena,
            textos.t("anim_costo_total", costo=f"{costo:.1f}"),
            theme.COLOR_TEXTO_SUAVE, (px, py),
        )
        py += theme.TAM_FUENTE_PEQUENA + theme.PADDING_CHICO

    controles = textos.t("anim_controles").split("   ")
    for linea in controles:
        _texto(pantalla, pequena, linea, theme.COLOR_TEXTO_SUAVE, (px, py))
        py += theme.TAM_FUENTE_PEQUENA + 2


def ejecutar_animacion(
    ruta_mundo: str,
    estados: list[Estado],
    titulo: str,
    resumen: list[tuple[str, str]] | None = None,
) -> None:
    """Abre la ventana de pygame y reproduce la lista de estados.

    `resumen` contiene las filas (etiqueta, valor) del reporte de la
    búsqueda; se dibujan en la parte superior del panel lateral.

    Función objetivo del proceso hijo: debe ejecutarse con "spawn".
    """
    import pygame

    pygame.init()
    try:
        world = World.desde_archivo(ruta_mundo)
        lista = list(estados)
        tam = theme.TAM_CELDA
        ancho_tablero = world.columnas * tam
        alto_tablero = world.filas * tam
        alto = max(
            alto_tablero + 2 * theme.PADDING_CHICO,
            theme.ALTO_MINIMO_ANIMACION,
        )
        ancho = ancho_tablero + theme.ANCHO_HUD_ANIMACION

        pantalla = pygame.display.set_mode((ancho, alto))
        pygame.display.set_caption(titulo)
        reloj = pygame.time.Clock()

        sprites = _cargar_sprites(pygame, tam)
        acumulados = report_panel.costos_acumulados(lista)
        total = len(lista)
        dx = 0
        dy = (alto - alto_tablero) // 2

        paso = 0
        pausado = False
        velocidad = theme.VELOCIDAD_ANIMACION
        acumulador = 0.0
        ejecutando = True

        while ejecutando:
            dt = reloj.tick(60) / 1000.0
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    ejecutando = False
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        ejecutando = False
                    elif evento.key == pygame.K_SPACE:
                        pausado = not pausado
                    elif evento.key == pygame.K_RIGHT:
                        paso = min(total - 1, paso + 1) if total else 0
                        pausado = True
                    elif evento.key == pygame.K_LEFT:
                        paso = max(0, paso - 1)
                        pausado = True
                    elif evento.key == pygame.K_UP:
                        velocidad = min(16.0, velocidad * 1.25)
                    elif evento.key == pygame.K_DOWN:
                        velocidad = max(0.5, velocidad / 1.25)
                    elif evento.key == pygame.K_r:
                        paso = 0
                        acumulador = 0.0
                        pausado = False

            if not pausado and paso < total - 1:
                acumulador += dt
                intervalo = 1.0 / max(velocidad, 0.01)
                while acumulador >= intervalo and paso < total - 1:
                    paso += 1
                    acumulador -= intervalo

            pantalla.fill(theme.COLOR_FONDO)
            if lista:
                estado = lista[paso]
                _dibujar_tablero(
                    pygame, pantalla, world, estado, sprites, tam, dx, dy
                )
                _dibujar_hud(
                    pygame, pantalla, alto, world, estado, paso, total,
                    acumulados[paso], velocidad, pausado, sprites, tam,
                    resumen,
                )
            pygame.display.flip()
    finally:
        pygame.quit()


def lanzar_animacion(
    ruta_mundo: str,
    estados: list[Estado],
    titulo: str,
    resumen: list[tuple[str, str]] | None = None,
) -> None:
    """Lanza la animación en un proceso nuevo con contexto "spawn"."""
    global _proceso
    detener_animacion()
    _proceso = _contexto.Process(
        target=ejecutar_animacion,
        args=(ruta_mundo, estados, titulo, resumen),
        daemon=True,
    )
    _proceso.start()


def detener_animacion() -> None:
    """Termina el proceso de animación si sigue vivo."""
    global _proceso
    if _proceso is not None:
        if _proceso.is_alive():
            _proceso.terminate()
        _proceso.join(timeout=2)
        _proceso = None


def en_ejecucion() -> bool:
    """Indica si la ventana de animación sigue abierta."""
    return _proceso is not None and _proceso.is_alive()
