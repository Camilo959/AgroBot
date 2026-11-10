"""Mundo del AgroBot: lectura y validación del mapa desde archivo de texto.

Supuestos de diseño:
    1. El movimiento que llega a la casilla de la avioneta cuesta 1 (el costo
       se determina por el combustible ANTES de moverse).
    5. Las casillas 2, 3, 4 y 5 son transitables. Una vez leído el mundo, la
       casilla del robot (2) cuenta como libre.
"""

from __future__ import annotations


class World:
    """Representa la cuadrícula estática del problema.

    Atributos:
        filas: número de filas de la matriz.
        columnas: número de columnas de la matriz.
        matriz: lista de listas con los valores originales 0-5.
        muros: frozenset de (fila, columna) con las casillas de valor 1.
        inicio: tupla (fila, columna) de la casilla del robot (valor 2).
        deposito: tupla (fila, columna) del depósito de fertilizante (valor 4).
        avioneta: tupla (fila, columna) de la avioneta (valor 5).
        cultivos: frozenset de (fila, columna) con los cultivos secos (valor 3).
    """

    # Dimensiones esperadas de la cuadrícula. Se definen como constantes para
    # no hardcodear el 10 en la lógica de validación.
    FILAS_ESPERADAS: int = 10
    COLUMNAS_ESPERADAS: int = 10
    VALORES_VALIDOS: frozenset[int] = frozenset({0, 1, 2, 3, 4, 5})

    def __init__(
        self,
        matriz: list[list[int]],
        muros: frozenset[tuple[int, int]],
        inicio: tuple[int, int],
        deposito: tuple[int, int],
        avioneta: tuple[int, int],
        cultivos: frozenset[tuple[int, int]],
    ) -> None:
        """Crea un mundo a partir de componentes ya validados."""
        self.filas: int = len(matriz)
        self.columnas: int = len(matriz[0]) if matriz else 0
        self.matriz: list[list[int]] = matriz
        self.muros: frozenset[tuple[int, int]] = muros
        self.inicio: tuple[int, int] = inicio
        self.deposito: tuple[int, int] = deposito
        self.avioneta: tuple[int, int] = avioneta
        self.cultivos: frozenset[tuple[int, int]] = cultivos

    @classmethod
    def desde_archivo(cls, ruta: str) -> World:
        """Lee y valida un archivo de mundo.

        Args:
            ruta: ruta al archivo de texto con 10 filas de 10 enteros
                separados por espacios.

        Returns:
            El mundo validado.

        Raises:
            FileNotFoundError: si el archivo no existe.
            ValueError: si el contenido no cumple el formato (dimensiones,
                valores 0-5, exactamente un 2, un 4 y un 5).
        """
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                lineas = [linea.strip() for linea in f if linea.strip() != ""]
        except FileNotFoundError:
            raise FileNotFoundError(f"No se encontró el archivo del mundo: {ruta}")
        except OSError as error:
            raise OSError(
                f"No se pudo leer el archivo del mundo '{ruta}': {error}"
            ) from error

        if len(lineas) != cls.FILAS_ESPERADAS:
            raise ValueError(
                f"El mundo debe tener {cls.FILAS_ESPERADAS} filas, "
                f"se encontraron {len(lineas)} en '{ruta}'."
            )

        matriz: list[list[int]] = []
        for i, linea in enumerate(lineas):
            partes = linea.split()
            if len(partes) != cls.COLUMNAS_ESPERADAS:
                raise ValueError(
                    f"Fila {i}: se esperaban {cls.COLUMNAS_ESPERADAS} columnas, "
                    f"se encontraron {len(partes)}."
                )
            fila: list[int] = []
            for j, token in enumerate(partes):
                try:
                    valor = int(token)
                except ValueError:
                    raise ValueError(
                        f"Casilla ({i}, {j}): '{token}' no es un entero válido."
                    )
                if valor not in cls.VALORES_VALIDOS:
                    raise ValueError(
                        f"Casilla ({i}, {j}): valor {valor} inválido, "
                        "solo se permiten valores 0-5."
                    )
                fila.append(valor)
            matriz.append(fila)

        muros: set[tuple[int, int]] = set()
        cultivos: set[tuple[int, int]] = set()
        inicios: list[tuple[int, int]] = []
        depositos: list[tuple[int, int]] = []
        avionetas: list[tuple[int, int]] = []

        for r in range(len(matriz)):
            for c in range(len(matriz[r])):
                valor = matriz[r][c]
                if valor == 1:
                    muros.add((r, c))
                elif valor == 2:
                    inicios.append((r, c))
                elif valor == 3:
                    cultivos.add((r, c))
                elif valor == 4:
                    depositos.append((r, c))
                elif valor == 5:
                    avionetas.append((r, c))

        if len(inicios) != 1:
            raise ValueError(
                f"El mundo debe tener exactamente un robot (2), "
                f"se encontraron {len(inicios)}."
            )
        if len(depositos) != 1:
            raise ValueError(
                f"El mundo debe tener exactamente un depósito (4), "
                f"se encontraron {len(depositos)}."
            )
        if len(avionetas) != 1:
            raise ValueError(
                f"El mundo debe tener exactamente una avioneta (5), "
                f"se encontraron {len(avionetas)}."
            )

        return cls(
            matriz=matriz,
            muros=frozenset(muros),
            inicio=inicios[0],
            deposito=depositos[0],
            avioneta=avionetas[0],
            cultivos=frozenset(cultivos),
        )

    def es_libre(self, r: int, c: int) -> bool:
        """Indica si la casilla (r, c) está dentro del rango y no es muro.

        Las casillas con valores 2, 3, 4 y 5 se consideran transitables;
        solo el valor 1 (muro) bloquea el paso.
        """
        if not (0 <= r < self.filas and 0 <= c < self.columnas):
            return False
        return (r, c) not in self.muros

    def __str__(self) -> str:
        """Devuelve el mundo como texto con filas de enteros separados por espacios."""
        return "\n".join(" ".join(str(v) for v in fila) for fila in self.matriz)
