"""Textos visibles de la interfaz del AgroBot.

Ningún texto visible debe escribirse directamente en las pantallas: todo
sale de este diccionario para facilitar cambios de redacción o idioma.
"""

from __future__ import annotations

TEXTOS: dict[str, str] = {
    # Aplicación
    "app_titulo": "AgroBot",
    "app_subtitulo": "Riego inteligente para tu granja",
    # Inicio
    "inicio_titulo": "AgroBot",
    "inicio_subtitulo": (
        "Un agente que recorre la granja para fertilizar todos los cultivos secos."
    ),
    "boton_salir": "Salir",
    # Juego
    "juego_titulo": "Planificar la misión",
    "boton_cargar_mundo": "Cargar mundo",
    "archivo_sin_cargar": "Ningún mundo cargado",
    "archivo_cargado": "Mundo: {nombre}",
    "filtro_mundos": "Mundos",
    "filtro_todos": "Todos los archivos",
    "tipo_busqueda": "Tipo de búsqueda",
    "tipo_no_informada": "No informada",
    "tipo_informada": "Informada",
    "algoritmo": "Algoritmo",
    "limite_nodos": "Límite de nodos",
    "limite_ayuda": "Avanzado: corta la búsqueda si crece demasiado.",
    "boton_ejecutar": "Ejecutar",
    "boton_cancelar": "Cancelar",
    "estado_inactivo": "Elige un mundo y un algoritmo.",
    "estado_buscando": "Buscando...",
    "estado_cancelado": "Búsqueda cancelada.",
    "estado_mundo_cargado": "Mundo cargado. Elige un algoritmo.",
    "estado_error": "Error: {mensaje}",
    "error_limite": "El límite de nodos debe ser un entero positivo.",
    "error_sin_algoritmo": "Selecciona un algoritmo válido.",
    "error_sin_mundo": "Primero carga un mundo.",
    "error_busqueda": "La búsqueda terminó inesperadamente.",
    # Algoritmos
    "alg_amplitud": "Amplitud",
    "alg_costo_uniforme": "Costo uniforme",
    "alg_profundidad": "Profundidad evitando ciclos",
    "alg_avara": "Avara",
    "alg_astar": "A*",
    # Resumen
    "resumen_titulo": "Resumen de la búsqueda",
    "resumen_exito": "¡Solución encontrada!",
    "resumen_sin_solucion": "Sin solución",
    "resumen_sin_solucion_detalle": (
        "No existe un camino que trate todos los cultivos secos con estas reglas."
    ),
    "resumen_limite": "Se alcanzó el límite de nodos",
    "resumen_limite_detalle": (
        "La búsqueda se detuvo antes de terminar. Prueba subir el límite de nodos."
    ),
    "resumen_sin_resultado": "Todavía no hay resultados.",
    "boton_animacion": "Ver animación",
    "boton_repetir_animacion": "Repetir animación",
    "boton_otro_algoritmo": "Probar otro algoritmo",
    "boton_resultados": "Ver Resultados Detallados",
    "estado_animando": (
        "Animación en curso. Al terminar podrás ver los resultados detallados."
    ),
    "estado_animacion_cerrada": (
        "Animación cerrada. Puedes ver los resultados detallados."
    ),
    "estado_sin_animacion": (
        "Búsqueda terminada. Puedes ver los resultados detallados."
    ),
    # Reporte
    "reporte_algoritmo": "Algoritmo",
    "reporte_estado": "Estado",
    "reporte_expandidos": "Nodos expandidos",
    "reporte_generados": "Nodos generados",
    "reporte_profundidad": "Profundidad máxima del árbol",
    "reporte_profundidad_solucion": "Profundidad de la solución",
    "reporte_tiempo": "Tiempo de cómputo",
    "reporte_costo": "Costo de la solución",
    "reporte_mundo": "Mundo",
    "reporte_exito": "Solución encontrada",
    "reporte_limite": "Límite alcanzado",
    "reporte_sin_solucion": "Sin solución",
    # Resumen detallado
    "detalle_busqueda_titulo": "Detalle de la búsqueda",
    "detalle_solucion_titulo": "Detalle de la solución",
    "detalle_solucion_no_disponible": "No disponible",
    "detalle_tipo_busqueda": "Tipo de búsqueda",
    "detalle_nodos_segundo": "Nodos por segundo",
    "detalle_limite_usado": "Límite de nodos",
    "detalle_pasos_costo_uno": "Pasos con costo 1.0",
    "detalle_pasos_costo_media": "Pasos con costo 0.5",
    "detalle_costo_pasos_uno": "Costo de pasos 1.0",
    "detalle_costo_pasos_media": "Costo de pasos 0.5",
    "detalle_cultivos_tratados": "Cultivos tratados",
    "detalle_posicion_final": "Posición final",
    "detalle_fertilizante_final": "Fertilizante final",
    "detalle_combustible_final": "Combustible final",
    "detalle_combustible_sin_abordar": "sin abordar",
    "detalle_combustible_agotada": "agotada",
    # Animación
    "anim_titulo": "AgroBot — {algoritmo}",
    "anim_resumen": "Resumen de la búsqueda",
    "anim_en_vivo": "Estado de la animación",
    "anim_paso": "Paso {actual} / {total}",
    "anim_fertilizante": "Fertilizante",
    "anim_combustible": "Combustible",
    "anim_costo": "Costo acumulado",
    "anim_sin_abordar": "sin abordar",
    "anim_agotada": "agotada",
    "anim_meta": "Meta alcanzada",
    "anim_costo_total": "Costo total: {costo}",
    "anim_velocidad": "x{valor}",
    "anim_pausa": "En pausa",
    "anim_controles": (
        "Espacio: pausa   izquierda/derecha: paso   arriba/abajo: velocidad   R: reiniciar   Esc: cerrar"
    ),
}


def t(clave: str, **kwargs: object) -> str:
    """Devuelve el texto de `clave`, formateado con los argumentos dados."""
    texto = TEXTOS.get(clave, clave)
    if kwargs:
        return texto.format(**kwargs)
    return texto
