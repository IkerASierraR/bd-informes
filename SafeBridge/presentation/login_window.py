"""
Ventana de login / conexión.
"""

import customtkinter as ctk
from tkinter import messagebox
from domain.models import ConnectionConfig, EngineType
from application.services.connection_service import ConnectionService
from infrastructure.security import save_connections, load_connections
from presentation.dashboard_window import DashboardWindow

DEFAULT_PORTS = {
    EngineType.MYSQL: "3306",
    EngineType.POSTGRESQL: "5432",
    EngineType.SQLSERVER: "1433",
    EngineType.ORACLE: "1521",
    EngineType.SQLITE: "",
}


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("SafeBridge - Login")
        self.root.geometry("520x650")
        self.root.resizable(False, False)

        # Logo y título
        self.logo_label = ctk.CTkLabel(root, text="SafeBridge", font=("Roboto", 32, "bold"))
        self.logo_label.pack(pady=(30, 10))

        self.subtitle = ctk.CTkLabel(root, text="Gestión profesional de backups", font=("Roboto", 14))
        self.subtitle.pack(pady=(0, 20))

        # Marco del formulario
        self.form = ctk.CTkFrame(root)
        self.form.pack(pady=10, padx=40, fill="both", expand=True)

        # Selector de motor
        ctk.CTkLabel(self.form, text="Motor de base de datos:").pack(anchor="w", pady=(10, 0))
        self.engine_var = ctk.StringVar(value=EngineType.MYSQL.value)
        self.engine_menu = ctk.CTkOptionMenu(self.form, values=[e.value for e in EngineType],
                                             variable=self.engine_var, command=self._on_engine_change)
        self.engine_menu.pack(fill="x", pady=5)

        # Campos
        self.fields = {}
        self._create_field("Host / IP", "host", "localhost")
        self._create_field("Puerto", "port", DEFAULT_PORTS[EngineType.MYSQL])
        
        # Frame para elementos dinámicos (TCP checkbox y Oracle fields)
        self.dynamic_frame = ctk.CTkFrame(self.form, fg_color="transparent")
        self.dynamic_frame.pack(fill="x", pady=0)
        
        # Checkbox TCP/IP (solo SQL Server)
        self.use_tcp_var = ctk.BooleanVar(value=False)
        self.use_tcp_check = ctk.CTkCheckBox(self.dynamic_frame, text="Usar conexión TCP/IP (solo SQL Server)", 
                                             variable=self.use_tcp_var)
        
        # Campo Oracle Service Name
        self.oracle_frame = ctk.CTkFrame(self.dynamic_frame, fg_color="transparent")
        self.service_label = ctk.CTkLabel(self.oracle_frame, text="Service Name (Oracle):")
        self.service_entry = ctk.CTkEntry(self.oracle_frame)
        
        self._create_field("Usuario", "user", "root")
        self._create_field("Contraseña", "password", "", show="*")

        # Checkbox guardar credenciales
        self.save_var = ctk.BooleanVar(value=False)
        self.save_check = ctk.CTkCheckBox(self.form, text="Guardar credenciales", variable=self.save_var)
        self.save_check.pack(pady=(15, 5), anchor="w")

        # Botones
        btn_frame = ctk.CTkFrame(self.form)
        btn_frame.pack(fill="x", pady=(10, 10))

        self.test_btn = ctk.CTkButton(btn_frame, text="Probar conexión", command=self._test_connection)
        self.test_btn.pack(side="left", expand=True, padx=5)

        self.connect_btn = ctk.CTkButton(btn_frame, text="Conectar", command=self._connect)
        self.connect_btn.pack(side="right", expand=True, padx=5)

        # Actualizar visibilidad según motor inicial
        self._update_dynamic_fields()
        
        # Cargar credenciales guardadas si existen
        self._load_saved_connections()

    def _create_field(self, label_text, key, default="", show=None):
        ctk.CTkLabel(self.form, text=f"{label_text}:").pack(anchor="w", pady=(5, 0))
        entry = ctk.CTkEntry(self.form, show=show)
        entry.pack(fill="x", pady=2)
        entry.insert(0, default)
        self.fields[key] = entry

    def _on_engine_change(self, engine_str):
        engine = EngineType(engine_str)
        port_entry = self.fields["port"]
        port_entry.delete(0, "end")
        port_entry.insert(0, DEFAULT_PORTS.get(engine, ""))
        self._update_dynamic_fields()

    def _update_dynamic_fields(self):
        """Muestra u oculta campos dinámicos según el motor seleccionado."""
        engine = EngineType(self.engine_var.get())
        
        # Limpiar frame dinámico
        for widget in self.dynamic_frame.winfo_children():
            widget.pack_forget()
        
        if engine == EngineType.SQLSERVER:
            # Mostrar solo checkbox TCP
            self.use_tcp_check.pack(anchor="w", pady=(5, 5))
            # Asegurar que el frame dinámico sea visible
            self.dynamic_frame.pack(fill="x", pady=0)
            
        elif engine == EngineType.ORACLE:
            # Mostrar campo Service Name
            self.oracle_frame.pack(fill="x", pady=0)
            self.service_label.pack(anchor="w", pady=(5, 0))
            self.service_entry.pack(fill="x", pady=(0, 5))
            # Asegurar que el frame dinámico sea visible
            self.dynamic_frame.pack(fill="x", pady=0)
            
        else:
            # MySQL, PostgreSQL, SQLite - ocultar completamente el frame dinámico
            self.dynamic_frame.pack_forget()

    def _get_config(self) -> ConnectionConfig:
        engine = EngineType(self.engine_var.get())
        port = self.fields["port"].get() or "0"
        service = self.service_entry.get() if engine == EngineType.ORACLE else ""
        config = ConnectionConfig(
            engine=engine,
            host=self.fields["host"].get(),
            port=int(port) if port.isdigit() else 0,
            user=self.fields["user"].get(),
            password=self.fields["password"].get(),
            service_name=service
        )
        if engine == EngineType.SQLSERVER:
            config.use_tcp = self.use_tcp_var.get()
        return config

    def _test_connection(self):
        config = self._get_config()
        result = ConnectionService.test_connection(config)
        messagebox.showinfo("Test de conexión", result)

    def _connect(self):
        config = self._get_config()
        # Guardar credenciales si se marcó
        if self.save_var.get():
            saved = load_connections()
            engine_str = config.engine.value
            # Buscar si ya existe una conexión con el mismo motor, host Y USUARIO
            found = False
            for conn in saved:
                if (conn.get("engine") == engine_str and 
                    conn.get("host") == config.host and 
                    conn.get("user") == config.user):  # ← Ahora también compara usuario
                    conn.update({
                        "port": config.port,
                        "password": config.password,
                        "service_name": config.service_name,
                    })
                    found = True
                    break
            if not found:
                saved.append({
                    "engine": engine_str,
                    "host": config.host,
                    "port": config.port,
                    "user": config.user,
                    "password": config.password,
                    "service_name": config.service_name,
                })
            save_connections(saved)

        # Abrir dashboard
        self.root.withdraw()
        dash = ctk.CTkToplevel()
        dash.protocol("WM_DELETE_WINDOW", lambda: self._on_close_dashboard(dash))
        DashboardWindow(dash, config, login_window=self)

    def _on_close_dashboard(self, dash):
        dash.destroy()
        self.root.deiconify()

    def _load_saved_connections(self):
        saved = load_connections()
        if not saved:
            return
        # Cargar la primera conexión guardada
        first = saved[0]
        self.engine_var.set(first["engine"])
        self._on_engine_change(first["engine"])
        self.fields["host"].delete(0, "end")
        self.fields["host"].insert(0, first["host"])
        self.fields["port"].delete(0, "end")
        self.fields["port"].insert(0, str(first["port"]))
        self.fields["user"].delete(0, "end")
        self.fields["user"].insert(0, first["user"])
        self.fields["password"].delete(0, "end")
        self.fields["password"].insert(0, first.get("password", ""))
        if first.get("service_name"):
            self.service_entry.delete(0, "end")
            self.service_entry.insert(0, first["service_name"])