"""
Widget de terminal integrado (salida en tiempo real).
"""

import customtkinter as ctk


class TerminalWidget(ctk.CTkTextbox):
    def __init__(self, master, **kwargs):
        super().__init__(master, wrap="word", state="disabled", font=("Consolas", 11), **kwargs)

    def write(self, text: str, tag: str = None):
        self.configure(state="normal")
        if tag:
            self.insert("end", text + "\n", tag)
        else:
            self.insert("end", text + "\n")
        self.see("end")
        self.configure(state="disabled")

    def clear(self):
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.configure(state="disabled")