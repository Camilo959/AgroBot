# AgroBot — Proyecto 1 de Inteligencia Artificial (Univalle)

Agente que recorre una cuadrícula de 10x10 y debe aplicar fertilizante a
todos los cultivos secos. Stack: Python, pygame y customtkinter.

## Estructura

```text
agrobot/
├── main.py, requirements.txt, README.md, pytest.ini
├── core/      (world.py, state.py, problem.py, node.py)
├── algorithms/ (base.py, bfs.py, ucs.py, dfs.py, ...)
├── ui/        (app.py, theme.py, textos.py, componentes.py, board_view.py,
│              runner.py, animator.py, report_panel.py, sesion.py,
│              assets_loader.py, screens/, assets/)
├── scripts/   (comparar_no_informada.py)
├── worlds/    (Prueba1.txt, ...)
├── tests/     (test_world.py, test_problem.py, test_algorithms.py,
│              test_ui_logica.py)
└── docs/      (informe/, CAMBIOS.md, CONTEXTO_BUSQUEDA_NO_INFORMADA.md)
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

## Cómo ejecutar la aplicación

```bash
python main.py
```

La interfaz tiene dos pantallas: la **principal** (cabecera de inicio,
carga de mundo, elección de algoritmo, ejecución y tablero) y el
**Resumen** (reporte y acceso a la animación). La portada anterior se
fusionó con la pantalla principal. En la pantalla principal, "Informada"
muestra Avara y A* deshabilitados con la leyenda "próximamente".

### Arquitectura de procesos

Customtkinter y pygame no comparten proceso:

1. La ventana principal (customtkinter) no importa pygame.
2. La búsqueda corre en un proceso hijo con `multiprocessing` (contexto
   `spawn`), lanzada desde `ui/runner.py`. Se puede cancelar con
   `terminate()` y la interfaz consulta el resultado con `after(...)`.
3. La animación (pygame) corre en otro proceso `spawn`
   (`ui/animator.py`). Cerrar su ventana no cierra la principal.
4. Al cerrar la ventana principal se terminan los procesos hijos vivos.

### Controles de la animación

| Tecla | Acción |
|---|---|
| Espacio | Pausar / reanudar |
| ← / → | Paso anterior / siguiente |
| ↑ / ↓ | Subir / bajar velocidad |
| R | Reiniciar |
| Esc | Cerrar la animación |

El panel lateral de la animación muestra, arriba, el **resumen de la
búsqueda** (algoritmo, estado, nodos expandidos, profundidad del árbol,
tiempo, pasos, costo cuando aplica y mundo) y, abajo, el estado en vivo
(paso, fertilizante, combustible, costo acumulado) más la leyenda de
controles. La velocidad, el ancho del panel y los colores se configuran
en `ui/theme.py`.

### Flujo de resultados

Al pulsar **Ejecutar** se calcula la búsqueda y se abre directamente la
animación, sin mostrar el reporte. Al llegar a la meta aparece en el HUD
el botón **"Ver Resultados Detallados"**; el reporte solo se abre al
pulsarlo. Si la animación se cierra antes de la meta, el botón aparece en
la pantalla principal. Cuando no hay solución o se alcanza el límite de
nodos (no hay animación), el botón aparece de inmediato en la pantalla
principal.

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

## Alcance actual (core + búsqueda no informada + UI)

- `core/world.py`: clase `World` con `desde_archivo`, `es_libre` y `__str__`.
- `core/state.py`: `Estado` como `@dataclass(frozen=True)` (hasheable).
- `core/problem.py`: `Problema` con `estado_inicial`, `es_meta` y
  `sucesores` (lista de `(accion, estado_nuevo, costo)`).
- `core/node.py`: `Nodo` con `reconstruir_camino`, `reconstruir_estados` y
  `__lt__` (desempate por `g` y orden de creación) para usarlo en `heapq`.
- `algorithms/base.py`: `Resultado`, claves de ciclo, detección en rama.
- `algorithms/bfs.py`, `ucs.py`, `dfs.py`: las tres búsquedas.
- `ui/`: tema centralizado, pantallas, tablero, runner de procesos,
  reporte puro y animación pygame. Ver `ui/README_UI.md`.

Fuera de alcance por ahora: `greedy.py`, `astar.py`, `heuristics.py`
(Avara y A* aparecen deshabilitados en la UI).

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
