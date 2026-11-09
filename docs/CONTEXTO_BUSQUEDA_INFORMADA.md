# Contexto: búsqueda informada (Avara y A*) y heurística (AgroBot)

Documento de referencia para implementar `algorithms/heuristics.py`, `greedy.py` y `astar.py`, habilitarlos en la UI y redactar el borrador del informe.

Fuentes:
- `Tema5.pdf` (Oscar Bedoya, Inteligencia Artificial, Univalle). Las referencias `d.N` son números de diapositiva.
- Enunciado del Proyecto 1.
- `docs/CONTEXTO_BUSQUEDA_NO_INFORMADA.md`: **todo lo que allí se definió sigue vigente** (ciclos por rama con clave relajada, meta al extraer, meta cuenta como expandido, `limite_nodos`, orden de operadores, estructura de `Resultado`).

---

## 1. Alcance

- **Cubre:** heurística, Avara y A*, su integración en la UI, pruebas y un borrador del informe (heurística y admisibilidad).
- **No cambia:** `core/` ni los tres algoritmos no informados. Si encuentras un bug en ellos, avisa antes de tocarlos.

## 2. Convenciones

### 2.1 Del Tema5

| Tema | Convención | Dónde |
|---|---|---|
| Heurística | `h(n)`: costo **estimado** de llegar a la meta desde `n` | d.8 |
| Avara | Expande el nodo con menor `h(n)`, sin importar la profundidad. Cola de prioridad con prioridad `h`. No es óptima ni completa en general | d.44, d.91, d.92 |
| A* | Expande el nodo con menor `f(n) = g(n) + h(n)`. Cola de prioridad con prioridad `f`. Es completa y óptima si `h` es admisible | d.108, d.150, d.151 |
| Admisible | `h(n) ≤ costo_real(n)`; nunca sobreestima | d.152 |
| Diseño | Se divide entre el mejor avance posible en un solo paso. Ejemplo con nave: Manhattan / 2 "para que sea admisible" | d.187, d.196 |
| Test de meta | No está dicho explícitamente. En el árbol de A* (d.148), un nodo meta con `f=310` se genera pero se expande antes otro con `f=275`; se sale por la meta con `f=278`. O sea, se verifica **al extraer** | d.148 |

### 2.2 Confirmado por el profesor

1. **Desempate en Avara y A\*: por orden de creación**, igual que en Costo uniforme (contador propio por búsqueda, `itertools.count()`).
2. **Ciclos en Avara y A\*: solo por rama**, igual que en los otros tres algoritmos (clave relajada, revisando los ancestros incluido el padre).
3. Ya confirmado antes y vigente: el nodo meta cuenta como expandido, la profundidad que se reporta es `profundidad_maxima`, los mundos son 10x10 parecidos a `Prueba1`, y el corte por `limite_nodos` con mensaje de "límite alcanzado" es aceptable.

### 2.3 Decisiones del equipo

1. **Heurística B** (sección 4): Manhattan, sin dependencia del combustible. Se eligió por sencillez y porque basta para los alcances del curso. Sigue el estilo del ejemplo del profesor (d.187: Manhattan / 2).
2. **Avara y A\* usan la misma heurística.**
3. El test de meta al extraer y el conteo del nodo meta se aplican igual que en los no informados (el Tema5 no lo contradice).
4. **No hay detección anticipada de mundos sin solución** (sección 3.3).

## 3. Algoritmos

### 3.1 Interfaz

```python
busqueda_avara(problema, heuristica, limite_nodos=None) -> Resultado
busqueda_a_estrella(problema, heuristica, limite_nodos=None) -> Resultado
```

- `heuristica` es un callable `h(estado) -> float` (sección 4).
- El `Resultado` es el mismo de los no informados. El costo `g` de la solución se calcula siempre; la UI lo muestra solo en Costo uniforme y A*.
- Copia la estructura de `algorithms/ucs.py` (contador, revisión de `limite_nodos` antes de extraer, constructores de éxito y fracaso).

### 3.2 Pseudocódigo

Avara (prioridad `h`) y A* (prioridad `g + h`) son idénticos salvo la prioridad.

```
frontera = heap con (prioridad(raiz), 0, nodo_raiz)
mientras frontera no vacía:
    _, _, n = heappop(frontera)
    si limite_nodos y expandidos >= limite_nodos: devolver fracaso (limite_alcanzado=True)
    expandidos += 1
    si es_meta(n.estado): devolver solución
    para cada (accion, estado, costo) en sucesores(n.estado):
        si crea_ciclo_en_rama(n, estado): continuar
        hijo = Nodo(estado, n, accion, g = n.g + costo)
        prioridad = h(estado)          (Avara)   |   hijo.g + h(estado)   (A*)
        heappush(frontera, (prioridad, contador, hijo))
devolver sin solución
```

- La prioridad del heap es `(prioridad, contador_creacion, nodo)`. El contador único evita comparar nodos y da el desempate por creación.
- Las sumas son de múltiplos de 0.5, así que son exactas en punto flotante.

### 3.3 Mundos sin solución (limitación conocida)

Con Manhattan, `h` nunca es infinita: no detecta que un cultivo está encerrado por muros. En un mundo sin solución, la búsqueda por rama agota el árbol. En laberintos de pasillos como `Prueba1` eso es corto, pero en zonas abiertas puede crecer exponencialmente (se observó con DFS). En ese caso actúa `limite_nodos` y la UI muestra "límite alcanzado". Los mundos de prueba del profesor son parecidos a `Prueba1` y se espera que tengan solución, así que no se añade ninguna detección extra. Se documenta como limitación en el informe.

### 3.4 Propiedades que se esperan (y se prueban)

- **A\* con `h ≡ 0` equivale a Costo uniforme:** mismo camino, mismo costo y mismos nodos expandidos.
- **Avara con `h ≡ 0` equivale a Amplitud:** todo empata y manda el orden de creación (cola FIFO).
- A* con heurística admisible da el costo óptimo (el mismo que UCS).
- Avara no garantiza el costo óptimo y puede alejarse mucho con una heurística pobre.

## 4. Heurística B

Se implementa como clase en `algorithms/heuristics.py`:

```python
class HeuristicaAgroBot:
    def __init__(self, world): ...      # guarda la posición del depósito
    def __call__(self, estado) -> float: ...
```

- Usa distancia Manhattan: `d(a, b) = |fa − fb| + |ca − cb|`. No necesita precálculos.
- **No depende del combustible**: solo de `pos`, `fertilizante` y `cultivos_pendientes`.
- Debe construirse **dentro del proceso de búsqueda** (la UI ya ejecuta la búsqueda en un proceso hijo).

### 4.1 Definición

Sea `P` el conjunto de cultivos pendientes, `f` el fertilizante, `D` el depósito, `pos` la posición del robot y `MST(S)` el costo del árbol de expansión mínima sobre el conjunto de puntos `S` con la distancia Manhattan.

**Movimientos mínimos `L`**

| Caso | `L` |
|---|---|
| `P` vacío | 0 |
| `f = 0` | `d(pos, D) + MST({D} ∪ P)` |
| `0 < f < |P|` | `MST({pos} ∪ P ∪ {D})` |
| `f ≥ |P|` | `MST({pos} ∪ P)` |

**Heurística:** `h(estado) = 0.5 · L`

El 0.5 es el menor costo posible de un movimiento (la avioneta lo reduce a la mitad). Es la misma idea del ejemplo de la nave del profesor: "Manhattan / 2 para que sea admisible" (d.187), ampliada a varios cultivos y al depósito.

Para `MST` basta Prim sobre pocos puntos (O(k²)).

### 4.2 Ejemplo a mano (estado inicial de `Prueba1`)

Robot (4,0), depósito (0,2), cultivos A=(4,3), B=(5,3), C=(6,8), `f = 0`.

- `d(robot, D) = |4−0| + |0−2| = 6`.
- Distancias Manhattan entre D, A, B, C: D-A = 5, D-B = 6, D-C = 12, A-B = 1, A-C = 7, B-C = 6.
- `MST({D, A, B, C}) = 1 (A-B) + 5 (D-A) + 6 (B-C) = 12`.
- `L = 6 + 12 = 18`, y **`h = 9.0`**.
- El costo óptimo real desde ese estado es 25.0, así que se cumple `h ≤ h*`.

Más casos para las pruebas (todos con combustible `-1`, salvo indicación):

| Estado | Caso | `L` | `h` |
|---|---|---|---|
| pos (0,2), `f = 2`, `P = {A, B, C}` | `f < |P|` | 12 | 6.0 |
| pos (5,3), `f = 1`, `P = {A, C}` | `f < |P|` | 12 | 6.0 |
| pos (5,3), `f = 2`, `P = {C}` | `f ≥ |P|` | 6 | 3.0 |
| inicial, con combustible 0, 7 o 30 | `f = 0` | 18 | 9.0 (igual: no depende del combustible) |

### 4.3 Justificación de admisibilidad (para el informe)

1. **Toda solución es una caminata por la cuadrícula** que pasa por todos los cultivos pendientes, y por el depósito cuando hace falta: antes de tratar el primer cultivo si `f = 0`, o al menos una vez si `f < |P|` (cada recarga da como máximo 2 unidades).
2. **Longitud mínima.** Una caminata que visita un conjunto de puntos mide al menos la suma de las distancias entre puntos consecutivos, y esa secuencia es un árbol de expansión de esos puntos; por tanto es mayor o igual que el `MST`. Cuando `f = 0` se separa el tramo hasta el depósito (≥ `d(pos, D)`) del tramo posterior, que debe visitar todos los cultivos. Manhattan ignora los muros, que solo alargan los caminos, así que nunca supera la longitud real. Por eso `L` es una cota inferior del número de movimientos.
3. **Costo.** Cada movimiento cuesta al menos 0.5 (1 normal, 0.5 en avioneta), así que el costo real es mayor o igual que `0.5 · L`.
4. **`h(meta) = 0`**, porque no quedan cultivos pendientes.

Como la búsqueda evita ciclos por rama (árbol de búsqueda), basta con admisibilidad: la consistencia no es necesaria para la optimalidad de A*.

### 4.4 Por qué B y qué queda como mejora posible

- B es sencilla, tiene prueba corta y reduce mucho la búsqueda (A* expande unas 12 veces menos nodos que UCS en `Prueba1`).
- **Mejoras posibles, no implementadas** (para mencionar en el informe sin cifras): usar distancias reales con BFS en vez de Manhattan, o tener en cuenta el combustible de la avioneta. Ambas dominan a B (d.229) y mantienen la admisibilidad, a cambio de una prueba más larga.
- **Se descartaron:** sumar distancias a todos los cultivos (no es admisible, sobrecuenta si están alineados) y usar solo el cultivo más lejano (admisible pero mucho más débil; Avara con esa heurística llegó a expandir cientos de miles de nodos en la réplica de análisis).

## 5. Resultados esperados sobre `Prueba1.txt`

Salen de una réplica independiente del problema que reproduce **exactamente** los números de UCS ya validados (9561 expandidos, 12335 generados, costo 25.0). Deberían coincidir con la implementación. Si no coinciden, no asumas cuál está mal: investiga y repórtalo.

| Algoritmo | Expandidos | Generados | Profundidad | Profundidad máx. | Costo |
|---|---|---|---|---|---|
| BFS | 5251 | 6423 | 30 | 31 | 30.0 |
| UCS | 9561 | 12335 | 38 | 40 | 25.0 |
| DFS | 81 | 105 | 68 | 76 | 58.0 |
| **A\*** | **770** | **1036** | **40** | **40** | **25.0** |
| **Avara** | **39** | **60** | **32** | **32** | **32.0** |

Notas:
- A* encuentra el mismo costo óptimo que UCS (25.0) con unas 12 veces menos expansiones. Su camino puede ser distinto (40 pasos contra 38) y es válido: el costo es el mismo.
- Avara es rápida pero no óptima (32.0 contra 25.0), como dice el Tema5 (d.92).

**Verificación exhaustiva de admisibilidad en `Prueba1`:** hay **12 302 estados alcanzables** (usando el `Estado` completo, no la clave relajada), todos con solución. El costo óptimo desde el estado inicial es 25.0 y la heurística B tiene **0 violaciones** de `h ≤ h*`.

## 6. Pruebas esperadas

### `tests/test_heuristics.py`

1. `h(meta) = 0`, y `h = 0` con `P` vacío sin importar el resto del estado.
2. Estado inicial de `Prueba1`: `L = 18` y `h = 9.0`. El mismo estado con combustible 0, 7 o 30 da el mismo `h` (no depende del combustible).
3. Los otros casos de la tabla de la sección 4.2 (cada fila de la tabla de `L`: fertilizante 0, insuficiente y suficiente).
4. **Admisibilidad exhaustiva** en `Prueba1`: enumerar los estados alcanzables con `Problema.sucesores` desde `estado_inicial`, calcular `h*` con Dijkstra inverso multifuente desde los estados meta, y verificar `h(s) ≤ h*(s) + 1e-9` en todos. Comprobar de paso que hay 12 302 estados y `h*(inicial) = 25.0`. Repetir la verificación en al menos 2 mundos pequeños propios (uno con fertilizante insuficiente que obligue a recargar y otro donde convenga la avioneta).

### `tests/test_algorithms.py` (casos nuevos, sin tocar los existentes)

5. A* da el mismo costo que UCS en `Prueba1` (25.0) y en los mundos pequeños de las pruebas existentes (el anillo de pasillos), con `nodos_expandidos(A*) ≤ nodos_expandidos(UCS)`.
6. **A\* con `h ≡ 0` equivale a UCS** (mismo camino, costo y expandidos) y **Avara con `h ≡ 0` equivale a BFS**.
7. Avara devuelve una solución válida (reproducida paso a paso con `sucesores` termina en meta) con `costo ≥` el óptimo.
8. Mundo sin solución tratable (por ejemplo, robot encerrado entre muros, o un mundo de pasillos pequeño donde la exploración por rama es corta): `exito == False`, camino vacío, `costo is None`, sin excepción. Si no logras un caso tratable con cultivo encerrado, verifica que `limite_nodos` corta con `limite_alcanzado == True`.
9. `limite_nodos` corta con `exito == False` y `limite_alcanzado == True`.
10. Sin cultivos: meta en la raíz, camino vacío, `costo == 0`, `nodos_expandidos == 1`.
11. Prueba de regresión sobre `Prueba1` con las cifras de la sección 5 (A* 770/1036/40/40/25.0; Avara 39/60/32/32/32.0).

Toda llamada a un algoritmo en las pruebas lleva un `limite_nodos` razonable (por ejemplo 200 000) para que ninguna prueba pueda colgarse.

## 7. Integración en la UI

- Habilitar "Avara" y "A*" en el selector "Informada" (quitar la leyenda "próximamente"). No cambies el diseño visual.
- `ui/runner.py`: el proceso hijo construye `Problema`, `HeuristicaAgroBot(world)` y llama a la función correspondiente, con `limite_nodos` como hoy. No pases la heurística entre procesos.
- Reporte (`construir_reporte`): **costo solo para Costo uniforme y A\***; Avara no lo muestra. Los demás campos (expandidos, profundidad = `profundidad_maxima`, tiempo) igual que siempre.
- Actualiza `ui/textos.py`, `ui/README_UI.md` y las pruebas de lógica de la UI (reporte de Avara sin costo y de A* con costo).

## 8. Borrador del informe (`docs/informe/heuristica.md`)

El enunciado exige: explicación de la heurística y justificación de su admisibilidad. Genera un **borrador** (a revisar por el equipo) con:

1. Descripción del problema relajado y de la idea (qué estima `h` y por qué: costo mínimo por movimiento 0.5 y longitud mínima del recorrido).
2. La definición de la sección 4.1, con el ejemplo numérico de la 4.2.
3. La justificación de admisibilidad de la 4.3, redactada como demostración corta, más la verificación exhaustiva (12 302 estados, 0 violaciones).
4. Tabla comparativa de los cinco algoritmos sobre `Prueba1`, **tomada de la salida real de `scripts/comparar_algoritmos.py`** (no copiada de este documento), con una lectura breve: A* óptimo y pocas expansiones, Avara rápida pero no óptima, UCS óptimo pero con muchas expansiones, BFS y DFS no óptimos en costo.
5. Mejoras posibles (4.4), solo de forma cualitativa y sin cifras.
6. Supuestos del equipo y limitaciones: ciclos por rama, clave relajada, test de meta al extraer, sin detección de mundos sin solución (3.3) y que `limite_nodos` puede cortar la búsqueda en mundos muy abiertos.

## 9. Supuestos que mencionar en el informe

1. Heurística B; la misma para Avara y A*.
2. Desempate por orden de creación y ciclos por rama (confirmados por el profesor).
3. Test de meta al extraer; el nodo meta cuenta como expandido.
4. Clave de ciclo relajada (ignora el combustible exacto, para que el vaivén dentro de la avioneta cuente como ciclo).
5. Sin detección anticipada de mundos sin solución.
6. Los supuestos del core: llegar a la avioneta cuesta 1, no hay bajada voluntaria, tratamiento automático.
