"""
Ventana de ajustes: historial, conexiones guardadas, sistema.
"""

import customtkinter as ctk
import os
from datetime import datetime
from infrastructure.security import load_connections, save_connections
from domain.models import EngineType


class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, master, current_config, logger):
        super().__init__(master)
        self.current_config = current_config
        self.logger = logger
        self.title("Ajustes - SafeBridge")
        self.geometry("750x550")
        self.minsize(600, 400)
        
        # ===== HACER QUE APAREZCA AL FRENTE =====
        self.lift()                    # Elevar la ventana
        self.focus_force()             # Forzar el foco
        self.grab_set()                # Hacerla modal (bloquea la ventana principal)
        self.transient(master)         # Hacerla hija de la ventana principal
        
        # Centrar en la pantalla
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() - 750) // 2
        y = master.winfo_y() + (master.winfo_height() - 550) // 2
        self.geometry(f"+{x}+{y}")
        
        # Cerrar con Escape
        self.bind("<Escape>", lambda e: self.destroy())
        
        # Asegurar que se cierre correctamente
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Pestañas
        self.tabview = ctk.CTkTabview(self, width=720, height=500)
        self.tabview.pack(padx=10, pady=10, fill="both", expand=True)

        self.tabview.add("Historial")
        self.tabview.add("Conexiones guardadas")
        self.tabview.add("Sistema")

        self._build_history_tab()
        self._build_connections_tab()
        self._build_system_tab()
    
    def _on_close(self):
        """Liberar el grab antes de cerrar."""
        self.grab_release()
        self.destroy()

    def _build_history_tab(self):
        tab = self.tabview.tab("Historial")
        frame = ctk.CTkFrame(tab)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Texto con logs de hoy
        log_file = os.path.join("logs", f"safebridge_{datetime.now().strftime('%Y%m%d')}.log")
        text = ctk.CTkTextbox(frame, wrap="word")
        text.pack(fill="both", expand=True)
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as f:
                content = f.read()
            text.insert("1.0", content)
        else:
            text.insert("1.0", "No hay registros para hoy.")
        text.configure(state="disabled")

    def _build_connections_tab(self):
        tab = self.tabview.tab("Conexiones guardadas")
        frame = ctk.CTkFrame(tab)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.connections_listbox = ctk.CTkTextbox(frame, height=200)
        self.connections_listbox.pack(fill="x", pady=5)
        self._refresh_connections_display()

        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(fill="x", pady=5)
        ctk.CTkButton(btn_frame, text="Eliminar seleccionada", command=self._delete_selected_connection).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Limpiar todas", command=self._clear_all_connections).pack(side="left", padx=5)

    def _refresh_connections_display(self):
        self.connections_listbox.configure(state="normal")
        self.connections_listbox.delete("1.0", "end")
        conns = load_connections()
        for i, c in enumerate(conns):
            self.connections_listbox.insert("end", f"{i+1}. {c['engine']} - {c['host']}:{c['port']} ({c['user']})\n")
        self.connections_listbox.configure(state="disabled")

    def _delete_selected_connection(self):
        """Elimina la conexión seleccionada (implementación básica)."""
        conns = load_connections()
        # Obtener la línea actual del cursor
        cursor_pos = self.connections_listbox.index("insert")
        line_num = int(cursor_pos.split('.')[0]) - 1
        
        if 0 <= line_num < len(conns):
            del conns[line_num]
            save_connections(conns)
            self._refresh_connections_display()

    def _clear_all_connections(self):
        save_connections([])
        self._refresh_connections_display()

    def _build_system_tab(self):
        tab = self.tabview.tab("Sistema")
        frame = ctk.CTkFrame(tab)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        backup_dir = "backups"
        num_backups = len([f for f in os.listdir(backup_dir) if os.path.isfile(os.path.join(backup_dir, f))]) if os.path.exists(backup_dir) else 0
        info = [
            f"Directorio de backups: {os.path.abspath(backup_dir)}",
            f"Número de backups almacenados: {num_backups}",
            f"Conexión activa: {self.current_config.engine.value} - {self.current_config.host}:{self.current_config.port}",
        ]
        for line in info:
            ctk.CTkLabel(frame, text=line, font=("Roboto", 12)).pack(anchor="w", pady=2)