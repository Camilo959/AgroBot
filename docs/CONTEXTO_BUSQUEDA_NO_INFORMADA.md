# Contexto: algoritmos de búsqueda no informada (AgroBot)

Documento de referencia para implementar `algorithms/base.py`, `bfs.py`, `ucs.py` y `dfs.py`.

Fuentes:
- `Tema4.pdf` (Oscar Bedoya, Inteligencia Artificial, Univalle). Las referencias `d.N` son números de diapositiva.
- Enunciado del Proyecto 1.

Las decisiones marcadas como **PENDIENTE DE CONFIRMAR** se consultarán con el profesor. Mientras tanto se aplican tal como están escritas aquí.

---

## 1. Qué cubre y qué no

- **Cubre:** Amplitud (BFS), Costo uniforme (UCS) y Profundidad evitando ciclos (DFS).
- **No cubre:** Avara, A*, heurísticas, UI, `main.py`.
- **El core no cambia.** `core/` (`World`, `Estado`, `Problema`, `Nodo`) ya está terminado y probado. Los algoritmos solo lo consumen.

## 2. Convenciones del profesor (obligatorias)

### 2.1 Qué significa "expandir" (d.40)

> Expandir = verificar si es meta + crear hijos.
> Al expandir un nodo meta no se crean sus hijos.

Consecuencias:

1. **El test de meta se hace al sacar el nodo** de la cola, cola de prioridad o pila. Nunca al generarlo.
2. **El nodo meta cuenta como nodo expandido**, aunque no genere hijos.
3. El nodo raíz también se expande. Si el estado inicial ya es meta (mundo sin cultivos secos), el resultado es: camino vacío, costo 0 y `nodos_expandidos = 1`.

### 2.2 Orden de operadores y de hijos (d.39, d.223, d.293)

- Orden fijo: **arriba, abajo, izquierda, derecha** (ya es `MOVIMIENTOS` en `core/problem.py`).
- Los hijos se consideran "de izquierda a derecha" en ese orden. El primer operador es el primero en expandirse.

### 2.3 Costo de ruta (d.10)

`g(n)` es la suma de los costos de las acciones a lo largo de la ruta. Aquí los costos son 1 o 0.5, así que las sumas son exactas en punto flotante y no hay errores de redondeo.

## 3. Los tres algoritmos

### 3.1 Amplitud (d.39, d.96)

- Estructura: **cola FIFO** (`collections.deque`). Los hijos se agregan al final.
- Es completo.
- **No es óptimo en costo** (d.119). Es óptimo en número de pasos, pero aquí los pasos cuestan 1 o 0.5.
- Por eso su `costo` puede ser mayor que el de UCS. Hay que reportarlo igual.

```
cola = [nodo_raiz]
mientras cola no vacía:
    n = sacar_del_frente(cola)
    [modo global] si clave(n.estado) en cerrados: continuar; si no, agregarla
    expandidos += 1
    si es_meta(n.estado): devolver solución
    para cada (accion, estado, costo) en sucesores(n.estado):
        [modo rama] si crea ciclo en la rama: continuar
        meter Nodo hijo al final de la cola
devolver sin solución
```

### 3.2 Costo uniforme (d.121, d.220)

- Estructura: **cola de prioridad** (`heapq`) con prioridad `g(n)`. Se expande el de menor `g`, sin importar la profundidad.
- Es completo y **óptimo** (d.219).
- El test de meta va **al extraer**. Si se hiciera al generar, se perdería la optimalidad.
- Desempate cuando hay igual `g`: orden de creación (FIFO). El profesor no lo especifica, así que se documenta como supuesto.
- Entradas del heap: `(g, contador_creacion, nodo)`. El contador único evita comparar nodos.

```
frontera = heap con (0, 0, nodo_raiz)
mientras frontera no vacía:
    g, _, n = heappop(frontera)
    [modo global] si estado completo de n en cerrados: continuar; si no, agregarlo
    expandidos += 1
    si es_meta(n.estado): devolver solución
    para cada hijo:
        [modo rama] si crea ciclo en la rama: continuar
        heappush(frontera, (hijo.g, contador, hijo))
devolver sin solución
```

Un estado repetido que se descarta al extraerlo en modo global **no** cuenta como expandido.

### 3.3 Profundidad evitando ciclos (d.223, d.253, d.281)

- Estructura: **pila** (lista con `append` y `pop`).
- Definición del profesor (d.281): *"se evita que sobre una misma rama se alcance un estado previo"*. Es decir, **se revisan solo los ancestros del camino actual**.
- d.282: *"evitar ciclo es un concepto más completo que evitar devolverse"*. No basta con comparar con el padre. Hay que revisar toda la rama.
- **Los hijos se apilan en orden inverso**, para que el primer operador (arriba) quede arriba de la pila y sea el primero en salir (d.254).
- No es óptimo y puede devolver soluciones largas. Eso es esperado.
- Con la detección de ciclos por rama, cada rama es finita, porque el espacio de estados es finito. Por eso el algoritmo es completo.
- Implementarlo **iterativo** (no recursivo), para no chocar con el límite de recursión de Python.

```
pila = [nodo_raiz]
mientras pila no vacía:
    n = pila.pop()
    [modo global] si clave(n.estado) en cerrados: continuar; si no, agregarla
    expandidos += 1
    si es_meta(n.estado): devolver solución
    hijos = []
    para cada (accion, estado, costo) en sucesores(n.estado):
        [modo rama] si crea ciclo en la rama: continuar
        hijos.append(Nodo hijo)
    pila.extend(reversed(hijos))
devolver sin solución
```

## 4. Manejo de ciclos

### 4.1 Lo que pide el enunciado

"En todos los algoritmos evite ciclos. Sin embargo, cuando el agente llegue a la casilla de la avioneta, o a un cultivo seco con fertilizante, o al depósito, debe dejar que se devuelva."

Lo que el enunciado permite es volver a una casilla **cuando algo cambió**: se subió a la avioneta, recargó fertilizante o trató un cultivo. Cualquier otro regreso es un ciclo.

### 4.2 Problema detectado: la oscilación en la avioneta

Si se usa el `Estado` completo como clave de ciclo, el campo `combustible` baja en cada movimiento mientras el robot va en la avioneta. Entonces `A → B → A` en vuelo produce un estado **distinto** (menos combustible), y no se detectaría como ciclo.

Resultado:
- Se permitirían hasta 30 pasos de vaivén sin sentido.
- Eso multiplica nodos y tiempo, y viola "evite ciclos".

### 4.3 Solución: dos claves de ciclo (en `algorithms/base.py`)

**Clave completa:** el `Estado` tal cual.

**Clave relajada:** `(pos, fertilizante, cultivos_pendientes, fase_avioneta)`, donde la fase sale de `combustible`:

| `combustible` | `fase_avioneta` |
|---|---|
| `-1` | `"sin_abordar"` |
| `1..30` | `"en_vuelo"` |
| `0` | `"agotada"` |

Por qué la clave relajada es segura: dentro de una misma fase, el combustible nunca sube. Un nodo descendiente con la misma clave relajada que un ancestro es igual o peor que ese ancestro, tanto en costo como en lo alcanzable. Descartarlo no pierde soluciones ni la optimalidad.

La clave relajada sigue permitiendo los regresos legítimos del enunciado, porque abordar la avioneta, recargar y tratar un cultivo cambian la fase, el fertilizante o los cultivos pendientes.

### 4.4 Parámetro `modo_ciclos`

| Algoritmo | Valor por defecto | Clave usada |
|---|---|---|
| BFS | `"global"` | relajada |
| UCS | `"global"` | **completa** |
| DFS | `"rama"` | relajada |

- **`"rama"`:** se revisan los ancestros del nodo (incluido el padre), tal como lo define el profesor.
- **`"global"`:** conjunto de estados ya expandidos (cerrados). Se marca el estado **al extraerlo**.
- En UCS con `"global"` hay que usar la clave **completa**. Con la relajada se podría cerrar un estado con menos combustible pero menor `g` antes de ver uno con más combustible y mayor `g`, y perder la optimalidad.
- En UCS con `"rama"` sí se puede usar la relajada (argumento de dominancia de 4.3).
- Para BFS y DFS la clave relajada es segura en modo global, porque el combustible solo afecta el costo y no lo alcanzable.
- Un valor de `modo_ciclos` inválido lanza `ValueError`.

**Por qué BFS y UCS usan `"global"` por defecto (PENDIENTE DE CONFIRMAR):** en clase los ciclos se evitan por rama. Mi estimación, sin haberla medido, es que BFS y UCS por rama pueden crecer de forma exponencial con la profundidad, y `Prueba1` probablemente necesita una solución de alrededor de 30 movimientos. Por eso el modo `"global"` es el práctico. El modo `"rama"` queda disponible para comparar y documentar en el informe.

### 4.5 Límite de seguridad

Cada algoritmo acepta `limite_nodos: int | None = None`. Si se alcanza, la búsqueda se detiene y devuelve `exito = False` con `limite_alcanzado = True`. Sirve para probar el modo `"rama"` sin que la terminal se quede colgada.

## 5. Interfaz de los algoritmos

```python
busqueda_amplitud(problema, modo_ciclos="global", limite_nodos=None) -> Resultado
busqueda_costo_uniforme(problema, modo_ciclos="global", limite_nodos=None) -> Resultado
busqueda_profundidad(problema, modo_ciclos="rama", limite_nodos=None) -> Resultado
```

### `Resultado` (en `algorithms/base.py`)

| Campo | Significado |
|---|---|
| `exito: bool` | Si se encontró solución |
| `camino: list[str]` | Acciones desde el estado inicial (vacío si no hay solución) |
| `estados: list[Estado]` | Estados recorridos, incluido el inicial (para la animación) |
| `nodos_expandidos: int` | Nodos extraídos y expandidos, **incluido el nodo meta** |
| `nodos_generados: int` | Nodos `Nodo` creados, incluida la raíz. Los hijos descartados por ciclo no se crean |
| `profundidad: int` | Profundidad del nodo solución |
| `profundidad_maxima: int` | Mayor profundidad entre todos los nodos creados |
| `tiempo: float` | Segundos, con `time.perf_counter`, medido solo alrededor de la búsqueda |
| `costo: float \| None` | Costo `g` de la solución. Se calcula siempre. `None` solo si no hay solución |
| `limite_alcanzado: bool` | Si se cortó por `limite_nodos` |

**Qué mostrar como "profundidad del árbol" en la UI es PENDIENTE DE CONFIRMAR.** Por ahora se guardan ambas (`profundidad` y `profundidad_maxima`).

Helpers en `base.py`:
- `clave_completa(estado)` y `clave_relajada(estado)`.
- `crea_ciclo_en_rama(nodo_padre, estado_hijo, clave)`: recorre `nodo.padre` hacia arriba, incluyendo el padre, comparando claves.
- Un helper para medir el tiempo y construir el `Resultado` (con éxito y sin él).

## 6. Cambios respecto a lo que se había dicho antes

| Tema | Antes | Ahora |
|---|---|---|
| Nodo expandido | El que genera sucesores | El que se extrae y se verifica, **incluye el nodo meta** |
| DFS evitando ciclos | `visitados` global | Revisión de ancestros (por rama) |
| Clave de ciclo | `Estado` completo siempre | Relajada (sin combustible exacto) salvo UCS global |
| `Resultado` | Sin `exito`, `nodos_generados`, `profundidad_maxima` | Se agregan |

## 7. Pruebas esperadas (`tests/test_algorithms.py`)

Los mundos de prueba se arman escribiendo una matriz 10x10 a un archivo temporal (`tmp_path`) y cargándola con `World.desde_archivo`.

1. **Sin cultivos:** meta en la raíz. Camino vacío, `costo == 0`, `nodos_expandidos == 1`.
2. **Un cultivo cerca del depósito:** los tres algoritmos devuelven solución válida.
3. **Validez de la solución:** reproducir `camino` paso a paso con `Problema.sucesores` desde el estado inicial. El estado final debe cumplir `es_meta`, y la suma de costos debe ser igual a `Resultado.costo`.
4. **Optimalidad:** en un mundo con varias rutas, `costo(UCS) <= costo(BFS)` y `costo(UCS) <= costo(DFS)`.
5. **BFS no es óptimo en costo:** construir, si es posible, un mundo donde un desvío para abordar la avioneta abarate el recorrido, de modo que `costo(BFS) > costo(UCS)`. Si no se logra, documentarlo en la prueba.
6. **Sin solución:** cultivo encerrado por muros, o depósito inalcanzable. Devuelve `exito == False`, camino vacío, `costo is None`, sin lanzar excepción.
7. **Sin oscilación:** en ninguna solución aparece `pos[i] == pos[i+2]` salvo que entre `i` y `i+2` haya cambiado el fertilizante, los cultivos pendientes o la fase de la avioneta.
8. **Meta al extraer:** el nodo meta cuenta como expandido, y `nodos_expandidos >= len(camino) + 1` en BFS.
9. **DFS apila en orden inverso:** en un mundo abierto, la primera expansión de DFS sigue "arriba" cuando es posible.
10. **`modo_ciclos` inválido** lanza `ValueError`.
11. **`limite_nodos`** corta la búsqueda con `exito == False` y `limite_alcanzado == True`.
12. **UCS con `"global"` y con `"rama"`** dan el mismo costo en mundos pequeños.

## 8. Verificación sobre `Prueba1.txt`

Un script de consola (`scripts/comparar_no_informada.py`) debe correr BFS, UCS y DFS sobre `worlds/Prueba1.txt` y mostrar una tabla con:

`algoritmo | modo_ciclos | exito | nodos_expandidos | nodos_generados | profundidad | profundidad_maxima | tiempo | costo`

Los modos `"rama"` de BFS y UCS se corren con un `limite_nodos` alto (por ejemplo 2 000 000), para dejar documentado si son viables.

## 9. Supuestos que hay que mencionar en el informe

1. Test de meta al extraer. El nodo meta cuenta como expandido.
2. Desempate en UCS por orden de creación.
3. `modo_ciclos` por defecto: BFS y UCS en `"global"`, DFS en `"rama"`.
4. Clave de ciclo relajada para evitar la oscilación en la avioneta.
5. Qué se reporta como "profundidad del árbol".
6. Los supuestos 1 a 6 del core (costo al llegar a la avioneta, sin bajada voluntaria, codificación de `combustible`, etc.), ya documentados en el README.
