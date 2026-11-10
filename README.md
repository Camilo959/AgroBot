# AgroBot — Proyecto 1 de Inteligencia Artificial (Univalle)

Agente que recorre una cuadrícula de 10x10 y debe aplicar fertilizante a
todos los cultivos secos. Stack: Python, pygame y customtkinter.

## Estructura

```text
agrobot/
├── main.py, requirements.txt, README.md, pytest.ini
├── core/      (mundo.py, estado.py, problema.py, nodo.py)
├── algoritmos/ (base.py, busqueda_no_informada/, busqueda_informada/)
├── ui/        (app.py, theme.py, textos.py, componentes.py, board_view.py,
│              runner.py, animator.py, report_panel.py, sesion.py,
│              assets_loader.py, screens/, assets/)
├── scripts/   (comparar_no_informada.py, comparar_algoritmos.py)
├── worlds/    (Prueba1.txt)
├── tests/     (test_world.py, test_problem.py, test_algorithms.py,
│              test_heuristics.py, test_ui_logica.py)
└── docs/      (informe/, CAMBIOS.md, CONTEXTO_BUSQUEDA_NO_INFORMADA.md,
               CONTEXTO_BUSQUEDA_INFORMADA.md)
```

## Entorno virtual

Python requerido: **3.10 o superior** (se usa `X | None` y `tuple[int, int]`).
Verificado con Python 3.12.3 en Windows.

Crear e instalar dependencias:

```bash
python -m venv .venv
```

Activar el entorno:

| Sistema | Comando |
|---|---|
| Windows PowerShell | `.\.venv\Scripts\Activate.ps1` |
| Windows CMD | `.venv\Scripts\activate.bat` |
| Linux / macOS (bash/zsh) | `source .venv/bin/activate` |

Instalar dependencias y correr pruebas:

```bash
pip install -r requirements.txt
pytest -v
```

> Nota: en este equipo (Windows) el shell es Git Bash, por lo que los
> comandos se invocan como `./.venv/Scripts/python.exe -m pytest -v`.
> Detecta tu SO con `python -c "import platform; print(platform.system())"`.

## Cómo ejecutar la aplicación

```bash
python main.py
```

La interfaz tiene dos pantallas: la **principal** (cabecera de inicio,
carga de mundo, elección de algoritmo, ejecución y tablero) y el
**Resumen** (reporte y acceso a la animación). La portada anterior se
fusionó con la pantalla principal. En la pantalla principal, "Informada"
habilita Avara y A*.

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
búsqueda** (algoritmo, estado, nodos expandidos, nodos generados,
profundidad de la solución, profundidad máxima del árbol, tiempo, costo
cuando aplica y mundo) y, abajo, el estado en vivo (paso, fertilizante,
combustible, costo acumulado) más la leyenda de controles. La velocidad,
el ancho del panel y los colores se configuran en `ui/theme.py`.

### Flujo de resultados

Al pulsar **Ejecutar** se calcula la búsqueda y se abre directamente la
animación. El HUD ya muestra el reporte resumido desde el inicio. Al
llegar a la meta aparece además el botón **"Ver Resultados Detallados"**;
la pantalla de resumen se abre al pulsarlo. Si la animación se cierra
antes de la meta, el botón aparece en la pantalla principal. Cuando no
hay solución o se alcanza el límite de nodos (no hay animación), el botón
aparece de inmediato en la pantalla principal.

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
   ciclos se detectan solo por rama con la **clave relajada**
   `(posición, fertilizante, cultivos pendientes, fase de la avioneta)`:
   no se compara el combustible exacto. Así el agente puede volver a una
   casilla si algo cambió (abordó la avioneta, recargó fertilizante o trató
   un cultivo), pero el vaivén dentro de la avioneta sí cuenta como ciclo.

## Alcance actual (core + búsqueda no informada e informada + UI)

- `core/mundo.py`: clase `World` con `desde_archivo`, `es_libre` y `__str__`.
- `core/estado.py`: `Estado` como `@dataclass(frozen=True)` (hasheable).
- `core/problema.py`: `Problema` con `estado_inicial`, `es_meta` y
  `sucesores` (lista de `(accion, estado_nuevo, costo)`).
- `core/nodo.py`: `Nodo` con `reconstruir_camino`, `reconstruir_estados` y
  `__lt__` (desempate por `g` y orden de creación) para usarlo en `heapq`.
- `algoritmos/base.py`: `Resultado`, claves de ciclo, detección en rama.
- `algoritmos/busqueda_no_informada/`: `amplitud.py`, `costo_uniforme.py`
  y `profundidad.py`.
- `algoritmos/busqueda_informada/heuristicas.py`: heurística B
  (Manhattan + MST).
- `algoritmos/busqueda_informada/`: `avara.py` y `a_estrella.py`.
- `ui/`: tema centralizado, pantallas, tablero, runner de procesos,
  reporte puro y animación pygame. Ver `ui/README_UI.md`.

Estado: el proyecto cubre lectura y visualización del mundo, los cinco
algoritmos, animación, reporte y búsquedas cancelables en procesos
aparte. La arquitectura general se mantiene estable para la entrega.

## Algoritmos de búsqueda no informada

| Algoritmo | Función | Estructura |
|---|---|---|
| Amplitud (BFS) | `busqueda_amplitud` | cola FIFO (`deque`) |
| Costo uniforme (UCS) | `busqueda_costo_uniforme` | `heapq` por `g` |
| Profundidad (DFS) | `busqueda_profundidad` | pila (iterativo) |

- **Test de meta al extraer** el nodo (nunca al generar); el meta cuenta
  como expandido.
- **Ciclos solo por rama:** se revisan los ancestros del camino actual
  (incluido el padre), como define el profesor. No hay conjunto compartido
  de estados cerrados ni parámetro de modo.
- **Clave relajada** (sin el combustible exacto): evita que el vaivén
  `A → B → A` dentro de la avioneta cuente como ciclo, y permite los
  regresos que autoriza el enunciado.
- **`limite_nodos`**: máximo de nodos a expandir; al alcanzarlo devuelve
  `exito=False` con `limite_alcanzado=True`.
- **Limitación:** en mundos muy abiertos la búsqueda por rama puede crecer
  exponencialmente y alcanzar el límite de nodos.
- Comparación sobre `Prueba1.txt`:
  `python scripts/comparar_no_informada.py`.

## Algoritmos de búsqueda informada y heurística

| Algoritmo | Función | Prioridad |
|---|---|---|
| Avara | `busqueda_avara` | `h(n)` |
| A* | `busqueda_a_estrella` | `g(n) + h(n)` |

- Ambos usan `HeuristicaAgroBot(world)`, la misma heurística B:
  `h = 0.5 · L`, donde `L` es una cota inferior de movimientos calculada
  con distancias Manhattan y un MST sobre la posición, el depósito y los
  cultivos pendientes.
- La heurística no depende del combustible y es admisible
  (`h(n) ≤ costo real`).
- Se mantienen las convenciones: meta al extraer, nodo meta expandido,
  ciclos solo por rama con clave relajada, desempate por orden de
  creación y `limite_nodos`.
- A* es óptimo con heurística admisible; Avara no garantiza optimalidad.
- Comparación de los cinco algoritmos sobre `Prueba1.txt`:
  `python scripts/comparar_algoritmos.py`.

## Checklist de entrega

Desde la raíz del proyecto y con el entorno virtual activo:

```bash
# Pruebas automáticas
pytest -v

# Comparación de los cinco algoritmos sobre Prueba1
python scripts/comparar_algoritmos.py

# Aplicación gráfica
python main.py
```

Verificación manual mínima:

1. Cargar `worlds/Prueba1.txt` y ejecutar los cinco algoritmos.
2. Confirmar que la animación y el HUD muestran el reporte.
3. Confirmar que el costo solo aparece en Costo uniforme y A*.
4. Probar un mundo sin solución y una búsqueda que alcance el límite.
5. Probar la carga de un archivo inválido.

El informe de heurística está en `docs/informe/heuristica.md`.
