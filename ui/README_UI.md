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
| `animator.py` | Animación pygame ejecutada en otro proceso. |
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
  `app.ir_a("inicio" | "juego" | "resumen")`.
- Las pantallas usan solo widgets de `componentes.py`; no usan colores ni
  fuentes directas.

## Cómo cambiar una pantalla

1. Crear una clase con el contrato anterior, por ejemplo
   `screens/mi_juego.py`.
2. Importarla en `screens/__init__.py`.
3. Cambiar una línea del registro:

```python
PANTALLAS = {
    "inicio": InicioScreen,
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

1. Implementar la función en `algorithms/`.
2. Registrar el identificador en `runner.ALGORITMOS`.
3. Añadir su etiqueta en `textos.py` y en la lista de
   `screens/juego.py`.
4. Si reporta costo, incluirlo en
   `report_panel.ALGORITMOS_CON_COSTO`.

## Notas

- La búsqueda y la animación corren en procesos `spawn`; las funciones
  objetivo (`_ejecutar_busqueda`, `ejecutar_animacion`) están a nivel de
  módulo.
- `main.py` usa `if __name__ == "__main__"` y `freeze_support()`.
- La ventana principal no importa pygame: solo lo hace el proceso de
  animación.
