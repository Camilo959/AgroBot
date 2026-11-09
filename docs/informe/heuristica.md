# Borrador: heurística B, Avara y A* (AgroBot)

> **Borrador para revisión del equipo.** Las cifras de la tabla se tomaron
> de la salida real de `scripts/comparar_algoritmos.py` sobre
> `worlds/Prueba1.txt`.

## 1. Idea de la heurística

La heurística estima el costo mínimo que falta para terminar la misión
desde un estado. Se construye relajando el problema:

- Se ignoran los muros y se usan distancias Manhattan.
- Se ignoran los detalles del combustible.
- Se supone que cada movimiento puede costar 0.5 (el menor costo posible,
  cuando el robot va en la avioneta).

Con esas relajaciones se obtiene una cota inferior del costo real, es
decir, una heurística **admisible**. El ejemplo del profesor propone
“Manhattan / 2”; aquí se adapta a varios cultivos y al depósito usando un
árbol de expansión mínima (MST).

## 2. Definición

Sea:

- `P`: conjunto de cultivos pendientes.
- `f`: fertilizante actual.
- `D`: posición del depósito.
- `pos`: posición del robot.
- `MST(S)`: costo del árbol de expansión mínima sobre los puntos `S` con
  distancia Manhattan.

Movimientos mínimos estimados `L`:

| Caso | `L` |
|---|---|
| `P` vacío | 0 |
| `f = 0` | `d(pos, D) + MST({D} ∪ P)` |
| `0 < f < |P|` | `MST({pos} ∪ P ∪ {D})` |
| `f ≥ |P|` | `MST({pos} ∪ P)` |

Finalmente:

```text
h(estado) = 0.5 · L
```

La heurística no depende del combustible exacto: solo de `pos`,
`fertilizante` y `cultivos_pendientes`.

### Ejemplo con el estado inicial de `Prueba1`

Robot `(4,0)`, depósito `D=(0,2)`, cultivos `A=(4,3)`, `B=(5,3)`,
`C=(6,8)`, `f=0`.

- `d(robot, D) = 6`.
- Distancias Manhattan: `D-A=5`, `D-B=6`, `D-C=12`, `A-B=1`, `A-C=7`,
  `B-C=6`.
- `MST({D,A,B,C}) = 1 + 5 + 6 = 12`.
- `L = 6 + 12 = 18`, por lo que `h = 9.0`.

El costo óptimo real desde ese estado es 25.0, así que se cumple
`h ≤ h*`.

## 3. Admisibilidad

### Demostración corta

1. Toda solución es una caminata por la cuadrícula que visita todos los
   cultivos pendientes y, cuando hace falta, el depósito.
2. Una caminata que visita un conjunto de puntos mide al menos la suma de
   las distancias entre puntos consecutivos. Esa secuencia contiene un
   árbol de expansión de los puntos, por lo que su longitud es mayor o
   igual que el MST. Manhattan ignora los muros, que solo alargan los
   caminos; por eso `L` nunca supera la longitud real.
3. Cada movimiento cuesta al menos 0.5, así que el costo real es mayor o
   igual que `0.5 · L`.
4. `h(meta) = 0` porque no quedan cultivos pendientes.

La búsqueda usa árbol (ciclos solo por rama), así que la admisibilidad es
suficiente para la optimalidad de A*; no se necesita consistencia.

### Verificación exhaustiva en `Prueba1`

Se enumeraron todos los estados alcanzables usando el `Estado` completo,
se calculó `h*` con Dijkstra inverso multifuente desde los estados meta y
se comprobó `h(s) ≤ h*(s) + 1e-9`.

- Estados alcanzables: **12 302**.
- Costo óptimo desde el estado inicial: **25.0**.
- Violaciones de admisibilidad: **0**.

La prueba se repite en dos mundos pequeños: uno que obliga a recargar
fertilizante y otro donde conviene usar la avioneta. En ambos hay 0
violaciones.

## 4. Comparación sobre `Prueba1.txt`

Salida real de `scripts/comparar_algoritmos.py`:

| Algoritmo | Expandidos | Generados | Profundidad | Prof. máx. | Costo |
|---|---:|---:|---:|---:|---:|
| BFS | 5251 | 6423 | 30 | 31 | 30.0 |
| UCS | 9561 | 12335 | 38 | 40 | 25.0 |
| DFS | 81 | 105 | 68 | 76 | 58.0 |
| Avara | 39 | 60 | 32 | 32 | 32.0 |
| A* | 770 | 1036 | 40 | 40 | 25.0 |

Lectura:

- **A*** encuentra el mismo costo óptimo que UCS (25.0) con muchas menos
  expansiones. Su camino puede diferir del de UCS, pero el costo es el
  mismo.
- **Avara** es la más rápida en expansiones, pero no es óptima: su costo
  es 32.0.
- **UCS** es óptimo pero expande muchos más nodos.
- **BFS y DFS** no son óptimos en costo.

## 5. Mejoras posibles (no implementadas)

- Usar distancias reales con BFS en vez de Manhattan: más informativa y
  sigue siendo admisible, pero requiere más cálculo.
- Incorporar el combustible de la avioneta en la estimación.
- Ambas mejoras dominarían a la heurística B y mantendrían la
  admisibilidad, a cambio de una demostración más larga.

Se descartaron sumar distancias a todos los cultivos (no es admisible) y
usar solo el cultivo más lejano (admisible pero mucho más débil).

## 6. Supuestos y limitaciones

- Heurística B, la misma para Avara y A*.
- Desempate por orden de creación y ciclos solo por rama (confirmados por
  el profesor).
- Test de meta al extraer; el nodo meta cuenta como expandido.
- Clave de ciclo relajada: ignora el combustible exacto para que el
  vaivén dentro de la avioneta cuente como ciclo.
- Sin detección anticipada de mundos sin solución. En mundos abiertos la
  búsqueda por rama puede crecer y alcanzar `limite_nodos`; en ese caso la
  UI muestra “límite alcanzado”.
- Supuestos del core: llegar a la avioneta cuesta 1, no hay bajada
  voluntaria y el tratamiento de cultivos es automático.
