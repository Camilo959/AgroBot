# Contexto: algoritmos de búsqueda no informada (AgroBot)

Documento de referencia para implementar `algoritmos/base.py`, `busqueda_no_informada/amplitud.py`, `costo_uniforme.py` y `profundidad.py`.

Fuentes:
- `Tema4.pdf` (Oscar Bedoya, Inteligencia Artificial, Univalle). Las referencias `d.N` son números de diapositiva.
- Enunciado del Proyecto 1.

Las decisiones **confirmadas por el profesor** se indican como tal. Los supuestos que aún son del equipo se listan en la sección 9.

---

## 1. Qué cubre y qué no

- **Cubre:** Amplitud (BFS), Costo uniforme (UCS) y Profundidad evitando ciclos (DFS).
- **No cubre:** Avara, A*, heurísticas, UI, `main.py`. La etapa informada se documenta en `docs/CONTEXTO_BUSQUEDA_INFORMADA.md`.
- **El core no cambia.** `core/` (`World`, `Estado`, `Problema`, `Nodo`) ya está terminado y probado. Los algoritmos solo lo consumen.

## 2. Convenciones del profesor (obligatorias)

### 2.1 Qué significa "expandir" (d.40)

> Expandir = verificar si es meta + crear hijos.
> Al expandir un nodo meta no se crean sus hijos.

**Confirmado por el profesor.**

Consecuencias:

1. **El test de meta se hace al sacar el nodo** de la cola, cola de prioridad o pila. Nunca al generarlo.
2. **El nodo meta cuenta como nodo expandido**, aunque no genere hijos.
3. El nodo raíz también se expande. Si el estado inicial ya es meta (mundo sin cultivos secos), el resultado es: camino vacío, costo 0 y `nodos_expandidos = 1`.

### 2.2 Orden de operadores y de hijos (d.39, d.223, d.293)

- Orden fijo: **arriba, abajo, izquierda, derecha** (ya es `MOVIMIENTOS` en `core/problema.py`). **Confirmado por el profesor.**
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
    expandidos += 1
    si es_meta(n.estado): devolver solución
    para cada (accion, estado, costo) en sucesores(n.estado):
        si crea ciclo en la rama: continuar
        meter Nodo hijo al final de la cola
devolver sin solución
```

### 3.2 Costo uniforme (d.121, d.220)

- Estructura: **cola de prioridad** (`heapq`) con prioridad `g(n)`. Se expande el de menor `g`, sin importar la profundidad.
- Es completo y **óptimo** (d.219).
- El test de meta va **al extraer**. Si se hiciera al generar, se perdería la optimalidad.
- Desempate cuando hay igual `g`: orden de creación (FIFO). **Confirmado por el profesor.**
- Entradas del heap: `(g, contador_creacion, nodo)`. El contador único evita comparar nodos.

```
frontera = heap con (0, 0, nodo_raiz)
mientras frontera no vacía:
    g, _, n = heappop(frontera)
    expandidos += 1
    si es_meta(n.estado): devolver solución
    para cada hijo:
        si crea ciclo en la rama: continuar
        heappush(frontera, (hijo.g, contador, hijo))
devolver sin solución
```

### 3.3 Profundidad evitando ciclos (d.223, d.253, d.281)

- Estructura: **pila** (lista con `append` y `pop`).
- Definición del profesor (d.281): *"se evita que sobre una misma rama se alcance un estado previo"*. Es decir, **se revisan solo los ancestros del camino actual**. **Confirmado por el profesor.**
- d.282: *"evitar ciclo es un concepto más completo que evitar devolverse"*. No basta con comparar con el padre. Hay que revisar toda la rama.
- **Los hijos se apilan en orden inverso**, para que el primer operador (arriba) quede arriba de la pila y sea el primero en salir (d.254).
- No es óptimo y puede devolver soluciones largas. Eso es esperado.
- Con la detección de ciclos por rama, cada rama es finita, porque el espacio de estados es finito. Por eso el algoritmo es completo.
- Implementarlo **iterativo** (no recursivo), para no chocar con el límite de recursión de Python.

```
pila = [nodo_raiz]
mientras pila no vacía:
    n = pila.pop()
    expandidos += 1
    si es_meta(n.estado): devolver solución
    hijos = []
    para cada (accion, estado, costo) en sucesores(n.estado):
        si crea ciclo en la rama: continuar
        hijos.append(Nodo hijo)
    pila.extend(reversed(hijos))
devolver sin solución
```

## 4. Manejo de ciclos

### 4.1 Lo que pide el enunciado

"En todos los algoritmos evite ciclos. Sin embargo, cuando el agente llegue a la casilla de la avioneta, o a un cultivo seco con fertilizante, o al depósito, debe dejar que se devuelva."

Lo que el enunciado permite es volver a una casilla **cuando algo cambió**: se subió a la avioneta, recargó fertilizante o trató un cultivo. Cualquier otro regreso es un ciclo.

El profesor precisó que el robot puede devolverse al llegar al depósito con el fertilizante lleno. La implementación descarta ese regreso concreto: si el estado (posición, fertilizante, cultivos pendientes y fase de la avioneta) ya está en la rama, se considera ciclo. Esto no pierde soluciones ni cambia el costo, porque volver al depósito con el fertilizante ya lleno no habilita nada nuevo. Permitirlo siempre podría generar bucles; en `Prueba1` el depósito `(0, 2)` es un callejón sin salida.

### 4.2 Problema detectado: la oscilación en la avioneta

Si se usa el `Estado` completo como clave de ciclo, el campo `combustible` baja en cada movimiento mientras el robot va en la avioneta. Entonces `A → B → A` en vuelo produce un estado **distinto** (menos combustible), y no se detectaría como ciclo.

Resultado:
- Se permitirían hasta 30 pasos de vaivén sin sentido.
- Eso multiplica nodos y tiempo, y viola "evite ciclos".

### 4.3 Solución: clave de ciclo relajada

**Clave relajada:** `(pos, fertilizante, cultivos_pendientes, fase_avioneta)`, donde la fase sale de `combustible`:

| `combustible` | `fase_avioneta` |
|---|---|
| `-1` | `"sin_abordar"` |
| `1..30` | `"en_vuelo"` |
| `0` | `"agotada"` |

Por qué la clave relajada es segura: dentro de una misma fase, el combustible nunca sube. Un nodo descendiente con la misma clave relajada que un ancestro es igual o peor que ese ancestro, tanto en costo como en lo alcanzable. Descartarlo no pierde soluciones ni la optimalidad.

La clave relajada sigue permitiendo los regresos legítimos del enunciado, porque abordar la avioneta, recargar y tratar un cultivo cambian la fase, el fertilizante o los cultivos pendientes.

### 4.4 Detección de ciclos por rama

- Se revisan los ancestros del nodo (incluido el padre), tal como lo define el profesor. **Confirmado por el profesor.**
- No existe un conjunto compartido de estados cerrados ni un parámetro para elegir el modo de ciclos.
- La clave relajada se usa en los tres algoritmos; es segura porque dentro de una misma fase el combustible nunca sube.
- Se descartó la alternativa de llevar un conjunto de estados cerrados para ser fiel a la definición de evitar ciclos de las diapositivas. En `Prueba1` daba el mismo costo y la misma profundidad de solución; solo reducía los nodos expandidos.

**Limitación conocida:** en mundos muy abiertos, la búsqueda por rama puede crecer de forma exponencial y alcanzar `limite_nodos`. Se observó con BFS y con DFS en mundos abiertos de prueba.

### 4.5 Límite de seguridad

Cada algoritmo acepta `limite_nodos: int | None = None`. Si se alcanza, la búsqueda se detiene y devuelve `exito = False` con `limite_alcanzado = True`. Sirve para acotar búsquedas costosas, por ejemplo en cuadrículas abiertas donde la búsqueda por rama explora muchos caminos simples. **Confirmado por el profesor:** el corte por `limite_nodos` con el mensaje de "límite alcanzado" es aceptable.

## 5. Interfaz de los algoritmos

```python
busqueda_amplitud(problema, limite_nodos=None) -> Resultado
busqueda_costo_uniforme(problema, limite_nodos=None) -> Resultado
busqueda_profundidad(problema, limite_nodos=None) -> Resultado
```

### `Resultado` (en `algoritmos/base.py`)

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

**Confirmado por el profesor:** "profundidad del árbol" = `profundidad_maxima`. Se guardan ambas (`profundidad` y `profundidad_maxima`) por si la UI necesita la otra.

Helpers en `base.py`:
- `clave_relajada(estado)`.
- `crea_ciclo_en_rama(nodo_padre, estado_hijo, clave)`: recorre `nodo.padre` hacia arriba, incluyendo el padre, comparando claves.
- Un helper para medir el tiempo y construir el `Resultado` (con éxito y sin él).

## 6. Cambios respecto a lo que se había dicho antes

| Tema | Antes | Ahora |
|---|---|---|
| Nodo expandido | El que genera sucesores | El que se extrae y se verifica, **incluye el nodo meta** |
| DFS evitando ciclos | `visitados` compartido | Revisión de ancestros (por rama) |
| Clave de ciclo | `Estado` completo siempre | Relajada (sin combustible exacto) en los tres algoritmos |
| Modo de ciclos | Existía la alternativa de cerrados | Solo por rama, sin parámetro |
| `Resultado` | Sin `exito`, `nodos_generados`, `profundidad_maxima` | Se agregan |

## 7. Pruebas esperadas (`tests/test_algorithms.py`)

Los mundos de prueba se arman escribiendo una matriz 10x10 a un archivo temporal (`tmp_path`) y cargándola con `World.desde_archivo`. Los casos de optimalidad (4 y 5) usan pasillos estrechos similares al ejemplo. **Confirmado por el profesor:** los mundos de prueba son 10x10 y parecidos al ejemplo. Todas las llamadas usan `limite_nodos=200_000` para que ninguna prueba pueda colgarse; las pruebas de solución afirman `exito == True` y `limite_alcanzado == False`.

1. **Sin cultivos:** meta en la raíz. Camino vacío, `costo == 0`, `nodos_expandidos == 1`.
2. **Un cultivo cerca del depósito:** los tres algoritmos devuelven solución válida.
3. **Validez de la solución:** reproducir `camino` paso a paso con `Problema.sucesores` desde el estado inicial. El estado final debe cumplir `es_meta`, y la suma de costos debe ser igual a `Resultado.costo`.
4. **Optimalidad:** en un mundo de pasillos estrechos con varias rutas, `costo(UCS) <= costo(BFS)` y `costo(UCS) <= costo(DFS)`.
5. **BFS no es óptimo en costo:** en un mundo de pasillos donde el desvío por la avioneta abarata el recorrido, `costo(BFS) > costo(UCS)`.
6. **Sin solución:** cultivo encerrado por muros, o depósito inalcanzable. Devuelve `exito == False`, camino vacío, `costo is None`, sin lanzar excepción.
7. **Sin oscilación:** en ninguna solución aparece `pos[i] == pos[i+2]` salvo que entre `i` y `i+2` haya cambiado el fertilizante, los cultivos pendientes o la fase de la avioneta.
8. **Meta al extraer:** el nodo meta cuenta como expandido, y `nodos_expandidos >= len(camino) + 1` en BFS.
9. **DFS apila en orden inverso:** en un mundo abierto, la primera expansión de DFS sigue "arriba" cuando es posible.
10. **`limite_nodos`** corta la búsqueda con `exito == False` y `limite_alcanzado == True`.

## 8. Verificación sobre `Prueba1.txt`

Un script de consola (`scripts/comparar_no_informada.py`) debe correr BFS, UCS y DFS sobre `worlds/Prueba1.txt` y mostrar una tabla con:

`algoritmo | exito | nodos_expandidos | nodos_generados | profundidad | profundidad_maxima | tiempo | costo`

Los tres algoritmos evitan ciclos solo por rama; no hay filas ni columnas de modo de ciclos.

## 9. Supuestos que hay que mencionar en el informe

**Confirmado por el profesor:**

1. Test de meta al extraer; el nodo meta cuenta como expandido y no genera hijos.
2. Ciclos solo por rama en BFS, UCS y DFS (revisión de ancestros).
3. Desempate de UCS por orden de creación y orden de operadores arriba, abajo, izquierda, derecha.
4. Los mundos de prueba son 10x10 y, en los casos de optimalidad, pasillos estrechos similares al ejemplo.
5. El corte por `limite_nodos` con mensaje de "límite alcanzado" es aceptable.
6. "Profundidad del árbol" = `profundidad_maxima`.
7. El movimiento que llega a la casilla de la avioneta cuesta 1 (el costo se determina por el combustible previo).
8. No hay bajada voluntaria de la avioneta.

**Supuestos del equipo:**

9. Clave de ciclo relajada. Se usa para que el vaivén dentro de la avioneta cuente como ciclo y para no multiplicar nodos. Es conservadora: dentro de una misma fase el combustible no sube y un descendiente con la misma clave es igual o peor que el ancestro, así que descartarlo no pierde soluciones ni optimalidad.
10. Los supuestos 3 a 6 del core (codificación de `combustible`, tratamiento automático y obligatorio, casillas transitables, orden de operadores), ya documentados en el README.

**Nota de implementación (regreso al depósito):** el profesor respondió que el robot puede devolverse al llegar al depósito con el fertilizante lleno. La implementación descarta ese regreso concreto porque el estado ya está en la rama; no pierde soluciones ni cambia el costo y evita bucles. En `Prueba1` el depósito es un callejón sin salida.

**Nota (sin confirmar):** el vaivén `A → B → A` dentro de la avioneta cuenta como ciclo en la implementación, porque la clave relajada agrupa toda la fase "en_vuelo".
