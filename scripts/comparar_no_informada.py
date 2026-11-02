"""Compara BFS, UCS y DFS sobre `worlds/Prueba1.txt`.

Muestra la tabla de la sección 8 de
`docs/CONTEXTO_BUSQUEDA_NO_INFORMADA.md`:

algoritmo | modo_ciclos | exito | nodos_expandidos | nodos_generados |
profundidad | profundidad_maxima | tiempo | costo

Los modos "rama" de BFS y UCS se corren con `limite_nodos=2_000_000`.

Uso (desde la raíz del proyecto):
    python scripts/comparar_no_informada.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from algorithms.base import Resultado
from algorithms.bfs import busqueda_amplitud
from algorithms.dfs import busqueda_profundidad
from algorithms.ucs import busqueda_costo_uniforme
from core.problem import Problema
from core.world import World

LIMITE_RAMA = 2_000_000


def fila(nombre: str, modo: str, r: Resultado) -> str:
    """Formatea una fila de la tabla de comparación."""
    costo = f"{r.costo:.1f}" if r.costo is not None else "-"
    return (
        f"{nombre:<6} {modo:<10} {str(r.exito):<6} "
        f"{r.nodos_expandidos:<17} {r.nodos_generados:<16} "
        f"{r.profundidad:<11} {r.profundidad_maxima:<18} "
        f"{r.tiempo:<8.2f} {costo}"
    )


def main() -> None:
    """Corre los cinco experimentos y muestra la tabla."""
    ruta = Path(__file__).resolve().parent.parent / "worlds" / "Prueba1.txt"
    problema = Problema(World.desde_archivo(str(ruta)))

    experimentos = [
        ("BFS", "global", busqueda_amplitud(problema, modo_ciclos="global")),
        ("UCS", "global", busqueda_costo_uniforme(problema, modo_ciclos="global")),
        ("DFS", "rama", busqueda_profundidad(problema, modo_ciclos="rama")),
        ("BFS", "rama", busqueda_amplitud(
            problema, modo_ciclos="rama", limite_nodos=LIMITE_RAMA)),
        ("UCS", "rama", busqueda_costo_uniforme(
            problema, modo_ciclos="rama", limite_nodos=LIMITE_RAMA)),
    ]

    print(
        f"{'alg':<6} {'modo':<10} {'exito':<6} "
        f"{'expandidos':<17} {'generados':<16} "
        f"{'prof':<11} {'prof_max':<18} "
        f"{'tiempo':<8} costo"
    )
    for nombre, modo, r in experimentos:
        print(fila(nombre, modo, r))
        if r.limite_alcanzado:
            print(f"  (nota: {nombre} {modo} chocó con el límite de "
                  f"{LIMITE_RAMA} nodos)")


if __name__ == "__main__":
    main()
