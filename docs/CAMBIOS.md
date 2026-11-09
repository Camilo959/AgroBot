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
  `clave_relajada` (fase `sin_abordar` / `en_vuelo` / `agotada` según
  `combustible`), `crea_ciclo_en_rama`, `construir_exito` /
  `construir_fracaso` y `ahora` (`time.perf_counter`).
- `algorithms/bfs.py` (nuevo): `busqueda_amplitud` con `deque` y clave
  relajada.
- `algorithms/ucs.py` (nuevo): `busqueda_costo_uniforme` con `heapq`
  `(g, contador, nodo)` y clave relajada.
- `algorithms/dfs.py` (nuevo): `busqueda_profundidad` iterativa con
  pila e hijos en orden inverso.
- `algorithms/__init__.py` (modificado): exporta las tres búsquedas.
- `tests/test_algorithms.py` (nuevo): casos de la especificación. El
  caso sin solución usa un depósito inalcanzable (robot encerrado) para
  que DFS no agote un área abierta.
- `scripts/comparar_no_informada.py` (nuevo, carpeta `scripts/` nueva):
  tabla de la sección 8 sobre `worlds/Prueba1.txt`.
- `README.md` (modificado): sección de algoritmos no informados.

Resultado: `pytest -v` → **49 passed** (24 del core + 25 nuevos).

Supuestos tomados:

1. Test de meta al extraer; el meta cuenta como expandido.
2. Desempate UCS por orden de creación (contador propio por búsqueda).
3. `limite_nodos` = máximo de nodos a expandir (se revisa antes de
   extraer); al alcanzarlo: `exito=False`, `limite_alcanzado=True`.
4. Sin solución: `camino=[]`, `estados=[]`, `costo=None`, `profundidad=0`
   (se conserva `profundidad_maxima` alcanzada), sin excepción.

Tabla sobre `Prueba1.txt`:

```text
alg    exito  expandidos        generados        prof        prof_max           tiempo   costo
BFS    True   5251              6423             30          31                 0.11     30.0
UCS    True   9561              12335            38          40                 0.23     25.0
DFS    True   81                105              68          76                 0.00     58.0
```

UCS abarata el costo (25.0 vs 30.0) usando la avioneta; DFS da una
solución larga (68 pasos, costo 58.0), como es esperado.

Sin tocar (fuera de alcance): `greedy.py`, `astar.py`, `heuristics.py`,
`ui/`, `main.py`.

---

## 2026-11-02 — Ajuste del manejo de ciclos en los tres algoritmos

Se unificó la detección de ciclos en BFS, UCS y DFS y se ajustaron las
pruebas de optimalidad para usar mundos de pasillos estrechos, donde la
búsqueda es tratable.

Archivos modificados:

- `algorithms/bfs.py`, `algorithms/ucs.py`, `algorithms/dfs.py`: ajuste
  de la detección de ciclos y de los docstrings.
- `tests/test_algorithms.py`: `test_4` y `test_5` se rediseñaron con
  pasillos estrechos para que la búsqueda por rama sea tratable.
- `scripts/comparar_no_informada.py`: comparación sobre Prueba1.
- `docs/CONTEXTO_BUSQUEDA_NO_INFORMADA.md`, `README.md` y esta entrada:
  documentación actualizada.

Tabla sobre `Prueba1.txt`:

```text
alg    exito  expandidos        generados        prof        prof_max           tiempo   costo
BFS    True   5251              6423             30          31                 0.11     30.0
UCS    True   9561              12335            38          40                 0.21     25.0
DFS    True   81                105              68          76                 0.00     58.0
```

UCS abarata el costo (25.0 vs 30.0) usando la avioneta; DFS da una
solución larga (68 pasos, costo 58.0), como es esperado.

Sin tocar (fuera de alcance): `core/`, `ui/`, `main.py`, `greedy.py`,
`astar.py`, `heuristics.py`.

---

## 2026-11-02 — Interfaz gráfica (inicio, juego, resumen) y animación

Aplicación completa de escritorio con customtkinter (ventana principal) y
pygame (animación en proceso aparte). No se modificó `core/` ni
`algorithms/`.

Archivos creados:

- `ui/theme.py`: colores, fuentes, tamaños, bordes, `TAM_CELDA`,
  `ARCHIVOS_ASSETS`, `LIMITE_NODOS_DEFECTO`, velocidad de animación,
  tamaños de ventana y geometría pura (`celda_a_pixeles`,
  `ajustar_tam_celda`).
- `ui/textos.py`: todos los textos visibles y `t(clave, **kwargs)`.
- `ui/assets_loader.py`: carga RGBA, escalado `NEAREST` para 16/32 px,
  preprocesado del robot (floodfill desde 8 puntos, `thresh=38`, recorte,
  lienzo cuadrado, 128×128 LANCZOS) y caché en
  `ui/assets/generados/agrobot_128.png`; reemplazos si falta un asset.
- `ui/componentes.py`: botón primario/secundario/peligro, tarjeta,
  título, subtítulo, etiquetas, campo, selector segmentado, opción,
  separador, contenedor, imagen y fila clave-valor. Las pantallas no usan
  colores ni fuentes directas.
- `ui/sesion.py`: `SesionJuego` con ruta, mundo, tipo, algoritmo, límite,
  resultado y estado de búsqueda.
- `ui/board_view.py`: `TableroCanvas` con capas casilla/muro/cultivo/
  depósito/avioneta con sombra/robot, redibujado al cambiar tamaño y
  celdas múltiplo de 16.
- `ui/report_panel.py`: `construir_reporte` (costo solo para Costo
  uniforme/A*), `costo_paso`, `costos_acumulados` y `costo_total`.
- `ui/runner.py`: búsqueda en proceso `spawn`; `iniciar`, `consultar`,
  `cancelar`, `en_ejecucion` y `ultimo_error`.
- `ui/animator.py`: animación pygame en proceso `spawn` con HUD
  (paso, fertilizante, combustible, costo), sombra de avioneta, tratado
  de cultivos, reproducción automática y controles
  Espacio/←/→/↑/↓/R/Esc.
- `ui/app.py`: ventana principal, contenedor apilado y `ir_a`.
- `ui/screens/__init__.py`: registro `PANTALLAS`.
- `ui/screens/inicio.py`, `juego.py`, `resumen.py`: las tres pantallas.
- `ui/README_UI.md`: contrato de pantallas y guía para cambiar pantalla,
  asset, color, fuente, texto o algoritmo.
- `scripts/` ya existía; sin cambios en esta etapa.
- `tests/test_ui_logica.py` (nuevo, 9 pruebas): reporte por algoritmo,
  sin solución, límite alcanzado, costo por paso y acumulado, geometría,
  preprocesado del robot (128×128 RGBA, esquinas transparentes, centro
  opaco), `NEAREST` y registro de pantallas.

Archivos modificados:

- `main.py`: abre `AgroBotApp`; `if __name__ == "__main__"` y
  `multiprocessing.freeze_support()`.
- `requirements.txt`: se agregó `pillow`.
- `.gitignore`: se ignora `ui/assets/generados/` (caché del robot).
- `README.md`: cómo ejecutar (`python main.py`), arquitectura de procesos,
  controles de la animación y alcance actualizado.
- `docs/CAMBIOS.md`: esta entrada.

Resultado: `pytest -v` → **58 passed** (74.57 s).

Pruebas de humo realizadas:

- `python main.py` durante 7 s: el proceso quedó vivo, sin salida de error.
- Creación de la app y navegación inicio → juego → resumen → inicio sin
  excepciones.
- Flujo completo con Prueba1 y Amplitud: búsqueda en proceso hijo
  (5251 expandidos, 30 pasos), navegación automática a resumen y
  animación lanzada en otro proceso (viva tras 3 s).
- Vista previa del robot preprocesado revisada visualmente: fondo
  transparente y figura completa.

Supuestos y notas:

- Los archivos reales usan guion bajo (`0_casilla.png`, …) y el robot
  actual es RGBA de 1276×1268 (no 2048×2048 opaco); el preprocesado se
  aplicó igual y se verificó. Se mantiene el mapeo en `ARCHIVOS_ASSETS`.
- Al agotarse el combustible (`0`) no se dibuja avioneta: el robot sigue
  a pie. Solo se muestra la avioneta en su casilla con `-1` y bajo el
  robot con `1..30`.
- La geometría del tablero se ajusta al espacio y se redondea a múltiplos
  de 16; si el espacio es muy pequeño, baja a 16 px.
- No se pudieron probar de forma interactiva las teclas de la animación
  ni apreciar el resultado visual final en pantalla desde este entorno;
  sí se verificó que la ventana de pygame se abre y permanece viva.
- Sigue fuera de alcance: Avara, A* y heurísticas (visibles y
  deshabilitados con "próximamente").

---

## 2026-11-02 — Resumen de la búsqueda dentro de la animación

Se mantiene el flujo cálculo → pantalla de resumen → animación. La ventana
pygame ahora muestra, en su panel lateral derecho, el resumen de la
búsqueda arriba y el estado en vivo de la animación abajo.

Archivos modificados:

- `ui/report_panel.py`: nuevo `construir_reporte_completo(resultado,
  algoritmo, ruta_mundo)`, que reutiliza `construir_reporte` y agrega la
  fila "Mundo". Lo usan la pantalla de resumen y la animación.
- `ui/screens/resumen.py`: usa el reporte completo (sin duplicar la fila
  del mundo) y pasa las filas a `lanzar_animacion`.
- `ui/animator.py`: `ejecutar_animacion` y `lanzar_animacion` aceptan
  `resumen`; `_dibujar_hud` lo pinta arriba (título "Resumen de la
  búsqueda", filas clave-valor) y debajo el bloque en vivo existente.
  Alto mínimo de ventana según `theme.ALTO_MINIMO_ANIMACION`.
- `ui/theme.py`: `ANCHO_HUD_ANIMACION` pasa de 320 a 420 y se agrega
  `ALTO_MINIMO_ANIMACION = 700`.
- `ui/textos.py`: nuevas claves "Resumen de la búsqueda" y "Estado de la
  animación".
- `tests/test_ui_logica.py`: pruebas de `construir_reporte_completo`
  (incluye "Mundo"; sin ruta no lo agrega).
- `README.md` y `ui/README_UI.md`: documentación del nuevo panel.

Resultado: `pytest -v` → **60 passed** (68.42 s). Se revisó una captura
del HUD (900×700) y el resumen no se solapa con los datos en vivo ni con
los controles. Prueba de humo: animación lanzada con el resumen en un
proceso `spawn`, viva tras 4 s.

---

## 2026-11-02 — Fusionar Inicio con Juego (dos pantallas)

Se eliminó la pantalla de Inicio como pantalla independiente y su contenido
se integró en la pantalla principal (`JuegoScreen`). La aplicación ahora
arranca directamente en esa pantalla combinada; la ventana de animación y
la pantalla de Resumen se mantienen.

Archivos modificados:

- `ui/screens/juego.py`: nueva cabecera con el robot, título "AgroBot" y
  subtítulo; el tablero y el panel bajan a la fila siguiente. El botón
  inferior pasa de "Volver al inicio" a "Salir" (cierra la aplicación).
- `ui/screens/inicio.py` (eliminado): su contenido vive ahora en la
  cabecera de `JuegoScreen`.
- `ui/screens/__init__.py`: `PANTALLAS` queda con `"juego"` y `"resumen"`
  (se quita `InicioScreen`).
- `ui/app.py`: la aplicación inicia en `"juego"`; se elimina el tamaño de
  ventana de inicio.
- `ui/screens/resumen.py`: el botón "Inicio" navega ahora a `"juego"`
  (la pantalla principal combinada).
- `ui/theme.py`: se quitan `TAM_ROBOT_INICIO` y `TAM_VENTANA_INICIO`; se
  agrega `TAM_ROBOT_JUEGO = 84`.
- `ui/textos.py`: se retiran textos ya sin uso ("Comenzar" y "Volver al
  inicio"); se conservan título y subtítulo de portada.
- `ui/sesion.py`: docstring actualizado (pantalla principal y resumen).
- `tests/test_ui_logica.py`: el registro de pantallas ahora debe contener
  `{"juego", "resumen"}`.
- `README.md` y `ui/README_UI.md`: documentación del nuevo flujo de dos
  pantallas.

Resultado: `pytest -v` → **60 passed** (61.00 s). Se revisó una captura
de la pantalla combinada: cabecera con robot, título y subtítulo, tablero
y panel con "Salir" visibles, sin recortes. `python main.py` arrancó y
permaneció vivo 7 s sin errores; el flujo búsqueda → resumen → animación
siguió funcionando.

---

## 2026-11-02 — Quitar el botón "Inicio" del resumen

En `ui/screens/resumen.py` se eliminó el botón "Inicio" porque hacía lo
mismo que "Probar otro algoritmo" (volver a la pantalla principal). Las
acciones del resumen quedan en dos columnas: "Ver animación" / "Repetir
animación" y "Probar otro algoritmo". También se retiró la clave
`boton_inicio` de `ui/textos.py`.

Resultado: `pytest -v` → **60 passed**.

---

## 2026-11-02 — Animación primero y botón "Ver Resultados Detallados"

Nuevo flujo: al pulsar **Ejecutar**, la búsqueda calcula y se abre la
animación directamente; el reporte ya no aparece automáticamente.

- Al llegar al último paso, el HUD de pygame muestra el botón **"Ver
  Resultados Detallados"**.
- Al pulsarlo se cierra la animación y se navega a la pantalla de resumen.
- Si la animación se cierra antes de la meta, el mismo botón aparece en
  la pantalla principal.
- Si la búsqueda no tiene solución o alcanza el límite (no hay
  animación), el botón aparece de inmediato en la pantalla principal.
- La animación lanzada desde el resumen no muestra ese botón.

Archivos modificados:

- `ui/animator.py`: eventos `solicitud_resultados` y `terminada`,
  `solicita_resultados()`, `termino()`, botón dibujado en el HUD y
  detección de clic; parámetro `mostrar_boton`.
- `ui/screens/juego.py`: al terminar la búsqueda lanza la animación (no
  navega), vigila su estado con `after(...)`, muestra el botón de respaldo
  y navega al resumen solo al pulsarlo.
- `ui/screens/resumen.py`: se quitó el auto-lanzamiento de la animación;
  la animación desde el resumen no muestra el botón de resultados.
- `ui/textos.py`: "Ver Resultados Detallados" y mensajes de estado.
- `tests/test_ui_logica.py`: prueba de geometría del botón.
- `README.md` y `ui/README_UI.md`: flujo actualizado.

Resultado: `pytest -v` → **61 passed** (66.26 s). Pruebas de humo:
el reporte no se abrió automáticamente; al cerrar la animación antes de
la meta apareció el botón en la pantalla principal; al simular el clic
del botón del HUD se navegó al resumen; con un mundo sin solución el
botón apareció de inmediato sin abrir el reporte. Captura del HUD
revisada: el botón se dibuja sin solaparse con los controles.

---

## 2026-11-03 — Ciclos solo por rama (sin modo configurable)

Decisión: el proyecto evita ciclos únicamente por rama, revisando los
ancestros del nodo (incluido el padre), como define el profesor. Se
eliminó por completo el modo alternativo y el parámetro de modo de ciclos.
La clave de ciclo relajada se conserva para que el vaivén dentro de la
avioneta cuente como ciclo. No se tocó `core/` ni el conteo de nodos.

Archivos modificados:

- `algorithms/base.py`: se eliminaron la validación del modo de ciclos y
  la clave completa; se conservan `clave_relajada`, `crea_ciclo_en_rama`,
  `Resultado` y los constructores.
- `algorithms/bfs.py`, `algorithms/ucs.py`, `algorithms/dfs.py`: firmas
  `busqueda_*(problema, limite_nodos=None)`; se eliminaron los conjuntos
  de cerrados y las ramas del modo alternativo. Los tres usan siempre
  `crea_ciclo_en_rama` con clave relajada.
- `tests/test_algorithms.py`: se quitaron las pruebas del modo inválido y
  de comparación entre modos. `test_4` y `test_5` usan ahora un anillo de
  pasillos estrechos (robot (9,1), depósito (8,1), avioneta (8,2),
  cultivo (1,7)); BFS cuesta 14, UCS 9 y DFS 14. Todas las llamadas usan
  `limite_nodos=200_000` y las pruebas de solución afirman
  `exito=True` y `limite_alcanzado=False`.
- `scripts/comparar_no_informada.py`: solo BFS, UCS y DFS, sin columna de
  modo ni filas alternativas.
- `docs/CONTEXTO_BUSQUEDA_NO_INFORMADA.md`: pseudocódigos y secciones 4 a
  9 actualizados; nota sobre el descarte de los cerrados compartidos y
  limitación de crecimiento exponencial en mundos abiertos.
- `README.md`: sección de algoritmos sin parámetro de modo.
- `docs/CAMBIOS.md`: entradas históricas reescritas para no referenciar
  el modo eliminado; esta entrada nueva.

Resultado: `pytest -v` → **57 passed** (12.82 s), frente a los ~60 s
anteriores.

Tabla sobre `Prueba1.txt`:

```text
alg    exito  expandidos        generados        prof        prof_max           tiempo   costo
BFS    True   5251              6423             30          31                 0.14     30.0
UCS    True   9561              12335            38          40                 0.38     25.0
DFS    True   81                105              68          76                 0.00     58.0
```

Grep final: sin resultados para el parámetro de ciclos, la clave completa,
la validación del modo y las cadenas del modo eliminado. Solo quedan las
declaraciones de variables de módulo en `ui/runner.py` y `ui/animator.py`.

Sin tocar: `core/`, Avara, A*, heurísticas y diseño visual.

---

## 2026-11-07 — Confirmaciones del profesor sobre las convenciones de búsqueda

No se modificó código. Se actualizó la documentación del contexto para
reflejar las respuestas del profesor y separar lo confirmado de los
supuestos del equipo.

Archivos modificados:

- `docs/CONTEXTO_BUSQUEDA_NO_INFORMADA.md`:
  - Se marcaron como **confirmados por el profesor**: el nodo meta cuenta
    como expandido; los ciclos son solo por rama en BFS, UCS y DFS; el
    desempate de UCS por orden de creación y el orden de operadores
    arriba/abajo/izquierda/derecha; los mundos de prueba 10x10 y de
    pasillos en los casos de optimalidad; y el corte por `limite_nodos`
    con mensaje de "límite alcanzado".
  - Se mantienen como **supuestos del equipo** la clave de ciclo relajada
    (con su razonamiento de dominancia) y los supuestos 3 a 6 del core.
  - Se documentó la respuesta sobre el regreso al depósito con el
    fertilizante lleno: la implementación lo descarta porque el estado ya
    está en la rama, no pierde soluciones ni cambia el costo y evita
    bucles; el depósito de `Prueba1` es un callejón sin salida.
  - Se anotó, **sin confirmar**, que el vaivén dentro de la avioneta
    cuenta como ciclo por la clave relajada.
- `docs/CAMBIOS.md`: esta entrada.

Resultado: solo cambios de documentación; sin cambios en `core/`,
`algorithms/`, `ui/` ni pruebas.

---

## 2026-11-08 — Búsqueda informada: heurística B, Avara y A*

Se implementó la heurística B y los algoritmos informados, se habilitaron
en la UI y se agregó el borrador del informe. No se modificó `core/` ni
los algoritmos no informados.

Archivos creados/modificados:

- `algorithms/heuristics.py`: `HeuristicaAgroBot` con Manhattan + MST
  (Prim) y los cuatro casos de `L`; `h = 0.5 · L`, sin depender del
  combustible.
- `algorithms/greedy.py`: `busqueda_avara` con prioridad `h(n)`.
- `algorithms/astar.py`: `busqueda_a_estrella` con prioridad `g(n)+h(n)`.
  Ambos reutilizan `Resultado`, `crea_ciclo_en_rama`, la clave relajada,
  meta al extraer, conteo del meta y `limite_nodos`.
- `algorithms/__init__.py`: exporta la heurística y las dos búsquedas.
- `tests/test_heuristics.py`: casos de la heurística y verificación
  exhaustiva de admisibilidad.
- `tests/test_algorithms.py`: casos nuevos de A*/Avara, equivalencias con
  `h ≡ 0`, solución válida, sin solución, límite, meta en raíz y regresión
  de `Prueba1`.
- `scripts/comparar_algoritmos.py`: tabla de los cinco algoritmos.
- `ui/runner.py`: mapas de algoritmos informados/no informados; el proceso
  hijo construye `HeuristicaAgroBot`.
- `ui/screens/juego.py`: Avara y A* habilitados en "Informada".
- `ui/textos.py`, `ui/README_UI.md`, `README.md` y `tests/test_ui_logica.py`
  actualizados.
- `docs/informe/heuristica.md`: borrador para revisión del equipo.
- `docs/CONTEXTO_BUSQUEDA_NO_INFORMADA.md`: nota cruzada a la etapa
  informada.

Resultado: `pytest -v` → **72 passed** (15.59 s). La verificación
exhaustiva de admisibilidad tardó ~0.37 s, encontró **12 302 estados
alcanzables**, `h*(inicial)=25.0` y **0 violaciones**.

Salida real de `scripts/comparar_algoritmos.py`:

```text
alg    exito  expandidos        generados        prof        prof_max           tiempo   costo
BFS    True   5251              6423             30          31                 0.14     30.0
UCS    True   9561              12335            38          40                 0.28     25.0
DFS    True   81                105              68          76                 0.00     58.0
Avara  True   39                60               32          32                 0.00     32.0
A*     True   770               1036             40          40                 0.03     25.0
```

Prueba de humo con pantalla: A* (770 expandidos, costo 25.0) y Avara
(39 expandidos, costo 32.0) sobre `Prueba1`; en ambos casos el reporte no
se abrió automáticamente y el botón del HUD llevó al resumen.

Supuestos: se siguió la revisión de `limite_nodos` antes de extraer
(sección 3.1 y estructura de `ucs.py`); no se añadió detección anticipada
de mundos sin solución. No se hizo commit.
