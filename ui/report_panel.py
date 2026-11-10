"""Lógica pura del reporte de resultados y del costo por paso.

No depende de tkinter ni de pygame para poder probarse sin abrir ventanas.
"""

from __future__ import annotations

from pathlib import Path

from core.estado import Estado
from core.mundo import World
from core.problema import Problema
from algoritmos.base import Resultado
from ui import textos

#: Algoritmos cuyos resultados reportan costo de solución.
ALGORITMOS_CON_COSTO: frozenset[str] = frozenset({"costo_uniforme", "astar"})

_CLAVES_NOMBRE: dict[str, str] = {
    "amplitud": "alg_amplitud",
    "costo_uniforme": "alg_costo_uniforme",
    "profundidad": "alg_profundidad",
    "avara": "alg_avara",
    "astar": "alg_astar",
}


def nombre_algoritmo(algoritmo: str | None) -> str:
    """Devuelve el nombre legible de un algoritmo."""
    if algoritmo is None:
        return "-"
    clave = _CLAVES_NOMBRE.get(algoritmo)
    return textos.t(clave) if clave else algoritmo


def costo_paso(estado_previo: Estado) -> float:
    """Costo de moverse desde `estado_previo`: 0.5 en vuelo, 1 en otro caso."""
    return 0.5 if estado_previo.combustible > 0 else 1.0


def costos_acumulados(estados: list[Estado]) -> list[float]:
    """Costo acumulado en cada estado; el primero siempre cuesta 0."""
    if not estados:
        return []
    acumulados = [0.0]
    for anterior in estados[:-1]:
        acumulados.append(acumulados[-1] + costo_paso(anterior))
    return acumulados


def costo_total(estados: list[Estado]) -> float:
    """Costo total de una secuencia de estados."""
    acumulados = costos_acumulados(estados)
    return acumulados[-1] if acumulados else 0.0


def construir_reporte(
    resultado: Resultado,
    algoritmo: str | None,
) -> list[tuple[str, str]]:
    """Construye las filas (etiqueta, valor) del reporte de resultados.

    Reglas:
        - Nodos expandidos, nodos generados, profundidad máxima del árbol
          y tiempo se muestran siempre.
        - La profundidad de la solución solo aparece cuando hay éxito.
        - El costo de la solución solo aparece para "Costo uniforme" y A*.
        - Sin solución y límite alcanzado se indican en la fila "Estado".
    """
    if resultado.exito:
        estado = textos.t("reporte_exito")
    elif resultado.limite_alcanzado:
        estado = textos.t("reporte_limite")
    else:
        estado = textos.t("reporte_sin_solucion")

    filas: list[tuple[str, str]] = [
        (textos.t("reporte_algoritmo"), nombre_algoritmo(algoritmo)),
        (textos.t("reporte_estado"), estado),
        (textos.t("reporte_expandidos"), str(resultado.nodos_expandidos)),
        (textos.t("reporte_generados"), str(resultado.nodos_generados)),
    ]

    if resultado.exito:
        filas.append(
            (textos.t("reporte_profundidad_solucion"),
             str(resultado.profundidad))
        )

    filas.extend([
        (textos.t("reporte_profundidad"), str(resultado.profundidad_maxima)),
        (textos.t("reporte_tiempo"), f"{resultado.tiempo:.3f} s"),
    ])

    if (
        resultado.exito
        and algoritmo in ALGORITMOS_CON_COSTO
        and resultado.costo is not None
    ):
        filas.append(
            (textos.t("reporte_costo"), f"{resultado.costo:.1f}")
        )

    return filas


def construir_reporte_completo(
    resultado: Resultado,
    algoritmo: str | None,
    ruta_mundo: str | Path | None = None,
) -> list[tuple[str, str]]:
    """Reporte del resumen más la fila del mundo cargado (si se conoce).

    Se usa tanto en la pantalla de resumen como en el HUD de la animación
    para que ambos muestren exactamente las mismas filas.
    """
    filas = construir_reporte(resultado, algoritmo)
    if ruta_mundo:
        filas.append(
            (textos.t("reporte_mundo"), Path(ruta_mundo).name)
        )
    return filas


def _texto_estado(resultado: Resultado) -> str:
    """Texto del estado de la búsqueda."""
    if resultado.exito:
        return textos.t("reporte_exito")
    if resultado.limite_alcanzado:
        return textos.t("reporte_limite")
    return textos.t("reporte_sin_solucion")


def _texto_tipo_busqueda(tipo_busqueda: str | None) -> str:
    """Texto legible del tipo de búsqueda."""
    if tipo_busqueda == "informada":
        return textos.t("tipo_informada")
    if tipo_busqueda == "no_informada":
        return textos.t("tipo_no_informada")
    return "-"


def _texto_combustible(combustible: int) -> str:
    """Texto legible del combustible final de la avioneta."""
    if combustible == -1:
        return textos.t("detalle_combustible_sin_abordar")
    if combustible == 0:
        return textos.t("detalle_combustible_agotada")
    return f"{combustible} / {Problema.COMBUSTIBLE_INICIAL}"


def _nodos_por_segundo(resultado: Resultado) -> str:
    """Nodos expandidos por segundo, o un guion si el tiempo es cero."""
    if resultado.tiempo <= 0:
        return "—"
    return f"{resultado.nodos_expandidos / resultado.tiempo:.1f}"


def pasos_por_costo(resultado: Resultado) -> tuple[int, int]:
    """Devuelve (pasos con costo 1.0, pasos con costo 0.5).

    Un paso cuesta 0.5 cuando el robot ya venía en la avioneta con
    combustible, es decir, cuando el estado previo tiene `combustible > 0`.
    El paso que sube a la avioneta cuesta 1.0 y cuenta como paso a pie.
    """
    pasos_uno = 0
    pasos_media = 0
    for estado_previo in resultado.estados[:-1]:
        if costo_paso(estado_previo) == 0.5:
            pasos_media += 1
        else:
            pasos_uno += 1
    return pasos_uno, pasos_media


def costo_por_tipo(resultado: Resultado) -> tuple[float, float]:
    """Devuelve (costo de pasos de 1.0, costo de pasos de 0.5)."""
    pasos_uno, pasos_media = pasos_por_costo(resultado)
    return float(pasos_uno), 0.5 * pasos_media


def construir_detalle_busqueda(
    resultado: Resultado,
    algoritmo: str | None,
    tipo_busqueda: str | None,
    limite_nodos: int | None,
    ruta_mundo: str | Path | None = None,
) -> list[tuple[str, str]]:
    """Filas detalladas de la búsqueda para la pantalla de resumen."""
    filas: list[tuple[str, str]] = [
        (textos.t("reporte_algoritmo"), nombre_algoritmo(algoritmo)),
        (textos.t("detalle_tipo_busqueda"),
         _texto_tipo_busqueda(tipo_busqueda)),
        (textos.t("reporte_estado"), _texto_estado(resultado)),
        (textos.t("reporte_expandidos"), str(resultado.nodos_expandidos)),
        (textos.t("reporte_generados"), str(resultado.nodos_generados)),
        (textos.t("reporte_profundidad"), str(resultado.profundidad_maxima)),
        (textos.t("reporte_tiempo"), f"{resultado.tiempo:.3f} s"),
        (textos.t("detalle_nodos_segundo"), _nodos_por_segundo(resultado)),
        (textos.t("detalle_limite_usado"),
         "—" if limite_nodos is None else str(limite_nodos)),
    ]
    if ruta_mundo:
        filas.append(
            (textos.t("reporte_mundo"), Path(ruta_mundo).name)
        )
    return filas


def construir_detalle_solucion(
    resultado: Resultado,
    algoritmo: str | None,
    mundo: World | None,
) -> list[tuple[str, str]]:
    """Filas detalladas de la solución; vacío si no hubo solución."""
    if not resultado.exito or not resultado.estados:
        return []

    final = resultado.estados[-1]
    pasos_uno, pasos_media = pasos_por_costo(resultado)
    mostrar_costo = (
        algoritmo in ALGORITMOS_CON_COSTO
        and resultado.costo is not None
    )

    filas: list[tuple[str, str]] = [
        (textos.t("reporte_profundidad_solucion"), str(resultado.profundidad)),
    ]
    if mostrar_costo:
        filas.append(
            (textos.t("reporte_costo"), f"{resultado.costo:.1f}")
        )

    filas.extend([
        (textos.t("detalle_pasos_costo_uno"), str(pasos_uno)),
        (textos.t("detalle_pasos_costo_media"), str(pasos_media)),
    ])

    if mostrar_costo:
        costo_uno, costo_media = costo_por_tipo(resultado)
        filas.extend([
            (textos.t("detalle_costo_pasos_uno"), f"{costo_uno:.1f}"),
            (textos.t("detalle_costo_pasos_media"), f"{costo_media:.1f}"),
        ])

    if mundo is not None:
        total = len(mundo.cultivos)
        tratados = total - len(final.cultivos_pendientes)
        filas.append(
            (textos.t("detalle_cultivos_tratados"),
             f"{tratados} / {total}")
        )

    filas.extend([
        (textos.t("detalle_posicion_final"),
         f"({final.pos[0]}, {final.pos[1]})"),
        (textos.t("detalle_fertilizante_final"),
         f"{final.fertilizante} / {Problema.CAPACIDAD_FERTILIZANTE}"),
        (textos.t("detalle_combustible_final"),
         _texto_combustible(final.combustible)),
    ])
    return filas
