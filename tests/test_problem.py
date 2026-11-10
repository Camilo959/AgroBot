"""Pruebas del Problema, el Estado y el Nodo sobre worlds/Prueba1.txt."""

from __future__ import annotations

import heapq
from pathlib import Path

from core.nodo import Nodo
from core.problema import Problema
from core.estado import Estado
from core.mundo import World

RUTA_PRUEBA1 = Path(__file__).resolve().parent.parent / "worlds" / "Prueba1.txt"


def _problema() -> Problema:
    return Problema(World.desde_archivo(str(RUTA_PRUEBA1)))


def _por_accion(sucesores):
    return {accion: (nuevo, costo) for accion, nuevo, costo in sucesores}


# --- Estado inicial y meta -------------------------------------------------

def test_estado_inicial():
    p = _problema()
    s = p.estado_inicial()
    assert s.pos == (4, 0)
    assert s.fertilizante == 0
    assert s.combustible == -1
    assert s.cultivos_pendientes == frozenset({(4, 3), (5, 3), (6, 8)})


def test_es_meta():
    p = _problema()
    assert p.es_meta(Estado((0, 0), 0, -1, frozenset())) is True
    s = p.estado_inicial()
    assert p.es_meta(s) is False


def test_estados_hasheables_e_iguales():
    a = Estado((1, 1), 1, -1, frozenset({(2, 2)}))
    b = Estado((1, 1), 1, -1, frozenset({(2, 2)}))
    c = Estado((1, 1), 2, -1, frozenset({(2, 2)}))
    assert a == b
    assert hash(a) == hash(b)
    assert a != c
    assert len({a, b, c}) == 2


# --- Movimiento normal -----------------------------------------------------

def test_movimiento_normal_cuesta_1_y_no_cambia_combustible():
    p = _problema()
    s = p.estado_inicial()  # (4, 0), combustible -1
    por_accion = _por_accion(p.sucesores(s))
    # (4, 0): arriba -> (3, 0) libre; abajo -> (5, 0) libre;
    # izquierda sale de la cuadrícula; derecha -> (4, 1) libre.
    assert set(por_accion) == {"arriba", "abajo", "derecha"}
    nuevo, costo = por_accion["derecha"]
    assert costo == 1
    assert nuevo.pos == (4, 1)
    assert nuevo.combustible == -1
    assert nuevo.fertilizante == 0


def test_movimientos_hacia_muros_y_fuera_no_aparecen():
    p = _problema()
    # (1, 0): arriba -> (0, 0) muro; izquierda sale; solo abajo y derecha.
    s = Estado((1, 0), 0, -1, frozenset())
    por_accion = _por_accion(p.sucesores(s))
    assert set(por_accion) == {"abajo", "derecha"}


def test_orden_fijo_de_operadores():
    p = _problema()
    orden = ["arriba", "abajo", "izquierda", "derecha"]
    # El inicial (4, 0) tiene 3 vecinos libres y deben salir en orden.
    acciones = [a for a, _, _ in p.sucesores(p.estado_inicial())]
    assert acciones == ["arriba", "abajo", "derecha"]
    # En cualquier casilla, las acciones son una subsecuencia del orden fijo.
    for pos in [(1, 0), (1, 6), (7, 6), (3, 3), (9, 7)]:
        acciones = [a for a, _, _ in p.sucesores(Estado(pos, 0, -1, frozenset()))]
        assert acciones == [a for a in orden if a in acciones]
        assert len(acciones) >= 1


# --- Avioneta --------------------------------------------------------------

def test_pisar_avioneta_deja_combustible_30_y_cuesta_1():
    p = _problema()
    # (1, 6) es libre y está justo debajo de la avioneta (0, 6).
    s = Estado((1, 6), 0, -1, frozenset())
    por_accion = _por_accion(p.sucesores(s))
    nuevo, costo = por_accion["arriba"]
    assert nuevo.pos == (0, 6)
    assert costo == 1
    assert nuevo.combustible == 30


def test_movimiento_con_avioneta_cuesta_medio_y_resta_combustible():
    p = _problema()
    s = Estado((0, 6), 0, 30, frozenset())  # recién abordada
    por_accion = _por_accion(p.sucesores(s))
    # Desde (0, 6) el único vecino libre es abajo -> (1, 6).
    assert set(por_accion) == {"abajo"}
    nuevo, costo = por_accion["abajo"]
    assert costo == 0.5
    assert nuevo.combustible == 29


def test_tras_30_movimientos_el_siguiente_cuesta_1_y_combustible_0():
    p = _problema()
    # La fila 1 es un pasillo libre: caminar 30 pasos de ida y vuelta.
    s = Estado((1, 0), 0, 30, frozenset())
    for i in range(30):
        por_accion = _por_accion(p.sucesores(s))
        accion = "derecha" if s.pos[1] == 0 else "izquierda"
        s, costo = por_accion[accion]
        assert costo == 0.5
    assert s.combustible == 0
    # Con combustible agotado, el siguiente movimiento cuesta 1 y sigue en 0.
    por_accion = _por_accion(p.sucesores(s))
    accion = "derecha" if s.pos[1] == 0 else "izquierda"
    s2, costo = por_accion[accion]
    assert costo == 1
    assert s2.combustible == 0


def test_pasar_por_avioneta_agotada_no_hace_nada():
    p = _problema()
    s = Estado((1, 6), 0, 0, frozenset())  # combustible ya agotado
    nuevo, costo = _por_accion(p.sucesores(s))["arriba"]
    assert nuevo.pos == (0, 6)
    assert costo == 1
    assert nuevo.combustible == 0


# --- Depósito y cultivos ----------------------------------------------------

def test_pisar_deposito_recarga_a_2():
    p = _problema()
    # (1, 2) es libre y está justo debajo del depósito (0, 2).
    s = Estado((1, 2), 0, -1, frozenset())
    nuevo, costo = _por_accion(p.sucesores(s))["arriba"]
    assert nuevo.pos == (0, 2)
    assert costo == 1
    assert nuevo.fertilizante == 2


def test_pisar_cultivo_con_fertilizante_lo_trata():
    p = _problema()
    pendientes = frozenset({(4, 3), (5, 3)})
    s = Estado((4, 2), 1, -1, pendientes)
    nuevo, _ = _por_accion(p.sucesores(s))["derecha"]
    assert nuevo.pos == (4, 3)
    assert nuevo.cultivos_pendientes == frozenset({(5, 3)})
    assert nuevo.fertilizante == 0


def test_pisar_cultivo_sin_fertilizante_no_lo_trata():
    p = _problema()
    pendientes = frozenset({(4, 3), (5, 3)})
    s = Estado((4, 2), 0, -1, pendientes)
    nuevo, _ = _por_accion(p.sucesores(s))["derecha"]
    assert nuevo.pos == (4, 3)
    assert nuevo.cultivos_pendientes == pendientes
    assert nuevo.fertilizante == 0


def test_tratar_cultivo_en_avioneta():
    p = _problema()
    mundo = p.world
    # Estado sintético: el robot va en la avioneta y pisa un cultivo.
    # Se usa la posición del cultivo (5, 3) llegando desde (5, 2)... pero
    # (5, 2) es muro; se llega desde arriba: (4, 3) ya tratado.
    s = Estado((4, 3), 1, 10, frozenset({(5, 3)}))
    assert mundo.es_libre(5, 3)
    nuevo, costo = _por_accion(p.sucesores(s))["abajo"]
    assert nuevo.pos == (5, 3)
    assert costo == 0.5  # iba en la avioneta
    assert nuevo.combustible == 9
    assert nuevo.cultivos_pendientes == frozenset()
    assert nuevo.fertilizante == 0


# --- Nodo -------------------------------------------------------------------

def test_nodo_reconstruye_camino_y_estados():
    p = _problema()
    raiz = Nodo(p.estado_inicial())
    hijo = Nodo(
        Estado((4, 1), 0, -1, p.estado_inicial().cultivos_pendientes),
        padre=raiz,
        accion="derecha",
        g=1.0,
        profundidad=1,
    )
    assert raiz.reconstruir_camino() == []
    assert hijo.reconstruir_camino() == ["derecha"]
    estados = hijo.reconstruir_estados()
    assert estados == [raiz.estado, hijo.estado]


def test_nodo_comparable_en_heapq():
    s = Estado((0, 0), 0, -1, frozenset())
    n1 = Nodo(s, g=1.0)
    n2 = Nodo(s, g=2.0)
    n3 = Nodo(s, g=1.0)
    assert n1 < n2
    heap = [n2, n3, n1]
    heapq.heapify(heap)
    # Al desempatar por g y luego por orden de creación, n1 sale primero.
    assert heapq.heappop(heap) is n1
