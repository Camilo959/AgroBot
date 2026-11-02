"""Pruebas de BFS, UCS y DFS (12 casos de la especificación).

Los mundos se arman como matrices 10x10 en archivos temporales (`tmp_path`)
y se cargan con `World.desde_archivo`.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from algorithms.base import clave_relajada
from algorithms.bfs import busqueda_amplitud
from algorithms.dfs import busqueda_profundidad
from algorithms.ucs import busqueda_costo_uniforme
from core.problem import Problema
from core.world import World

RUTA_PRUEBA1 = Path(__file__).resolve().parent.parent / "worlds" / "Prueba1.txt"

TODOS = [busqueda_amplitud, busqueda_costo_uniforme, busqueda_profundidad]


def escribir_mundo(
    tmp_path: Path,
    nombre: str,
    robot: tuple[int, int],
    deposito: tuple[int, int],
    avioneta: tuple[int, int],
    cultivos: tuple[tuple[int, int], ...] = (),
    muros: tuple[tuple[int, int], ...] = (),
) -> Problema:
    """Arma un mundo 10x10 abierto con las piezas indicadas."""
    filas = [[0] * 10 for _ in range(10)]
    filas[robot[0]][robot[1]] = 2
    filas[deposito[0]][deposito[1]] = 4
    filas[avioneta[0]][avioneta[1]] = 5
    for r, c in cultivos:
        filas[r][c] = 3
    for r, c in muros:
        filas[r][c] = 1
    ruta = tmp_path / nombre
    ruta.write_text(
        "\n".join(" ".join(str(v) for v in fila) for fila in filas) + "\n",
        encoding="utf-8",
    )
    return Problema(World.desde_archivo(str(ruta)))


def mundo_cerca(tmp_path: Path) -> Problema:
    """Un cultivo junto al depósito; avioneta lejos en una esquina."""
    return escribir_mundo(
        tmp_path, "cerca.txt",
        robot=(5, 5), deposito=(5, 4), avioneta=(9, 9),
        cultivos=((5, 3),),
    )


def validar_reproduccion(problema: Problema, resultado) -> None:
    """Reproduce el camino con `sucesores` y verifica meta y costo."""
    assert resultado.exito
    estado = problema.estado_inicial()
    total = 0.0
    for accion in resultado.camino:
        opciones = {a: (e, c) for a, e, c in problema.sucesores(estado)}
        assert accion in opciones, f"acción inválida: {accion}"
        estado, costo = opciones[accion]
        total += costo
    assert problema.es_meta(estado)
    # Los costos son 1 o 0.5: sumas exactas en punto flotante (d.10).
    assert total == resultado.costo


def test_1_sin_cultivos_meta_en_raiz(tmp_path):
    for buscar in TODOS:
        p = escribir_mundo(
            tmp_path, f"vacio_{buscar.__name__}.txt",
            robot=(5, 5), deposito=(0, 0), avioneta=(9, 9),
        )
        r = buscar(p)
        assert r.exito is True
        assert r.camino == []
        assert r.costo == 0
        assert r.nodos_expandidos == 1


@pytest.mark.parametrize("buscar", TODOS)
def test_2_un_cultivo_cerca_todos_resuelven(tmp_path, buscar):
    r = buscar(mundo_cerca(tmp_path))
    assert r.exito is True
    assert r.costo is not None


@pytest.mark.parametrize("buscar", TODOS)
def test_3_solucion_valida_reproducible(tmp_path, buscar):
    p = mundo_cerca(tmp_path)
    validar_reproduccion(p, buscar(p))


def test_3b_solucion_valida_en_prueba1():
    p = Problema(World.desde_archivo(str(RUTA_PRUEBA1)))
    validar_reproduccion(p, busqueda_amplitud(p))
    validar_reproduccion(p, busqueda_costo_uniforme(p))


def mundo_avioneta(tmp_path: Path) -> Problema:
    """Cuadrícula abierta donde el desvío por la avioneta abarata el viaje.

    Robot (9, 0), depósito (9, 1), cultivo (0, 9), avioneta (0, 0).
    Directo: 1 + 17 = 18 pasos a costo 1 → 18. Con avioneta: 20 pasos
    pero 1 + 10 + 9*0.5 = 15.5. Ningún camino de 18 pasos puede pasar por
    la avioneta (necesita mínimo 1 + 10 + 9 = 20), así que BFS queda en 18.
    """
    return escribir_mundo(
        tmp_path, "avioneta.txt",
        robot=(9, 0), deposito=(9, 1), avioneta=(0, 0),
        cultivos=((0, 9),),
    )


def test_4_optimalidad_ucs(tmp_path):
    """La optimalidad de UCS no depende del modo de ciclos.

    Se fija "global" en BFS y UCS porque este mundo abierto con la meta
    lejana hace que el modo "rama" explote en BFS (complejidad de caminos
    simples); el modo por defecto se cubre en `test_3b` sobre Prueba1.
    """
    p = mundo_avioneta(tmp_path)
    bfs = busqueda_amplitud(p, modo_ciclos="global")
    ucs = busqueda_costo_uniforme(p, modo_ciclos="global")
    dfs = busqueda_profundidad(p)
    assert bfs.exito and ucs.exito and dfs.exito
    assert ucs.costo <= bfs.costo
    assert ucs.costo <= dfs.costo


def test_5_bfs_mas_caro_que_ucs_por_avioneta(tmp_path):
    """BFS minimiza pasos, no costo; UCS sí abarata con la avioneta."""
    p = mundo_avioneta(tmp_path)
    bfs = busqueda_amplitud(p, modo_ciclos="global")
    ucs = busqueda_costo_uniforme(p, modo_ciclos="global")
    assert bfs.exito and ucs.exito
    assert bfs.costo == 18
    assert ucs.costo == 15.5
    assert bfs.costo > ucs.costo


def mundo_sin_solucion(tmp_path: Path) -> Problema:
    """Depósito inalcanzable: el robot queda encerrado en (1, 1).

    Se usa el depósito inalcanzable (en vez del cultivo encerrado en un
    mundo abierto) porque DFS por rama, sin cerrados globales, tendría que
    agotar todos los caminos simples del área abierta antes de fallar, lo
    cual es exponencial. El corte por límite para esos casos se prueba en
    el caso 11 y en el script de verificación.
    """
    return escribir_mundo(
        tmp_path, "cerrado.txt",
        robot=(1, 1), deposito=(5, 5), avioneta=(9, 9),
        cultivos=((5, 6),),
        muros=((0, 1), (2, 1), (1, 0), (1, 2)),
    )


@pytest.mark.parametrize("buscar", TODOS)
def test_6_sin_solucion(tmp_path, buscar):
    r = buscar(mundo_sin_solucion(tmp_path))
    assert r.exito is False
    assert r.camino == []
    assert r.costo is None
    assert r.limite_alcanzado is False


def fases(estado) -> str:
    return clave_relajada(estado)[3]


@pytest.mark.parametrize("buscar", TODOS)
def test_7_sin_oscilacion(tmp_path, buscar):
    r = buscar(mundo_cerca(tmp_path))
    assert r.exito
    for i in range(len(r.estados) - 2):
        if r.estados[i].pos == r.estados[i + 2].pos:
            a, b = r.estados[i], r.estados[i + 2]
            assert (
                a.fertilizante != b.fertilizante
                or a.cultivos_pendientes != b.cultivos_pendientes
                or fases(a) != fases(b)
            ), f"oscilación sin cambio en los pasos {i}..{i + 2}"


def test_8_meta_al_extraer_cuenta_como_expandido(tmp_path):
    r = busqueda_amplitud(mundo_cerca(tmp_path))
    assert r.exito
    # Raíz + un expandido por cada paso del camino, como mínimo.
    assert r.nodos_expandidos >= len(r.camino) + 1


def test_9_dfs_apila_en_orden_inverso(tmp_path):
    r = busqueda_profundidad(mundo_cerca(tmp_path))
    assert r.exito
    # Desde (5, 5) todo está libre: el primer operador (arriba) sale primero.
    assert r.camino[0] == "arriba"


@pytest.mark.parametrize("buscar", TODOS)
def test_10_modo_ciclos_invalido(buscar):
    p = Problema(World.desde_archivo(str(RUTA_PRUEBA1)))
    with pytest.raises(ValueError):
        buscar(p, modo_ciclos="globalmente")


@pytest.mark.parametrize("buscar", TODOS)
def test_11_limite_nodos(tmp_path, buscar):
    r = buscar(mundo_cerca(tmp_path), limite_nodos=3)
    assert r.exito is False
    assert r.limite_alcanzado is True


def test_12_ucs_global_y_rama_mismo_costo(tmp_path):
    for nombre, mundo in (
        ("cerca", mundo_cerca(tmp_path)),
        ("avioneta", mundo_avioneta(tmp_path)),
    ):
        g = busqueda_costo_uniforme(mundo, modo_ciclos="global")
        r = busqueda_costo_uniforme(mundo, modo_ciclos="rama")
        assert g.exito and r.exito, nombre
        assert g.costo == r.costo, nombre
