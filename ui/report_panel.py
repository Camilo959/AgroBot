"""Lógica pura del reporte de resultados y del costo por paso.

No depende de tkinter ni de pygame para poder probarse sin abrir ventanas.
"""

from __future__ import annotations

from pathlib import Path

from core.estado import Estado
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
        - Nodos expandidos, profundidad del árbol (profundidad_maxima) y
          tiempo se muestran siempre.
        - El costo de la solución solo aparece para "Costo uniforme" (y
          A* cuando exista).
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
        (textos.t("reporte_profundidad"), str(resultado.profundidad_maxima)),
        (textos.t("reporte_tiempo"), f"{resultado.tiempo:.3f} s"),
    ]

    if resultado.exito:
        filas.append((textos.t("reporte_pasos"), str(len(resultado.camino))))
        if algoritmo in ALGORITMOS_CON_COSTO and resultado.costo is not None:
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
