"""Punto de entrada de AgroBot."""

from __future__ import annotations

import multiprocessing


def main() -> None:
    """Abre la ventana principal de la aplicación."""
    multiprocessing.freeze_support()
    from ui.app import AgroBotApp

    app = AgroBotApp()
    app.mainloop()


if __name__ == "__main__":
    main()
