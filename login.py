import ctypes
import os
import sys
import tkinter as tk
import crypto

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

if getattr(sys, 'frozen', False):
    _RESOURCE_DIR = sys._MEIPASS
else:
    _RESOURCE_DIR = os.path.dirname(os.path.abspath(__file__))

# Paleta (mesma do app)
BG = "#0f0f14"
SURFACE = "#16161e"
BORDER = "#2a2a3a"
TEXT = "#e2e4f0"
TEXT_DIM = "#6b6e8a"
TEXT_MUTED = "#454760"
ACCENT = "#6366f1"
ACCENT_HOVER = "#818cf8"
ENTRY_BG = "#12121a"
DANGER = "#f43f5e"
FONT = "Segoe UI"


def _set_dark_titlebar(hwnd):
    try:
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, 20,
            ctypes.byref(ctypes.c_int(1)),
            ctypes.sizeof(ctypes.c_int),
        )
    except Exception:
        pass


class LoginWindow(tk.Tk):
    """Tela de autenticação. Retorna True em self.authenticated se login ok."""

    def __init__(self):
        super().__init__()
        self.authenticated = False
        self._is_first_run = crypto.is_first_run()

        self.withdraw()  # Esconde até posicionar

        self.title("Acessar Servidores — Login")
        w, h = 560, 540
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.minsize(500, 480)
        self.configure(bg=BG)

        icon_path = os.path.join(_RESOURCE_DIR, "icon.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)

        self.update_idletasks()
        _set_dark_titlebar(ctypes.windll.user32.GetParent(self.winfo_id()))

        self._build_ui()
        self.bind("<Return>", lambda _: self._on_submit())

        self.deiconify()  # Mostra já centralizada
        self._pw_entry.focus_force()

    def _build_ui(self):
        # Header
        tk.Label(self, text="⬡", bg=BG, fg=ACCENT,
                 font=(FONT, 28)).pack(pady=(40, 5))
        tk.Label(self, text="ACESSAR SERVIDORES", bg=BG, fg=TEXT,
                 font=(FONT, 14, "bold")).pack()

        if self._is_first_run:
            subtitle = "Crie uma senha mestre para proteger suas conexões"
        else:
            subtitle = "Digite sua senha mestre para continuar"

        tk.Label(self, text=subtitle, bg=BG, fg=TEXT_DIM,
                 font=(FONT, 9)).pack(pady=(4, 30))

        # Campo de senha
        form = tk.Frame(self, bg=BG)
        form.pack(padx=50, fill=tk.X)

        self._pw_entry, self._pw_line = self._create_password_field(form, "SENHA MESTRE")

        # Campo de confirmação (só no primeiro acesso)
        if self._is_first_run:
            self._confirm_entry, _ = self._create_password_field(
                form, "CONFIRMAR SENHA", top_pad=16)

        # Mensagem de erro
        self._error_label = tk.Label(form, text="", bg=BG, fg=DANGER,
                                     font=(FONT, 9))
        self._error_label.pack(anchor="w", pady=(10, 0))

        # Botão
        btn = tk.Canvas(form, height=42, bg=BG, highlightthickness=0, cursor="hand2")
        btn.pack(fill=tk.X, pady=(12, 0))

        def _render_btn(hover=False):
            btn.delete("all")
            w = btn.winfo_width() or 320
            color = ACCENT_HOVER if hover else ACCENT
            r = 8
            points = [r, 0, w - r, 0, w, 0, w, r, w, 42 - r, w, 42,
                      w - r, 42, r, 42, 0, 42, 0, 42 - r, 0, r, 0, 0]
            btn.create_polygon(points, smooth=True, fill=color, outline="")
            text = "CRIAR SENHA" if self._is_first_run else "ENTRAR"
            btn.create_text(w / 2, 21, text=text, fill="#ffffff",
                            font=(FONT, 11, "bold"))

        btn.bind("<Configure>", lambda _: _render_btn())
        btn.bind("<Enter>", lambda _: _render_btn(True))
        btn.bind("<Leave>", lambda _: _render_btn(False))
        btn.bind("<ButtonRelease-1>", lambda _: self._on_submit())

        self._pw_entry.focus_set()

    def _create_password_field(self, parent, label_text, top_pad=0):
        """Cria um campo de senha com botão de olhinho para mostrar/esconder."""
        tk.Label(parent, text=label_text, bg=BG, fg=TEXT_DIM,
                 font=(FONT, 8, "bold")).pack(anchor="w", pady=(top_pad, 4))

        row = tk.Frame(parent, bg=ENTRY_BG)
        row.pack(fill=tk.X)

        entry = tk.Entry(
            row, bg=ENTRY_BG, fg=TEXT, insertbackground=ACCENT,
            font=(FONT, 12), relief=tk.FLAT, bd=0, show="●",
            highlightthickness=0,
        )
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10)

        eye_label = tk.Label(row, text="Exibir", bg=ENTRY_BG, fg=TEXT_MUTED,
                             font=(FONT, 12), cursor="hand2")
        eye_label.pack(side=tk.RIGHT, padx=(0, 8))

        visible = [False]

        def toggle(_e=None):
            visible[0] = not visible[0]
            entry.config(show="" if visible[0] else "●")
            eye_label.config(
                text="Ocultar" if visible[0] else "Exibir",
                fg=ACCENT if visible[0] else TEXT_MUTED,
            )

        eye_label.bind("<Button-1>", toggle)

        line = tk.Canvas(parent, height=2, bg=BORDER, highlightthickness=0)
        line.pack(fill=tk.X)

        return entry, line

    def _show_error(self, msg: str):
        self._error_label.config(text=msg)
        self._pw_line.config(bg=DANGER)
        self.after(3000, lambda: (
            self._error_label.config(text=""),
            self._pw_line.config(bg=BORDER),
        ))

    def _on_submit(self):
        password = self._pw_entry.get()

        if not password:
            self._show_error("Digite uma senha.")
            return

        if self._is_first_run:
            if len(password) < 4:
                self._show_error("A senha deve ter pelo menos 4 caracteres.")
                return
            confirm = self._confirm_entry.get()
            if password != confirm:
                self._show_error("As senhas não coincidem.")
                return
            crypto.create_master_password(password)
            self.authenticated = True
            self.destroy()
        else:
            if crypto.authenticate(password):
                self.authenticated = True
                self.destroy()
            else:
                self._show_error("Senha incorreta.")
                self._pw_entry.delete(0, tk.END)
                self._pw_entry.focus_set()
