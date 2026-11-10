"""Compara BFS, UCS y DFS sobre `worlds/Prueba1.txt`.

Muestra la tabla de la sección 8 de
`docs/CONTEXTO_BUSQUEDA_NO_INFORMADA.md`:

algoritmo | exito | nodos_expandidos | nodos_generados |
profundidad | profundidad_maxima | tiempo | costo

Los tres algoritmos evitan ciclos solo por rama.

Uso (desde la raíz del proyecto):
    python scripts/comparar_no_informada.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from algoritmos.base import Resultado
from algoritmos.busqueda_no_informada.amplitud import busqueda_amplitud
from algoritmos.busqueda_no_informada.profundidad import busqueda_profundidad
from algoritmos.busqueda_no_informada.costo_uniforme import busqueda_costo_uniforme
from core.problema import Problema
from core.mundo import World


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
    """Corre los tres experimentos y muestra la tabla."""
    ruta = Path(__file__).resolve().parent.parent / "worlds" / "Prueba1.txt"
    problema = Problema(World.desde_archivo(str(ruta)))

    experimentos = [
        ("BFS", busqueda_amplitud(problema)),
        ("UCS", busqueda_costo_uniforme(problema)),
        ("DFS", busqueda_profundidad(problema)),
    ]

    print(
        f"{'alg':<6} {'exito':<6} "
        f"{'expandidos':<17} {'generados':<16} "
        f"{'prof':<11} {'prof_max':<18} "
        f"{'tiempo':<8} costo"
    )
    for nombre, r in experimentos:
        print(fila(nombre, r))
        if r.limite_alcanzado:
            print(f"  (nota: {nombre} chocó con el límite de nodos)")


if __name__ == "__main__":
    main()
