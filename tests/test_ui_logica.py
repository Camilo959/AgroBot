"""Pruebas de la lógica pura de la UI (sin abrir ventanas)."""

from __future__ import annotations

from types import SimpleNamespace

from PIL import Image

from algoritmos.base import Resultado
from core.estado import Estado
from ui import assets_loader, animator, report_panel, theme, textos
from ui.screens import PANTALLAS


def _resultado(
    exito: bool = True,
    limite: bool = False,
    costo: float | None = 1.5,
) -> Resultado:
    estados = [
        Estado((0, 0), 0, -1, frozenset({(0, 1)})),
        Estado((0, 1), 1, -1, frozenset()),
    ]
    return Resultado(
        exito=exito,
        camino=["derecha"] if exito else [],
        estados=estados if exito else [],
        nodos_expandidos=5,
        nodos_generados=7,
        profundidad=1 if exito else 0,
        profundidad_maxima=3,
        tiempo=0.1234,
        costo=costo if exito else None,
        limite_alcanzado=limite,
    )


def test_reporte_sin_costo_para_amplitud_y_profundidad():
    for algoritmo in ("amplitud", "profundidad"):
        filas = dict(
            report_panel.construir_reporte(_resultado(), algoritmo)
        )
        assert textos.t("reporte_costo") not in filas
        assert filas[textos.t("reporte_algoritmo")] == (
            report_panel.nombre_algoritmo(algoritmo)
        )
        assert filas[textos.t("reporte_expandidos")] == "5"
        assert filas[textos.t("reporte_generados")] == "7"
        assert filas[textos.t("reporte_profundidad")] == "3"
        assert filas[textos.t("reporte_profundidad_solucion")] == "1"
        assert filas[textos.t("reporte_tiempo")] == "0.123 s"


def test_reporte_con_costo_para_costo_uniforme_y_astar():
    for algoritmo in ("costo_uniforme", "astar"):
        filas = dict(
            report_panel.construir_reporte(_resultado(), algoritmo)
        )
        assert filas[textos.t("reporte_costo")] == "1.5"


def test_reporte_completo_incluye_mundo():
    filas = dict(
        report_panel.construir_reporte_completo(
            _resultado(), "costo_uniforme", "worlds/Prueba1.txt"
        )
    )
    assert filas[textos.t("reporte_mundo")] == "Prueba1.txt"
    assert filas[textos.t("reporte_costo")] == "1.5"
    assert filas[textos.t("reporte_estado")] == textos.t("reporte_exito")


def test_reporte_completo_sin_ruta_no_agrega_mundo():
    filas = dict(
        report_panel.construir_reporte_completo(_resultado(), "amplitud")
    )
    assert textos.t("reporte_mundo") not in filas


def test_reporte_sin_solucion():
    filas = dict(
        report_panel.construir_reporte(_resultado(exito=False), "amplitud")
    )
    assert filas[textos.t("reporte_estado")] == textos.t(
        "reporte_sin_solucion"
    )
    assert textos.t("reporte_costo") not in filas
    assert textos.t("reporte_profundidad_solucion") not in filas
    assert filas[textos.t("reporte_generados")] == "7"
    assert filas[textos.t("reporte_profundidad")] == "3"


def test_reporte_limite_alcanzado():
    filas = dict(
        report_panel.construir_reporte(
            _resultado(exito=False, limite=True), "costo_uniforme"
        )
    )
    assert filas[textos.t("reporte_estado")] == textos.t(
        "reporte_limite"
    )
    assert textos.t("reporte_costo") not in filas
    assert textos.t("reporte_profundidad_solucion") not in filas


def test_costo_por_paso_y_acumulado():
    estados = [
        Estado((0, 0), 0, -1, frozenset()),
        Estado((0, 1), 0, 30, frozenset()),
        Estado((0, 2), 0, 29, frozenset()),
        Estado((0, 3), 0, 0, frozenset()),
        Estado((0, 4), 0, 0, frozenset()),
    ]
    costos = [report_panel.costo_paso(e) for e in estados[:-1]]
    assert costos == [1.0, 0.5, 0.5, 1.0]
    assert report_panel.costos_acumulados(estados) == [0.0, 1.0, 1.5, 2.0, 3.0]
    assert report_panel.costo_total(estados) == 3.0
    assert report_panel.costos_acumulados([]) == []


def test_geometria_de_celdas():
    assert theme.celda_a_pixeles(0, 0, 48) == (0, 0)
    assert theme.celda_a_pixeles(2, 3, 48) == (144, 96)
    assert theme.celda_a_pixeles(1, 1, 16) == (16, 16)
    assert theme.ajustar_tam_celda(480, 480, 10, 10) == 48
    assert theme.ajustar_tam_celda(100, 100, 10, 10) == 16
    assert theme.ajustar_tam_celda(500, 500, 10, 10) == 48


def test_rect_boton_resultados_no_se_solapa_con_controles():
    x, y, ancho, alto = animator.rect_boton_resultados(
        theme.ALTO_MINIMO_ANIMACION, 480, theme.ANCHO_HUD_ANIMACION
    )
    assert x == 480 + theme.PADDING
    assert ancho == theme.ANCHO_HUD_ANIMACION - 2 * theme.PADDING
    assert alto == animator.ALTO_BOTON_RESULTADOS
    assert y + alto < theme.ALTO_MINIMO_ANIMACION - 150


def test_preprocesado_robot(tmp_path):
    destino = tmp_path / "robot_128.png"
    resultado = assets_loader.preprocesar_robot(
        theme.ruta_asset("robot"), destino
    )
    assert resultado.is_file()
    with Image.open(resultado) as imagen:
        assert imagen.size == (128, 128)
        assert imagen.mode == "RGBA"
        alfa = imagen.getchannel("A")
        for esquina in [(0, 0), (127, 0), (0, 127), (127, 127)]:
            assert alfa.getpixel(esquina) == 0
        assert alfa.getpixel((64, 64)) == 255


def test_nearest_conserva_tamano_en_sprites_de_16_px():
    sprite = assets_loader.obtener_sprite("casilla", theme.TAM_CELDA)
    assert sprite.size == (theme.TAM_CELDA, theme.TAM_CELDA)
    assert sprite.mode == "RGBA"

    pequena = Image.new("RGBA", (2, 2))
    pequena.putpixel((0, 0), (255, 0, 0, 255))
    pequena.putpixel((1, 0), (0, 255, 0, 255))
    pequena.putpixel((0, 1), (0, 0, 255, 255))
    pequena.putpixel((1, 1), (255, 255, 0, 255))
    escalada = assets_loader.escalar_nearest(pequena, 48)
    assert escalada.size == (48, 48)
    assert escalada.getpixel((0, 0)) == (255, 0, 0, 255)
    assert escalada.getpixel((47, 47)) == (255, 255, 0, 255)


def test_registro_de_pantallas():
    assert set(PANTALLAS) == {"juego", "resumen"}
    for clase in PANTALLAS.values():
        assert callable(clase)


def test_reporte_sin_costo_para_avara():
    filas = dict(
        report_panel.construir_reporte(_resultado(), "avara")
    )
    assert textos.t("reporte_costo") not in filas
    assert filas[textos.t("reporte_algoritmo")] == "Avara"


def _resultado_con_avioneta() -> Resultado:
    """Resultado de 3 pasos: uno de costo 1.0 y dos de costo 0.5."""
    estados = [
        Estado((0, 0), 0, -1, frozenset({(0, 1)})),
        Estado((0, 1), 0, 30, frozenset({(0, 1)})),
        Estado((0, 2), 0, 29, frozenset({(0, 1)})),
        Estado((0, 3), 0, 0, frozenset()),
    ]
    return Resultado(
        exito=True,
        camino=["derecha", "derecha", "derecha"],
        estados=estados,
        nodos_expandidos=10,
        nodos_generados=15,
        profundidad=3,
        profundidad_maxima=4,
        tiempo=0.5,
        costo=2.0,
    )


def test_pasos_y_costos_por_tipo():
    resultado = _resultado_con_avioneta()
    assert report_panel.pasos_por_costo(resultado) == (1, 2)
    assert report_panel.costo_por_tipo(resultado) == (1.0, 1.0)


def test_detalle_busqueda_incluye_tipo_nodos_segundo_y_limite():
    filas = dict(
        report_panel.construir_detalle_busqueda(
            _resultado_con_avioneta(),
            "costo_uniforme",
            "no_informada",
            500_000,
            "worlds/Prueba1.txt",
        )
    )
    assert filas[textos.t("detalle_tipo_busqueda")] == (
        textos.t("tipo_no_informada")
    )
    assert filas[textos.t("detalle_nodos_segundo")] == "20.0"
    assert filas[textos.t("detalle_limite_usado")] == "500000"
    assert filas[textos.t("reporte_mundo")] == "Prueba1.txt"


def test_detalle_solucion_muestra_costos_solo_para_costo_uniforme_y_astar():
    resultado = _resultado_con_avioneta()
    mundo = SimpleNamespace(cultivos=frozenset({(0, 1)}))

    for algoritmo in ("costo_uniforme", "astar"):
        filas = dict(
            report_panel.construir_detalle_solucion(
                resultado, algoritmo, mundo
            )
        )
        assert filas[textos.t("reporte_costo")] == "2.0"
        assert filas[textos.t("detalle_pasos_costo_uno")] == "1"
        assert filas[textos.t("detalle_pasos_costo_media")] == "2"
        assert filas[textos.t("detalle_costo_pasos_uno")] == "1.0"
        assert filas[textos.t("detalle_costo_pasos_media")] == "1.0"


def test_detalle_solucion_no_muestra_costos_en_otros_algoritmos():
    resultado = _resultado_con_avioneta()
    mundo = SimpleNamespace(cultivos=frozenset({(0, 1)}))

    for algoritmo in ("amplitud", "profundidad", "avara"):
        filas = dict(
            report_panel.construir_detalle_solucion(
                resultado, algoritmo, mundo
            )
        )
        assert textos.t("reporte_costo") not in filas
        assert textos.t("detalle_costo_pasos_uno") not in filas
        assert textos.t("detalle_costo_pasos_media") not in filas
        assert filas[textos.t("detalle_pasos_costo_uno")] == "1"
        assert filas[textos.t("detalle_pasos_costo_media")] == "2"


def test_detalle_solucion_incluye_estado_final_y_cultivos():
    filas = dict(
        report_panel.construir_detalle_solucion(
            _resultado_con_avioneta(),
            "costo_uniforme",
            SimpleNamespace(cultivos=frozenset({(0, 1)})),
        )
    )
    assert filas[textos.t("detalle_cultivos_tratados")] == "1 / 1"
    assert filas[textos.t("detalle_posicion_final")] == "(0, 3)"
    assert filas[textos.t("detalle_fertilizante_final")] == "0 / 2"
    assert filas[textos.t("detalle_combustible_final")] == (
        textos.t("detalle_combustible_agotada")
    )


def test_detalle_solucion_vacio_si_no_hay_exito():
    resultado = Resultado(exito=False, nodos_expandidos=3)
    assert report_panel.construir_detalle_solucion(
        resultado, "costo_uniforme", SimpleNamespace(cultivos=frozenset())
    ) == []
