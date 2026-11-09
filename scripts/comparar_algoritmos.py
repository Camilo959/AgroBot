"""Compara los cinco algoritmos sobre `worlds/Prueba1.txt`.

Ejecuta BFS, UCS, DFS, Avara y A* y muestra la tabla de la sección 5 de
`docs/CONTEXTO_BUSQUEDA_INFORMADA.md`:

alg | exito | nodos_expandidos | nodos_generados |
profundidad | profundidad_maxima | tiempo | costo

Uso (desde la raíz del proyecto):
    python scripts/comparar_algoritmos.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from algorithms.astar import busqueda_a_estrella
from algorithms.base import Resultado
from algorithms.bfs import busqueda_amplitud
from algorithms.dfs import busqueda_profundidad
from algorithms.greedy import busqueda_avara
from algorithms.heuristics import HeuristicaAgroBot
from algorithms.ucs import busqueda_costo_uniforme
from core.problem import Problema
from core.world import World


def fila(nombre: str, r: Resultado) -> str:
    """Formatea una fila de la tabla de comparación."""
    costo = f"{r.costo:.1f}" if r.costo is not None else "-"
    return (
        f"{nombre:<6} {str(r.exito):<6} "
        f"{r.nodos_expandidos:<17} {r.nodos_generados:<16} "
        f"{r.profundidad:<11} {r.profundidad_maxima:<18} "
        f"{r.tiempo:<8.2f} {costo}"
    )


def main() -> None:
    """Corre los cinco experimentos y muestra la tabla."""
    ruta = Path(__file__).resolve().parent.parent / "worlds" / "Prueba1.txt"
    mundo = World.desde_archivo(str(ruta))
    problema = Problema(mundo)
    heuristica = HeuristicaAgroBot(mundo)

    experimentos = [
        ("BFS", busqueda_amplitud(problema)),
        ("UCS", busqueda_costo_uniforme(problema)),
        ("DFS", busqueda_profundidad(problema)),
        ("Avara", busqueda_avara(problema, heuristica)),
        ("A*", busqueda_a_estrella(problema, heuristica)),
    ]

    print(
        f"{'alg':<6} {'exito':<6} "
        f"{'expandidos':<17} {'generados':<16} "
        f"{'prof':<11} {'prof_max':<18} "
        f"{'tiempo':<8} costo"
    )
    for nombre, resultado in experimentos:
        print(fila(nombre, resultado))
        if resultado.limite_alcanzado:
            print(f"  (nota: {nombre} chocó con el límite de nodos)")


if __name__ == "__main__":
    main()
