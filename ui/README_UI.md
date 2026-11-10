# Guía de la interfaz de AgroBot

Documento corto para modificar la UI sin tocar el core ni los algoritmos.

## Estructura

| Archivo | Responsabilidad |
|---|---|
| `theme.py` | **Todo** lo visual: colores, fuentes, tamaños, bordes, `TAM_CELDA`, `ARCHIVOS_ASSETS`, velocidades y tamaños de ventana. |
| `textos.py` | Todos los textos visibles. |
| `assets_loader.py` | Carga, escalado (`NEAREST`) y preprocesado del robot (LANCZOS + caché). |
| `componentes.py` | Botones, tarjetas, títulos, etiquetas, campos, selector y filas clave-valor ya estilizados. |
| `sesion.py` | `SesionJuego`, estado compartido entre pantallas. |
| `board_view.py` | Tablero estático en un `Canvas` de tkinter. |
| `animator.py` | Animación pygame ejecutada en otro proceso; el panel lateral muestra el resumen de la búsqueda arriba y el estado en vivo abajo. |
| `report_panel.py` | Lógica pura del reporte y del costo por paso. |
| `runner.py` | Búsqueda en proceso hijo y cancelación. |
| `app.py` | Ventana principal y gestor de pantallas. |
| `screens/` | Una pantalla por archivo + registro `PANTALLAS`. |

## Contrato de una pantalla

```python
class MiPantalla(ctk.CTkFrame):
    def __init__(self, master, app): ...
    def al_mostrar(self): ...
```

- `__init__(self, master, app)` construye los widgets.
- `al_mostrar(self)` se llama **cada vez** que se navega a la pantalla;
  ahí se sincroniza la vista con `app.sesion`.
- La pantalla lee y escribe únicamente en `app.sesion` y navega con
  `app.ir_a("juego" | "resumen")`.
- Las pantallas usan solo widgets de `componentes.py`; no usan colores ni
  fuentes directas.
- La portada (título, subtítulo y robot) vive dentro de `JuegoScreen`, que
  es la pantalla inicial de la aplicación.

## Cómo cambiar una pantalla

1. Crear una clase con el contrato anterior, por ejemplo
   `screens/mi_juego.py`.
2. Importarla en `screens/__init__.py`.
3. Cambiar una línea del registro:

```python
PANTALLAS = {
    "juego": MiJuegoScreen,   # antes JuegoScreen
    "resumen": ResumenScreen,
}
```

No hace falta tocar `app.py`.

## Cómo cambiar un asset

1. Reemplazar el archivo en `ui/assets/` manteniendo el nombre, o
2. editar `ARCHIVOS_ASSETS` en `theme.py`:

```python
ARCHIVOS_ASSETS = {
    "casilla": "0_casilla.png",
    ...
}
```

- Los sprites de 16 px y 32 px se escalan con `Image.NEAREST` a
  `TAM_CELDA` (múltiplo de 16, por defecto 48).
- El robot se preprocesa una vez y se cachea en
  `ui/assets/generados/agrobot_128.png` (ignorado por git). Para forzar
  el recálculo, borrar ese archivo.
- Si falta un asset, se dibuja un color de reemplazo
  (`COLORES_REEMPLAZO`), sin romper la aplicación.

## Cómo cambiar un color, fuente o tamaño

Editar `ui/theme.py`. Por ejemplo:

```python
COLOR_ACCION = "#84c669"
TAM_CELDA = 48
FAMILIA_FUENTE = "Trebuchet MS"
```

Si existe un `.ttf` en `ui/assets/fuentes/`, se usa su nombre como
familia (tanto en tkinter como en pygame); si no, se usa una fuente del
sistema.

## Cómo cambiar un texto

Editar la clave correspondiente en `ui/textos.py`. Los textos con
parámetros usan `{nombre}` y se leen con `textos.t("clave", nombre=...)`.

## Añadir una opción de algoritmo

1. Implementar la función en `algoritmos/`.
2. Registrar el identificador en `runner.ALGORITMOS_NO_INFORMADOS` o
   `runner.ALGORITMOS_INFORMADOS` según corresponda; `runner.ALGORITMOS`
   es la unión que usa la UI.
3. Añadir su etiqueta en `textos.py` y en la lista de
   `screens/juego.py` (`ALGORITMOS_NO_INFORMADA` o
   `ALGORITMOS_INFORMADA`).
4. Si reporta costo, incluirlo en
   `report_panel.ALGORITMOS_CON_COSTO`.

Avara y A* ya están habilitados; el proceso hijo construye
`HeuristicaAgroBot(world)` y no se pasa la heurística entre procesos.

## Resumen dentro de la animación

La ventana pygame recibe las mismas filas del reporte que la pantalla de
resumen:

- `report_panel.construir_reporte_completo(resultado, algoritmo, ruta)`
  genera las filas (incluida "Mundo").
- `juego._lanzar_animacion` (tras **Ejecutar**) las pasa a
  `animator.lanzar_animacion(ruta, estados, titulo, resumen)`.
- `animator._dibujar_hud` pinta el resumen arriba y el estado en vivo
  abajo. El ancho del panel y el alto mínimo están en `theme.py`
  (`ANCHO_HUD_ANIMACION`, `ALTO_MINIMO_ANIMACION`).

## Flujo animación → resultados

1. Al terminar la búsqueda con solución se abre la animación; el reporte
   no se muestra automáticamente.
2. Al llegar al último paso aparece el botón "Ver Resultados Detallados"
   en el HUD. Al pulsarlo se cierra la animación y se abre el resumen.
3. Si la animación se cierra antes, el botón aparece en la pantalla
   principal. También aparece ahí de inmediato si no hay solución o se
   alcanzó el límite.
4. La animación lanzada desde el resumen ("Ver animación / Repetir
   animación") no muestra ese botón: el reporte ya está abierto.

## Resumen detallado

La pantalla `Resumen` no usa el reporte compacto del HUD. Se organiza en
dos columnas con `report_panel.construir_detalle_busqueda` y
`report_panel.construir_detalle_solucion`:

- **Búsqueda:** algoritmo, tipo, estado, expandidos, generados,
  profundidad máxima, tiempo, nodos por segundo y límite.
- **Solución:** profundidad de la solución, cultivos tratados, pasos con
  costo 1.0 y 0.5, posición final, fertilizante final y combustible final.

El costo total y el costo desglosado por tipo de paso se muestran solo
para Costo uniforme y A*. El HUD de la animación conserva el reporte
compacto de `construir_reporte_completo`.

## Notas

- La búsqueda y la animación corren en procesos `spawn`; las funciones
  objetivo (`_ejecutar_busqueda`, `ejecutar_animacion`) están a nivel de
  módulo.
- `main.py` usa `if __name__ == "__main__"` y `freeze_support()`.
- La ventana principal no importa pygame: solo lo hace el proceso de
  animación.
