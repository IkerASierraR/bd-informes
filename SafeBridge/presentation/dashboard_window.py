"""
Panel principal después de la conexión.
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from datetime import datetime
import os
import threading

from domain.models import ConnectionConfig
from application.services.connection_service import ConnectionService
from application.services.backup_service import BackupProcess
from infrastructure.logger import SafeBridgeLogger
from presentation.terminal_widget import TerminalWidget
from presentation.settings_window import SettingsWindow


class DashboardWindow:
    def __init__(self, master, config: ConnectionConfig, login_window=None):
        self.master = master
        self.config = config
        self.login_window = login_window  # Referencia a la ventana de login
        self.master.title("SafeBridge - Panel Principal")
        self.master.geometry("1000x700")
        self.master.minsize(800, 600)

        # Logger con callback a terminal
        self.terminal = None
        self.logger = SafeBridgeLogger(terminal_callback=self._log_to_terminal)

        # Obtener listado de bases de datos
        self.databases = []
        try:
            self.databases = ConnectionService.get_databases_list(config)
        except Exception as e:
            self.logger.error(f"No se pudo cargar la lista de bases de datos: {e}")

        self._build_ui()
        self.logger.info(f"Conectado a {config.engine.value} en {config.host}:{config.port}")
        
        # Cuando se cierra la ventana con la X, hacer logout
        self.master.protocol("WM_DELETE_WINDOW", self._logout)

    def _build_ui(self):
        # Barra superior
        top_bar = ctk.CTkFrame(self.master, height=50)
        top_bar.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(top_bar, text="SafeBridge", font=("Roboto", 18, "bold")).pack(side="left", padx=10)
        info_text = f"{self.config.engine.value} | {self.config.host}"
        ctk.CTkLabel(top_bar, text=info_text, font=("Roboto", 12)).pack(side="left", padx=20)

        # Botón CERRAR SESIÓN (rojo, a la derecha)
        self.logout_btn = ctk.CTkButton(
            top_bar, 
            text="Cerrar sesión", 
            width=100,
            fg_color="#8B0000",
            hover_color="#A00000",
            command=self._logout
        )
        self.logout_btn.pack(side="right", padx=10)

        # Botón ajustes
        self.settings_btn = ctk.CTkButton(top_bar, text="Ajustes", width=80,
                                         command=self._open_settings)
        self.settings_btn.pack(side="right", padx=10)

        # Sección central
        center_frame = ctk.CTkFrame(self.master)
        center_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Panel izquierdo (configuración backup)
        left_panel = ctk.CTkFrame(center_frame, width=300)
        left_panel.pack(side="left", fill="y", padx=(0, 10))

        ctk.CTkLabel(left_panel, text="Base de datos", font=("Roboto", 14, "bold")).pack(anchor="w", pady=(10, 0))
        self.db_var = ctk.StringVar(value="")
        if self.databases:
            self.db_menu = ctk.CTkOptionMenu(left_panel, values=self.databases, variable=self.db_var)
            self.db_menu.pack(fill="x", pady=5)
        else:
            ctk.CTkLabel(left_panel, text="No se encontraron bases de datos", text_color="red").pack()

        ctk.CTkLabel(left_panel, text="Carpeta destino", font=("Roboto", 14, "bold")).pack(anchor="w", pady=(15, 0))
        folder_frame = ctk.CTkFrame(left_panel)
        folder_frame.pack(fill="x", pady=5)
        self.folder_path = ctk.StringVar(value=os.path.abspath("backups"))
        self.folder_entry = ctk.CTkEntry(folder_frame, textvariable=self.folder_path)
        self.folder_entry.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(folder_frame, text="...", width=30, command=self._select_folder).pack(side="right", padx=(5, 0))

        self.backup_btn = ctk.CTkButton(left_panel, text="Generar Backup", command=self._start_backup)
        self.backup_btn.pack(fill="x", pady=(20, 10))

        # Terminal / log viewer
        right_panel = ctk.CTkFrame(center_frame)
        right_panel.pack(side="right", fill="both", expand=True)

        ctk.CTkLabel(right_panel, text="Consola de salida", font=("Roboto", 14, "bold")).pack(anchor="w", pady=(10, 0))
        self.terminal = TerminalWidget(right_panel)
        self.terminal.pack(fill="both", expand=True, pady=5)

    def _select_folder(self):
        path = filedialog.askdirectory(initialdir=self.folder_path.get())
        if path:
            self.folder_path.set(path)

    def _start_backup(self):
        db = self.db_var.get()
        if not db:
            messagebox.showerror("Error", "Seleccione una base de datos")
            return
        output_dir = self.folder_path.get()
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{db}_{timestamp}.sql"
        output_path = os.path.join(output_dir, filename)
        self.terminal.clear()
        self.logger.info(f"Iniciando proceso de backup para {db}")

        self.backup_btn.configure(state="disabled")
        process = BackupProcess(self.config, db, output_path, self.logger)
        process.start()
        self._monitor_process(process)

    def _monitor_process(self, process):
        """Revisa la cola del hilo y actualiza la interfaz."""
        try:
            msg_type, msg_text = process.queue.get_nowait()
            if msg_type == "success":
                messagebox.showinfo("Backup completado", msg_text)
            else:
                messagebox.showerror("Error", msg_text)
            self.backup_btn.configure(state="normal")
        except:
            self.master.after(100, self._monitor_process, process)

    def _log_to_terminal(self, text):
        if self.terminal:
            self.terminal.write(text)

    def _open_settings(self):
        SettingsWindow(self.master, self.config, self.logger)

    def _logout(self):
        """Cierra la sesión actual y vuelve al login."""
        # Si hay backup en progreso, preguntar
        if self.backup_btn.cget("state") == "disabled":
            respuesta = messagebox.askyesno(
                "Backup en progreso", 
                "Hay un backup en ejecución. ¿Seguro que quieres cerrar sesión?"
            )
            if not respuesta:
                return
        
        # Cerrar esta ventana
        self.master.destroy()
        
        # Mostrar el login nuevamente
        if self.login_window:
            self.login_window.root.deiconify()
            self.login_window.root.lift()
            self.login_window.root.focus_force()