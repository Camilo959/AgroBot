# AgroBot — Proyecto 1 de Inteligencia Artificial (Univalle)

Agente que recorre una cuadrícula de 10x10 y debe aplicar fertilizante a
todos los cultivos secos. El entorno incluye obstáculos, un depósito de
fertilizante y una avioneta con combustible limitado. Stack: Python,
pygame y customtkinter.

## Contenido de la entrega

```text
AgroBot/
├── main.py
├── requirements.txt
├── README.md
├── core/
├── algoritmos/
├── ui/
├── worlds/
│   └── Prueba1.txt
└── docs/
    └── informe/
        └── heuristica.md
```

## Requisitos

- Python 3.10 o superior.
- Dependencias: `pygame`, `customtkinter` y `pillow`.

## Entorno virtual

Crear el entorno e instalar dependencias:

```bash
python -m venv .venv
```

Activar el entorno:

| Sistema | Comando |
|---|---|
| Windows PowerShell | `.\.venv\Scripts\Activate.ps1` |
| Windows CMD | `.venv\Scripts\activate.bat` |
| Linux / macOS (bash/zsh) | `source .venv/bin/activate` |

Instalar dependencias:

```bash
pip install -r requirements.txt
```

> Nota: en Windows con Git Bash los comandos se invocan como
> `./.venv/Scripts/python.exe ...`.

## Cómo ejecutar

```bash
python main.py
```

La interfaz permite cargar un mundo, elegir el tipo de búsqueda y el
algoritmo, ejecutar la búsqueda y ver la animación y el reporte.

## Controles de la animación

| Tecla | Acción |
|---|---|
| Espacio | Pausar / reanudar |
| ← / → | Paso anterior / siguiente |
| ↑ / ↓ | Subir / bajar velocidad |
| R | Reiniciar |
| Esc | Cerrar la animación |

## Flujo de resultados

Al pulsar **Ejecutar** se calcula la búsqueda y se abre la animación. El
HUD muestra un resumen de la búsqueda desde el inicio. Al llegar a la meta
aparece el botón **Ver Resultados Detallados**, que abre la pantalla de
resumen. Si la animación se cierra antes, el botón aparece en la pantalla
principal. Cuando no hay solución o se alcanza el límite de nodos, el
botón aparece de inmediato.

La pantalla **Resumen** separa la información en dos bloques:

- **Búsqueda:** algoritmo, tipo, estado, nodos expandidos, nodos
  generados, profundidad máxima, tiempo, nodos por segundo y límite de
  nodos.
- **Solución:** profundidad de la solución, cultivos tratados, pasos con
  costo 1.0 y 0.5, posición final, fertilizante final y combustible final.

El costo total y el costo desglosado por tipo de paso se muestran solo
para Costo uniforme y A*. Los demás algoritmos muestran cuántos pasos
hicieron con cada costo, pero no el costo monetario.

## Supuestos de diseño

1. **Costo al abordar la avioneta.** El movimiento que llega a la casilla
   de la avioneta cuesta 1, porque el costo se determina por el
   combustible antes de moverse. El 0.5 aplica desde el movimiento
   siguiente, y el combustible pasa a 30 al subirse.
2. **Sin bajada voluntaria.** Una vez abordada, la avioneta se mueve con
   el robot hasta agotar el combustible. Después, pasar por su casilla no
   hace nada.
3. **Combustible.** `-1` significa que aún no se abordó la avioneta,
   `1..30` que está en uso con ese combustible restante y `0` que ya se
   agotó. Mientras `combustible > 0`, cada movimiento cuesta 0.5 y resta 1.
4. **Tratamiento automático y obligatorio.** Al llegar a un cultivo seco
   con fertilizante disponible se trata de inmediato: se consume una
   unidad y el cultivo deja de estar pendiente. Sin fertilizante, el
   cultivo sigue seco. El tratamiento también ocurre en la avioneta.
5. **Casillas transitables.** Las casillas 2, 3, 4 y 5 son transitables;
   solo el muro (1) bloquea. La casilla inicial del robot cuenta como
   libre.
6. **Orden fijo de operadores.** Arriba, abajo, izquierda, derecha. Los
   ciclos se detectan solo por rama con la clave relajada
   `(posición, fertilizante, cultivos pendientes, fase de la avioneta)`:
   no se compara el combustible exacto. Así el agente puede volver a una
   casilla si algo cambió, pero el vaivén dentro de la avioneta cuenta
   como ciclo.

## Algoritmos de búsqueda no informada

| Algoritmo | Función | Estructura |
|---|---|---|
| Amplitud (BFS) | `busqueda_amplitud` | cola FIFO (`deque`) |
| Costo uniforme (UCS) | `busqueda_costo_uniforme` | `heapq` por `g` |
| Profundidad (DFS) | `busqueda_profundidad` | pila iterativa |

- El test de meta se hace al extraer el nodo; el nodo meta cuenta como
  expandido.
- Los ciclos se revisan solo por rama, comparando los ancestros del nodo
  actual.
- La clave de ciclo es relajada: no incluye el combustible exacto.
- `limite_nodos` corta la búsqueda si crece demasiado y devuelve
  `exito=False` con `limite_alcanzado=True`.
- En mundos muy abiertos la búsqueda por rama puede crecer
  exponencialmente y alcanzar ese límite.

## Algoritmos de búsqueda informada y heurística

| Algoritmo | Función | Prioridad |
|---|---|---|
| Avara | `busqueda_avara` | `h(n)` |
| A* | `busqueda_a_estrella` | `g(n) + h(n)` |

Ambos usan la heurística B:

```text
h = 0.5 · L
```

donde `L` es una cota inferior del número de movimientos que faltan,
calculada con distancias Manhattan y un árbol de expansión mínima (MST)
sobre la posición, el depósito y los cultivos pendientes. La heurística
no depende del combustible y es admisible: nunca sobreestima el costo
real. A* es óptimo con heurística admisible; Avara no garantiza
optimalidad.

## Informe

La explicación de la heurística y la justificación de su admisibilidad
están en:

```text
docs/informe/heuristica.md
```

## Verificación rápida

1. Ejecutar `python main.py`.
2. Cargar `worlds/Prueba1.txt`.
3. Probar los cinco algoritmos.
4. Confirmar que la animación y el HUD muestran el reporte.
5. Confirmar que el costo solo aparece en Costo uniforme y A*.
6. Probar un mundo sin solución y una búsqueda que alcance el límite.
