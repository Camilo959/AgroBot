# AgroBot — Proyecto 1 de Inteligencia Artificial (Univalle)

Agente que recorre una cuadrícula de 10x10 y debe aplicar fertilizante a
todos los cultivos secos. Stack: Python, pygame y customtkinter.

## Estructura

```text
agrobot/
├── main.py, requirements.txt, README.md
├── core/      (world.py, state.py, problem.py, node.py)
├── algorithms/ (bfs.py, ucs.py, dfs.py, greedy.py, astar.py, ...)
├── ui/        (app.py, report_panel.py, animator.py, assets/)
├── worlds/    (Prueba1.txt, ...)
├── tests/     (test_problem.py, test_world.py, ...)
└── docs/informe/
```

## Entorno virtual

Python requerido: **3.10 o superior** (se usa `X | None` y `tuple[int, int]`).
Verificado con Python 3.12.3 en Windows.

Crear e instalar dependencias:

```bash
python -m venv venv
```

Activar el entorno:

| Sistema | Comando |
|---|---|
| Windows PowerShell | `.\venv\Scripts\Activate.ps1` |
| Windows CMD | `venv\Scripts\activate.bat` |
| Linux / macOS (bash/zsh) | `source venv/bin/activate` |

Instalar dependencias y correr pruebas:

```bash
pip install -r requirements.txt
pytest -v
```

> Nota: en este equipo (Windows) el shell es Git Bash, por lo que los
> comandos se invocan como `./venv/Scripts/python.exe -m pytest -v`.
> Detecta tu SO con `python -c "import platform; print(platform.system())"`.

## Supuestos de diseño

1. **Costo al abordar la avioneta.** El movimiento que llega a la casilla de
   la avioneta cuesta 1, porque el costo se determina por el combustible
   *antes* de moverse. El 0.5 aplica desde el movimiento siguiente, y el
   combustible pasa a 30 al subirse.
2. **Sin bajada voluntaria.** Una vez abordada, el robot va en la avioneta
   hasta agotar el combustible. Después, pasar por su casilla no hace nada.
3. **Codificación del combustible.** `-1` = aún no ha abordado, `1..30` = en
   la avioneta con ese combustible restante, `0` = agotada. Mientras
   `combustible > 0`, cada movimiento cuesta 0.5 y resta 1.
4. **Tratamiento automático y obligatorio.** Al llegar a un cultivo seco con
   fertilizante > 0 se trata de inmediato (fertilizante −1 y el cultivo deja
   de estar pendiente). Sin fertilizante, el robot pasa por encima y el
   cultivo sigue seco. El robot puede tratar estando en la avioneta.
5. **Casillas transitables.** Las casillas 2, 3, 4 y 5 son transitables;
   solo el muro (1) bloquea. Una vez leído el mundo, la casilla del robot
   cuenta como libre.
6. **Orden fijo de operadores.** Arriba, abajo, izquierda, derecha. Los
   ciclos se detectan sobre el **estado completo** (posición + fertilizante
   + combustible + pendientes), así el agente puede volver a una casilla si
   algo cambió (abordó la avioneta, recargó fertilizante o trató un cultivo).

## Alcance actual (core + búsqueda no informada, sin UI)

- `core/world.py`: clase `World` con `desde_archivo`, `es_libre` y `__str__`.
- `core/state.py`: `Estado` como `@dataclass(frozen=True)` (hasheable).
- `core/problem.py`: `Problema` con `estado_inicial`, `es_meta` y
  `sucesores` (lista de `(accion, estado_nuevo, costo)`).
- `core/node.py`: `Nodo` con `reconstruir_camino`, `reconstruir_estados` y
  `__lt__` (desempate por `g` y orden de creación) para usarlo en `heapq`.
- `algorithms/base.py`: `Resultado`, claves de ciclo, detección en rama.
- `algorithms/bfs.py`, `ucs.py`, `dfs.py`: las tres búsquedas.

Fuera de alcance por ahora: `greedy.py`, `astar.py`, `heuristics.py`,
`ui/` y `main.py`.

## Algoritmos de búsqueda no informada

| Algoritmo | Función | Estructura | Defecto `modo_ciclos` |
|---|---|---|---|
| Amplitud (BFS) | `busqueda_amplitud` | cola FIFO (`deque`) | `"rama"` |
| Costo uniforme (UCS) | `busqueda_costo_uniforme` | `heapq` por `g` | `"rama"` |
| Profundidad (DFS) | `busqueda_profundidad` | pila (iterativo) | `"rama"` |

- **Test de meta al extraer** el nodo (nunca al generar); el meta cuenta
  como expandido.
- **`modo_ciclos`** (por defecto `"rama"` en los tres): `"rama"` revisa
  solo los ancestros del camino actual y permite los regresos que autoriza
  el enunciado; `"global"` marca estados ya expandidos (cerrados) y suele
  expandir menos nodos. BFS y DFS usan la clave relajada (sin combustible
  exacto: evita la oscilación en la avioneta) en ambos modos; UCS usa la
  clave completa en `"global"` (preserva la optimalidad) y la relajada en
  `"rama"`. Valor inválido → `ValueError`.
- **`limite_nodos`**: máximo de nodos a expandir; al alcanzarlo devuelve
  `exito=False` con `limite_alcanzado=True`. Útil para probar `"rama"`
  sin colgar la terminal.
- Comparación sobre `Prueba1.txt`:
  `python scripts/comparar_no_informada.py`.
