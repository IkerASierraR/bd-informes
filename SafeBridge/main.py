"""
SafeBridge - Sistema de gestión de backups de bases de datos.
Punto de entrada principal.
"""

import os
import sys
import customtkinter as ctk

from presentation.login_window import LoginWindow


def main():
    # Configuración visual global
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Crear directorios necesarios
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for folder in ["logs", "backups"]:
        os.makedirs(os.path.join(base_dir, folder), exist_ok=True)

    # Directorio de configuración en el home del usuario
    config_dir = os.path.expanduser("~/.safebridge")
    os.makedirs(config_dir, exist_ok=True)

    root = ctk.CTk()
    root.title("SafeBridge - Login")
    root.geometry("520x600")
    root.resizable(False, False)

    app = LoginWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()