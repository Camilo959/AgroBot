# Registro de cambios — AgroBot

Historial de modificaciones del proyecto. Cada entrada indica fecha,
archivos afectados y descripción del cambio.

---

## 2026-10-29 — Core del proyecto (lógica pura, sin UI ni algoritmos)

Archivos creados/modificados:

- `core/world.py` (nuevo): clase `World` con `desde_archivo(ruta)`
  (lectura y validación 10x10, valores 0-5, exactamente un 2/4/5;
  lanza `FileNotFoundError` / `ValueError`), atributos `filas`,
  `columnas`, `matriz`, `muros`, `inicio`, `deposito`, `avioneta`,
  `cultivos`, y métodos `es_libre` y `__str__`.
- `core/state.py` (nuevo): `Estado` como `@dataclass(frozen=True)` con
  `pos`, `fertilizante`, `combustible`, `cultivos_pendientes`. Sin
  lógica de transición.
- `core/problem.py` (nuevo): `Problema` con `estado_inicial`,
  `es_meta`, `sucesores` (orden arriba/abajo/izquierda/derecha) y
  constante `MOVIMIENTOS`. Orden de eventos: costo/combustible →
  depósito/cultivo → abordaje de avioneta.
- `core/node.py` (nuevo): `Nodo` con `__slots__`,
  `reconstruir_camino`, `reconstruir_estados` y `__lt__` (desempate
  por `g` y contador de creación) para `heapq`.
- `core/__init__.py` (modificado): exporta
  `Estado`, `Nodo`, `Problema`, `World`.
- `requirements.txt` (modificado): `pygame`, `customtkinter`, `pytest`.
- `.gitignore` (nuevo): `venv/`, `__pycache__/`, `.pytest_cache/`,
  `*.pyc`, `.vscode/`, `.idea/`.
- `pytest.ini` (nuevo): `pythonpath = .` para imports desde la raíz.
- `venv/` (nuevo): entorno virtual, Python 3.12.3, dependencias
  instaladas y verificadas.
- `tests/test_problem.py` (nuevo, 16 pruebas): estado inicial, meta,
  hashabilidad, costo 1 normal, abordaje (30) y 0.5 posterior,
  agotamiento tras 30 movimientos, depósito, tratamiento con/sin
  fertilizante (incluido en avioneta), muros/fuera de cuadrícula,
  orden de operadores, `Nodo` (caminos y `heapq`).
- `tests/test_world.py` (nuevo, 8 pruebas): lectura de Prueba1
  (inicio (4,0), depósito (0,2), avioneta (0,6), cultivos
  {(4,3),(5,3),(6,8)}), 4 errores de validación, `es_libre`, `__str__`.
- `README.md` (modificado): estructura, entorno virtual y activación
  por SO, supuestos de diseño 1-6, alcance del core.

Resultado: `pytest -v` → **24 passed**.

Supuestos de diseño adoptados:

1. Llegar a la avioneta cuesta 1 (costo según combustible previo);
   el 0.5 aplica desde el movimiento siguiente (combustible → 30).
2. Sin bajada voluntaria; pasar por la avioneta agotada no hace nada.
3. `combustible`: `-1` sin abordar, `1..30` en avioneta, `0` agotada.
4. Tratamiento automático y obligatorio (también en avioneta).
5. Casillas 2/3/4/5 transitables; la del robot cuenta como libre.
6. Orden fijo: arriba, abajo, izquierda, derecha; ciclos sobre el
   estado completo.

Sin tocar (fuera de alcance): `algorithms/`, `ui/`, `main.py`.

---

## 2026-10-30 — Búsqueda no informada (BFS, UCS, DFS)

Especificación: `docs/CONTEXTO_BUSQUEDA_NO_INFORMADA.md` (manda sobre el
prompt anterior; sus cambios están listados en su sección 6). `core/` no
se modificó: era compatible (`Nodo.padre/g/profundidad`, contador de
creación y `es_meta`).

Archivos creados/modificados:

- `algorithms/base.py` (nuevo): `Resultado` (`exito`, `camino`,
  `estados`, `nodos_expandidos`, `nodos_generados`, `profundidad`,
  `profundidad_maxima`, `tiempo`, `costo`, `limite_alcanzado`),
  `clave_completa` / `clave_relajada` (fase `sin_abordar` / `en_vuelo` /
  `agotada` según `combustible`), `crea_ciclo_en_rama`,
  `validar_modo_ciclos`, `construir_exito` / `construir_fracaso` y
  `ahora` (`time.perf_counter`).
- `algorithms/bfs.py` (nuevo): `busqueda_amplitud` con `deque`
  (por defecto `modo_ciclos="global"`, clave relajada).
- `algorithms/ucs.py` (nuevo): `busqueda_costo_uniforme` con `heapq`
  `(g, contador, nodo)` (por defecto `"global"` con clave completa;
  `"rama"` con relajada).
- `algorithms/dfs.py` (nuevo): `busqueda_profundidad` iterativa con
  pila e hijos en orden inverso (por defecto `"rama"`, clave relajada).
- `algorithms/__init__.py` (modificado): exporta las tres búsquedas.
- `tests/test_algorithms.py` (nuevo, 25 pruebas): los 12 casos de la
  especificación. Caso 5 construido (mundo abierto con avioneta en
  (0, 0): BFS = 18 pasos a costo 18, UCS = 15.5). Caso 6 con depósito
  inalcanzable (robot encerrado): el cultivo encerrado en mundo abierto
  se descartó porque DFS por rama tarda tiempo exponencial en fallar
  ahí (verificado: >300 s sin terminar); el corte por límite se cubre
  en el caso 11.
- `scripts/comparar_no_informada.py` (nuevo, carpeta `scripts/` nueva):
  tabla de la sección 8 sobre `worlds/Prueba1.txt`; `"rama"` de BFS y
  UCS con `limite_nodos=2_000_000`.
- `README.md` (modificado): sección de algoritmos no informados.

Resultado: `pytest -v` → **49 passed** (24 del core + 25 nuevos).

Supuestos tomados:

1. Test de meta al extraer; el meta cuenta como expandido; un repetido
   descartado al extraer en modo global no cuenta.
2. Desempate UCS por orden de creación (contador propio por búsqueda).
3. `limite_nodos` = máximo de nodos a expandir (se revisa antes de
   extraer); al alcanzarlo: `exito=False`, `limite_alcanzado=True`.
4. Sin solución: `camino=[]`, `estados=[]`, `costo=None`, `profundidad=0`
   (se conserva `profundidad_maxima` alcanzada), sin excepción.

Tabla sobre `Prueba1.txt`:

```text
alg    modo       exito  expandidos        generados        prof        prof_max           tiempo   costo
BFS    global     True   651               1424             30          31                 0.01     30.0
UCS    global     True   3380              7377             38          40                 0.05     25.0
DFS    rama       True   81                105              68          76                 0.00     58.0
BFS    rama       True   5251              6423             30          31                 0.11     30.0
UCS    rama       True   9561              12335            38          40                 0.23     25.0
```

Los modos `"rama"` de BFS y UCS fueron viables en Prueba1 (mismo costo
que en `"global"`, sin chocar con el límite). UCS abarata el costo
(25.0 vs 30.0) usando la avioneta; DFS da una solución larga (68 pasos,
costo 58.0), como es esperado.

Sin tocar (fuera de alcance): `greedy.py`, `astar.py`, `heuristics.py`,
`ui/`, `main.py`.

---

## 2026-11-02 — `modo_ciclos="rama"` por defecto en los tres algoritmos

Decisión: los ciclos se evitan por rama por defecto en BFS, UCS y DFS,
porque el enunciado permite devolverse (subir a la avioneta, recargar,
tratar un cultivo) y la clave relajada ya cubre esos regresos. `"global"`
sigue disponible como opción.

Archivos modificados:

- `algorithms/bfs.py` (modificado): valor por defecto `modo_ciclos="rama"`;
  docstring actualizado. No cambió la lógica ni el conteo de expandidos.
- `algorithms/ucs.py` (modificado): valor por defecto `modo_ciclos="rama"`;
  docstring actualizado. Se conserva la regla de claves (completa en
  `"global"`, relajada en `"rama"`). Sin cambios de lógica ni de conteo.
- `algorithms/dfs.py` (sin cambios): ya tenía `"rama"` por defecto.
- `tests/test_algorithms.py` (modificado): `test_4` y `test_5` fijan
  `modo_ciclos="global"` en BFS y UCS. Motivo: el mundo abierto con la
  meta lejana hace que `"rama"` explote combinatoriamente en BFS (se
  comprobó: `pytest` no terminó en 15 min); la propiedad que verifican
  (optimalidad de UCS y BFS no óptimo en costo) no depende del modo. El
  modo por defecto (`"rama"`) se sigue cubriendo en `test_3b` sobre
  Prueba1 y en `test_1`, `test_2`, `test_3`, `test_6`–`test_11`.
  No cambió ninguna aserción.
- `scripts/comparar_no_informada.py` (modificado): las tres filas
  principales usan los valores por defecto (rama); se conservan las filas
  `"global"` de BFS y UCS como comparación. Se eliminó el límite de
  2 000 000 porque `"rama"` ya es el modo por defecto y no lo necesita.
- `docs/CONTEXTO_BUSQUEDA_NO_INFORMADA.md` (modificado):
  - 4.4: tabla con `"rama"` por defecto en los tres; se conserva la regla
    de claves (BFS/DFS relajada; UCS completa en `"global"` y relajada en
    `"rama"`). Se reemplazó el párrafo de "por qué BFS y UCS usan global"
    por la nota de la decisión.
  - 5: firmas con `modo_ciclos="rama"`; "profundidad del árbol" marcada
    como confirmada por el profesor.
  - 6: nueva fila con el cambio del valor por defecto.
  - 9: supuestos separados en "Confirmado por el profesor" (profundidad
    del árbol = `profundidad_maxima`, llegar a la avioneta cuesta 1, sin
    bajada voluntaria) y "Supuestos del equipo" (nodo meta expandido,
    desempate UCS, `"rama"` por defecto, clave relajada, supuestos 3-6 del
    core).
- `README.md` (modificado): tabla de algoritmos con `"rama"` por defecto
  y explicación de `modo_ciclos`, claves y `limite_nodos`.

Resultado: `pytest -v` → **49 passed** (80.45 s).

Tabla sobre `Prueba1.txt` (valores por defecto):

```text
alg    modo       exito  expandidos        generados        prof        prof_max           tiempo   costo
BFS    rama       True   5251              6423             30          31                 0.11     30.0
UCS    rama       True   9561              12335            38          40                 0.21     25.0
DFS    rama       True   81                105              68          76                 0.00     58.0
BFS    global     True   651               1424             30          31                 0.01     30.0
UCS    global     True   3380              7377             38          40                 0.05     25.0
```

Coincide con las filas `"rama"` de la corrida anterior: BFS 5251
expandidos, UCS 9561, DFS 81. Ningún modo chocó con límites.

Sin tocar (fuera de alcance): `core/`, `ui/`, `main.py`, `greedy.py`,
`astar.py`, `heuristics.py`.
