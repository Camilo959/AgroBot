"""Pruebas de BFS, UCS y DFS (casos de la especificación).

Los mundos se arman como matrices 10x10 en archivos temporales (`tmp_path`)
y se cargan con `World.desde_archivo`. Todos los algoritmos se ejecutan con
un límite de nodos para que ninguna prueba pueda colgarse.
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
LIMITE_PRUEBAS = 200_000

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


def mundo_pasillos(tmp_path: Path) -> Problema:
    """Anillo de pasillos estrechos con dos rutas entre robot y cultivo.

    Robot (9, 1), depósito (8, 1), avioneta (8, 2), cultivo (1, 7).
    Ruta directa: 1 + 13 = 14 pasos, costo 14.
    Ruta con avioneta: 1 + 15 = 16 pasos, costo 1 + 14*0.5 + 1 = 9.
    BFS elige la ruta de menos pasos; UCS elige la de menor costo.
    """
    abiertos: set[tuple[int, int]] = set()
    for columna in range(1, 9):
        abiertos.add((1, columna))
        abiertos.add((8, columna))
    for fila in range(1, 9):
        abiertos.add((fila, 1))
        abiertos.add((fila, 8))

    robot = (9, 1)
    deposito = (8, 1)
    avioneta = (8, 2)
    cultivo = (1, 7)
    abiertos.update({robot, deposito, avioneta, cultivo})

    muros = tuple(
        (fila, columna)
        for fila in range(10)
        for columna in range(10)
        if (fila, columna) not in abiertos
    )
    return escribir_mundo(
        tmp_path, "pasillos.txt",
        robot=robot, deposito=deposito, avioneta=avioneta,
        cultivos=(cultivo,), muros=muros,
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
        r = buscar(p, limite_nodos=LIMITE_PRUEBAS)
        assert r.exito is True
        assert r.limite_alcanzado is False
        assert r.camino == []
        assert r.costo == 0
        assert r.nodos_expandidos == 1


@pytest.mark.parametrize("buscar", TODOS)
def test_2_un_cultivo_cerca_todos_resuelven(tmp_path, buscar):
    r = buscar(mundo_cerca(tmp_path), limite_nodos=LIMITE_PRUEBAS)
    assert r.exito is True
    assert r.limite_alcanzado is False
    assert r.costo is not None


@pytest.mark.parametrize("buscar", TODOS)
def test_3_solucion_valida_reproducible(tmp_path, buscar):
    p = mundo_cerca(tmp_path)
    r = buscar(p, limite_nodos=LIMITE_PRUEBAS)
    assert r.limite_alcanzado is False
    validar_reproduccion(p, r)


def test_3b_solucion_valida_en_prueba1():
    p = Problema(World.desde_archivo(str(RUTA_PRUEBA1)))
    bfs = busqueda_amplitud(p, limite_nodos=LIMITE_PRUEBAS)
    ucs = busqueda_costo_uniforme(p, limite_nodos=LIMITE_PRUEBAS)
    assert bfs.limite_alcanzado is False
    assert ucs.limite_alcanzado is False
    validar_reproduccion(p, bfs)
    validar_reproduccion(p, ucs)


def test_4_optimalidad_ucs(tmp_path):
    """UCS no es más caro que BFS ni que DFS en pasillos estrechos."""
    p = mundo_pasillos(tmp_path)
    bfs = busqueda_amplitud(p, limite_nodos=LIMITE_PRUEBAS)
    ucs = busqueda_costo_uniforme(p, limite_nodos=LIMITE_PRUEBAS)
    dfs = busqueda_profundidad(p, limite_nodos=LIMITE_PRUEBAS)
    for r in (bfs, ucs, dfs):
        assert r.exito is True
        assert r.limite_alcanzado is False
    assert ucs.costo <= bfs.costo
    assert ucs.costo <= dfs.costo


def test_5_bfs_mas_caro_que_ucs_por_avioneta(tmp_path):
    """BFS minimiza pasos, no costo; UCS abarata con la avioneta."""
    p = mundo_pasillos(tmp_path)
    bfs = busqueda_amplitud(p, limite_nodos=LIMITE_PRUEBAS)
    ucs = busqueda_costo_uniforme(p, limite_nodos=LIMITE_PRUEBAS)
    assert bfs.exito is True and ucs.exito is True
    assert bfs.limite_alcanzado is False
    assert ucs.limite_alcanzado is False
    assert bfs.costo == 14.0
    assert ucs.costo == 9.0
    assert bfs.costo > ucs.costo


def mundo_sin_solucion(tmp_path: Path) -> Problema:
    """Depósito inalcanzable: el robot queda encerrado en (1, 1)."""
    return escribir_mundo(
        tmp_path, "cerrado.txt",
        robot=(1, 1), deposito=(5, 5), avioneta=(9, 9),
        cultivos=((5, 6),),
        muros=((0, 1), (2, 1), (1, 0), (1, 2)),
    )


@pytest.mark.parametrize("buscar", TODOS)
def test_6_sin_solucion(tmp_path, buscar):
    r = buscar(mundo_sin_solucion(tmp_path), limite_nodos=LIMITE_PRUEBAS)
    assert r.exito is False
    assert r.camino == []
    assert r.costo is None
    assert r.limite_alcanzado is False


def fases(estado) -> str:
    return clave_relajada(estado)[3]


@pytest.mark.parametrize("buscar", TODOS)
def test_7_sin_oscilacion(tmp_path, buscar):
    r = buscar(mundo_cerca(tmp_path), limite_nodos=LIMITE_PRUEBAS)
    assert r.exito
    assert r.limite_alcanzado is False
    for i in range(len(r.estados) - 2):
        if r.estados[i].pos == r.estados[i + 2].pos:
            a, b = r.estados[i], r.estados[i + 2]
            assert (
                a.fertilizante != b.fertilizante
                or a.cultivos_pendientes != b.cultivos_pendientes
                or fases(a) != fases(b)
            ), f"oscilación sin cambio en los pasos {i}..{i + 2}"


def test_8_meta_al_extraer_cuenta_como_expandido(tmp_path):
    r = busqueda_amplitud(
        mundo_cerca(tmp_path), limite_nodos=LIMITE_PRUEBAS
    )
    assert r.exito
    assert r.limite_alcanzado is False
    # Raíz + un expandido por cada paso del camino, como mínimo.
    assert r.nodos_expandidos >= len(r.camino) + 1


def test_9_dfs_apila_en_orden_inverso(tmp_path):
    r = busqueda_profundidad(
        mundo_cerca(tmp_path), limite_nodos=LIMITE_PRUEBAS
    )
    assert r.exito
    assert r.limite_alcanzado is False
    # Desde (5, 5) todo está libre: el primer operador (arriba) sale primero.
    assert r.camino[0] == "arriba"


@pytest.mark.parametrize("buscar", TODOS)
def test_10_limite_nodos(tmp_path, buscar):
    r = buscar(mundo_cerca(tmp_path), limite_nodos=3)
    assert r.exito is False
    assert r.limite_alcanzado is True
