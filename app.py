import ctypes
import os
import sys
import tkinter as tk
from tkinter import messagebox
import storage
import rdp

# Recursos empacotados (icon) ficam em _MEIPASS; dados persistentes ao lado do .exe
if getattr(sys, 'frozen', False):
    _RESOURCE_DIR = sys._MEIPASS
else:
    _RESOURCE_DIR = os.path.dirname(os.path.abspath(__file__))

# DPI awareness no Windows — evita interface borrada em monitores HiDPI
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass


def _set_dark_titlebar(hwnd):
    """Força title bar escura no Windows 10/11."""
    try:
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(ctypes.c_int(1)),
            ctypes.sizeof(ctypes.c_int),
        )
    except Exception:
        pass


# ── Paleta ──────────────────────────────────────────────────
class C:
    BG = "#0f0f14"
    SURFACE = "#16161e"
    CARD = "#1c1c27"
    BORDER = "#2a2a3a"
    BORDER_FOCUS = "#6366f1"
    TEXT = "#e2e4f0"
    TEXT_DIM = "#6b6e8a"
    TEXT_MUTED = "#454760"
    ACCENT = "#6366f1"
    ACCENT_HOVER = "#818cf8"
    DANGER = "#f43f5e"
    DANGER_HOVER = "#fb7185"
    ENTRY_BG = "#12121a"
    ROW_HOVER = "#1e1e2e"
    ROW_SELECTED = "#24243a"


FONT = "Segoe UI"
FONT_MONO = "Cascadia Code"


# ── Widgets customizados ────────────────────────────────────

class FlatEntry(tk.Frame):
    """Entry com linha de foco animada na base."""

    def __init__(self, parent, placeholder="", show=""):
        super().__init__(parent, bg=C.BG)
        self._placeholder = placeholder
        self._is_placeholder = False
        self._show = show
        self._visible = False

        row = tk.Frame(self, bg=C.ENTRY_BG)
        row.pack(fill=tk.X, pady=(1, 0))

        self.entry = tk.Entry(
            row, bg=C.ENTRY_BG, fg=C.TEXT, insertbackground=C.ACCENT,
            font=(FONT, 11), relief=tk.FLAT, bd=0, show=show,
            highlightthickness=0,
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=1)

        # Olhinho para campos de senha
        if show:
            self._eye = tk.Label(row, text="Exibir", bg=C.ENTRY_BG, fg=C.TEXT_MUTED,
                                 font=(FONT, 11), cursor="hand2")
            self._eye.pack(side=tk.RIGHT, padx=(0, 6))
            self._eye.bind("<Button-1>", self._toggle_visibility)

        self._line = tk.Canvas(self, height=2, bg=C.BORDER, highlightthickness=0)
        self._line.pack(fill=tk.X)

        self.entry.bind("<FocusIn>", self._focus_in)
        self.entry.bind("<FocusOut>", self._focus_out)

        self._show_placeholder()

    def _show_placeholder(self):
        if not self.entry.get():
            self._is_placeholder = True
            self.entry.config(fg=C.TEXT_MUTED)
            if self._show:
                self.entry.config(show="")
            self.entry.insert(0, self._placeholder)

    def _hide_placeholder(self):
        if self._is_placeholder:
            self._is_placeholder = False
            self.entry.delete(0, tk.END)
            self.entry.config(fg=C.TEXT)
            if self._show:
                self.entry.config(show=self._show)

    def _toggle_visibility(self, _e=None):
        self._visible = not self._visible
        if self._is_placeholder:
            return
        self.entry.config(show="" if self._visible else self._show)
        if hasattr(self, "_eye"):
            self._eye.config(
                text="Ocultar" if self._visible else "Exibir",
                fg=C.ACCENT if self._visible else C.TEXT_MUTED,
            )

    def _focus_in(self, _e):
        self._hide_placeholder()
        self._line.config(bg=C.ACCENT)

    def _focus_out(self, _e):
        self._line.config(bg=C.BORDER)
        if not self.entry.get():
            self._show_placeholder()

    def get(self) -> str:
        if self._is_placeholder:
            return ""
        return self.entry.get()

    def set(self, value: str):
        self._is_placeholder = False
        self.entry.config(fg=C.TEXT)
        if self._show:
            self.entry.config(show=self._show)
        self.entry.delete(0, tk.END)
        if value:
            self.entry.insert(0, value)
        else:
            self._show_placeholder()

    def clear(self):
        self._is_placeholder = False
        self.entry.delete(0, tk.END)
        self.entry.config(fg=C.TEXT)
        if self._show:
            self.entry.config(show=self._show)
        self._show_placeholder()


class FlatButton(tk.Canvas):
    """Botão flat com hover animado."""

    def __init__(self, parent, text="", command=None,
                 bg=C.ACCENT, fg="#ffffff", hover_bg=C.ACCENT_HOVER,
                 width=140, height=38, radius=8, font_size=10, bold=True):
        super().__init__(parent, width=width, height=height,
                         bg=C.BG, highlightthickness=0, cursor="hand2")
        self._text = text
        self._command = command
        self._bg = bg
        self._fg = fg
        self._hover_bg = hover_bg
        self._current_bg = bg
        self._radius = radius
        self._font_size = font_size
        self._bold = bold

        self.bind("<Enter>", lambda _: self._set_color(hover_bg))
        self.bind("<Leave>", lambda _: self._set_color(bg))
        self.bind("<ButtonRelease-1>", self._release)
        self.bind("<Configure>", lambda _: self._render())
        self._render()

    def _set_color(self, color):
        self._current_bg = color
        self._render()

    def _release(self, _e):
        if self._command:
            self._command()

    def _render(self):
        self.delete("all")
        w = self.winfo_width() or int(self.cget("width"))
        h = self.winfo_height() or int(self.cget("height"))
        r = self._radius
        points = [
            r, 0, w - r, 0, w, 0, w, r,
            w, h - r, w, h, w - r, h, r, h,
            0, h, 0, h - r, 0, r, 0, 0,
        ]
        self.create_polygon(points, smooth=True, fill=self._current_bg, outline="")
        weight = "bold" if self._bold else "normal"
        self.create_text(w / 2, h / 2, text=self._text, fill=self._fg,
                         font=(FONT, self._font_size, weight))


class ConnectionCard(tk.Frame):
    """Card de conexão individual na lista."""

    def __init__(self, parent, conn: dict, on_select, on_dblclick):
        super().__init__(parent, bg=C.SURFACE, cursor="hand2")
        self.conn = conn
        self._selected = False

        self.configure(highlightthickness=1, highlightbackground=C.BORDER)

        # Conteúdo
        top = tk.Frame(self, bg=C.SURFACE)
        top.pack(fill=tk.X, padx=14, pady=(10, 2))

        desc = conn.get("description") or conn["host"]
        tk.Label(top, text=desc, bg=C.SURFACE, fg=C.TEXT,
                 font=(FONT, 11, "bold"), anchor="w").pack(side=tk.LEFT)

        port_text = f":{conn['port']}" if conn["port"] != "3389" else ""
        tk.Label(top, text=port_text, bg=C.SURFACE, fg=C.TEXT_DIM,
                 font=(FONT_MONO, 9)).pack(side=tk.RIGHT)

        bottom = tk.Frame(self, bg=C.SURFACE)
        bottom.pack(fill=tk.X, padx=14, pady=(0, 10))

        tk.Label(bottom, text=conn["host"], bg=C.SURFACE, fg=C.TEXT_DIM,
                 font=(FONT_MONO, 9), anchor="w").pack(side=tk.LEFT)

        tk.Label(bottom, text=conn["username"], bg=C.SURFACE,
                 fg=C.TEXT_MUTED, font=(FONT, 9), anchor="e").pack(side=tk.RIGHT)

        # Bind no card inteiro — usa bind no frame pai para evitar flicker
        self.bind("<Button-1>", lambda _: on_select(self))
        self.bind("<Double-1>", lambda _: on_dblclick(self))
        self.bind("<Enter>", lambda _: self._hover(True))
        self.bind("<Leave>", lambda _: self._hover(False))

        # Filhos propagam eventos para o card pai
        for widget in self._all_children():
            widget.bind("<Button-1>", lambda _: on_select(self))
            widget.bind("<Double-1>", lambda _: on_dblclick(self))
            # Não bind Enter/Leave nos filhos — evita flicker
            widget.configure(cursor="hand2")

    def _all_children(self):
        result = []
        for child in self.winfo_children():
            result.append(child)
            for sub in child.winfo_children():
                result.append(sub)
        return result

    def _hover(self, entering):
        if self._selected:
            return
        color = C.ROW_HOVER if entering else C.SURFACE
        self._set_bg(color)

    def _set_bg(self, color):
        self.configure(bg=color)
        for widget in self._all_children():
            try:
                widget.configure(bg=color)
            except tk.TclError:
                pass

    def select(self):
        self._selected = True
        self._set_bg(C.ROW_SELECTED)
        self.configure(highlightbackground=C.ACCENT)

    def deselect(self):
        self._selected = False
        self._set_bg(C.SURFACE)
        self.configure(highlightbackground=C.BORDER)


# ── App principal ───────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()  # Esconde até posicionar

        self.title("Acessar Servidores")
        w, h = 1200, 800
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.minsize(1100, 750)
        self.configure(bg=C.BG)

        # Ícone da janela
        icon_path = os.path.join(_RESOURCE_DIR, "icon.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)

        # Title bar escura no Windows 10/11
        self.update_idletasks()
        _set_dark_titlebar(ctypes.windll.user32.GetParent(self.winfo_id()))

        self._selected_id: str | None = None
        self._cards: list[ConnectionCard] = []
        self._selected_card: ConnectionCard | None = None
        self._scroll_canvas: tk.Canvas | None = None

        self._build_ui()
        self._refresh_list()

        self.deiconify()  # Mostra já centralizada

    def _build_ui(self):
        # ── Header ──
        header = tk.Frame(self, bg=C.BG, height=56)
        header.pack(fill=tk.X, padx=24, pady=(18, 0))
        header.pack_propagate(False)

        tk.Label(header, text="⬡", bg=C.BG, fg=C.ACCENT,
                 font=(FONT, 20)).pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(header, text="ACESSAR SERVIDORES", bg=C.BG, fg=C.TEXT,
                 font=(FONT, 14, "bold")).pack(side=tk.LEFT)
        tk.Label(header, text="Gerenciador de Conexões RDP", bg=C.BG, fg=C.TEXT_DIM,
                 font=(FONT, 10)).pack(side=tk.LEFT, padx=(12, 0), pady=(3, 0))

        # Separador
        tk.Canvas(self, height=1, bg=C.BORDER, highlightthickness=0).pack(
            fill=tk.X, padx=24, pady=(12, 0))

        # ── Corpo ──
        body = tk.Frame(self, bg=C.BG)
        body.pack(fill=tk.BOTH, expand=True, padx=24, pady=16)
        body.columnconfigure(0, weight=3, minsize=400)
        body.columnconfigure(1, weight=0)
        body.columnconfigure(2, weight=2, minsize=320)
        body.rowconfigure(0, weight=1)

        self._build_left_panel(body)
        self._build_right_panel(body)

        # Separador vertical
        tk.Frame(body, bg=C.BORDER, width=1).grid(row=0, column=1, sticky="ns", padx=20)

        # ── Rodapé ──
        footer = tk.Frame(self, bg=C.BG, height=30)
        footer.pack(fill=tk.X, padx=24, pady=(0, 10))
        tk.Label(footer,
                 text="↑↓ navegar  ·  Enter conectar  ·  Ctrl+S salvar  ·  Ctrl+N nova",
                 bg=C.BG, fg=C.TEXT_MUTED, font=(FONT, 8)).pack(side=tk.LEFT)

        # ── Atalhos de teclado ──
        self.bind_all("<Control-s>", lambda _: self._on_save())
        self.bind_all("<Control-n>", lambda _: self._clear_form())
        self.bind_all("<Control-Return>", lambda _: self._on_connect())
        self.bind_all("<Return>", lambda _: self._on_connect())
        self.bind_all("<Escape>", lambda _: self._clear_form())
        self.bind_all("<Up>", lambda _: self._navigate_cards(-1))
        self.bind_all("<Down>", lambda _: self._navigate_cards(1))

    def _build_left_panel(self, body):
        left = tk.Frame(body, bg=C.BG)
        left.grid(row=0, column=0, sticky="nsew")
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)

        # Header da lista
        list_header = tk.Frame(left, bg=C.BG)
        list_header.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        tk.Label(list_header, text="Conexões Salvas", bg=C.BG, fg=C.TEXT,
                 font=(FONT, 11, "bold")).pack(side=tk.LEFT)

        self._count_label = tk.Label(list_header, text="0", bg=C.BG, fg=C.TEXT_DIM,
                                     font=(FONT, 10))
        self._count_label.pack(side=tk.LEFT, padx=(8, 0))

        # Searchbar com placeholder
        search_frame = tk.Frame(list_header, bg=C.ENTRY_BG, highlightthickness=1,
                                highlightbackground=C.BORDER)
        search_frame.pack(side=tk.RIGHT)

        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._refresh_list())
        search_entry = tk.Entry(search_frame, textvariable=self._search_var,
                                bg=C.ENTRY_BG, fg=C.TEXT, insertbackground=C.TEXT_DIM,
                                font=(FONT, 10), relief=tk.FLAT, bd=0, width=16)
        search_entry.pack(side=tk.LEFT, padx=(8, 4), pady=5)

        tk.Label(search_frame, text="🔍", bg=C.ENTRY_BG, fg=C.TEXT_MUTED,
                 font=(FONT, 12)).pack(side=tk.LEFT, padx=(0, 8))

        # Container scrollável
        list_container = tk.Frame(left, bg=C.SURFACE, highlightthickness=1,
                                  highlightbackground=C.BORDER)
        list_container.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        list_container.rowconfigure(0, weight=1)
        list_container.columnconfigure(0, weight=1)

        canvas = tk.Canvas(list_container, bg=C.SURFACE, highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(list_container, orient=tk.VERTICAL,
                                 command=canvas.yview, bg=C.SURFACE,
                                 troughcolor=C.SURFACE, width=8,
                                 relief=tk.FLAT, bd=0)

        self._list_frame = tk.Frame(canvas, bg=C.SURFACE)
        self._list_frame.bind(
            "<Configure>",
            lambda _: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=self._list_frame, anchor="nw", tags="frame")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        self._scrollbar = scrollbar
        # Scrollbar só aparece quando necessário
        self._scrollbar_visible = False

        # Resize: ajusta largura do frame interno
        canvas.bind("<Configure>", lambda e: canvas.itemconfig("frame", width=e.width))

        # Scroll com mouse — só quando o cursor está sobre a lista
        self._scroll_canvas = canvas

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _bind_scroll(_e):
            self.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_scroll(_e):
            self.unbind_all("<MouseWheel>")

        canvas.bind("<Enter>", _bind_scroll)
        canvas.bind("<Leave>", _unbind_scroll)
        self._list_frame.bind("<Enter>", _bind_scroll)
        self._list_frame.bind("<Leave>", _unbind_scroll)

        # Label de estado vazio
        self._empty_label = tk.Label(
            self._list_frame,
            text="Nenhuma conexão salva.\nPreencha os campos ao lado e clique em Salvar.",
            bg=C.SURFACE, fg=C.TEXT_MUTED, font=(FONT, 10),
            justify=tk.CENTER, pady=40,
        )

    def _build_right_panel(self, body):
        right = tk.Frame(body, bg=C.BG)
        right.grid(row=0, column=2, sticky="nsew")

        tk.Label(right, text="Detalhes da Conexão", bg=C.BG, fg=C.TEXT,
                 font=(FONT, 11, "bold")).pack(anchor="w", pady=(0, 16))

        # Campos do formulário
        fields = [
            ("Descrição", "descrição", "Ex: Servidor Produção", ""),
            ("Host / IP", "host_ip", "192.168.1.100", ""),
            ("Porta", "porta", "3389", ""),
            ("Usuário", "usuário", "administrator", ""),
            ("Senha", "senha", "••••••••", "*"),
        ]
        self.entries: dict[str, FlatEntry] = {}

        for label_text, key, placeholder, show in fields:
            tk.Label(right, text=label_text.upper(), bg=C.BG, fg=C.TEXT_DIM,
                     font=(FONT, 8, "bold")).pack(anchor="w", pady=(8, 3))
            entry = FlatEntry(right, placeholder=placeholder, show=show)
            entry.pack(fill=tk.X, pady=(0, 4))
            self.entries[key] = entry

        self.entries["porta"].set("3389")

        # ── Botões ──
        btn_area = tk.Frame(right, bg=C.BG)
        btn_area.pack(fill=tk.X, pady=(20, 0))

        connect_btn = FlatButton(btn_area, text="▶  CONECTAR", command=self._on_connect,
                                 bg=C.ACCENT, hover_bg=C.ACCENT_HOVER,
                                 width=280, height=42, font_size=11)
        connect_btn.pack(fill=tk.X, pady=(0, 10))

        btn_row = tk.Frame(btn_area, bg=C.BG)
        btn_row.pack(fill=tk.X)
        btn_row.columnconfigure(0, weight=1)
        btn_row.columnconfigure(1, weight=1)

        save_btn = FlatButton(btn_row, text="SALVAR", command=self._on_save,
                              bg=C.CARD, fg=C.TEXT, hover_bg=C.BORDER,
                              width=130, height=36, font_size=10, bold=False)
        save_btn.grid(row=0, column=0, sticky="ew", padx=(0, 4))

        del_btn = FlatButton(btn_row, text="EXCLUIR", command=self._on_delete,
                             bg=C.CARD, fg=C.DANGER, hover_bg="#2a1520",
                             width=130, height=36, font_size=10, bold=False)
        del_btn.grid(row=0, column=1, sticky="ew", padx=(4, 0))

        new_btn = FlatButton(btn_area, text="+  NOVA CONEXÃO", command=self._clear_form,
                             bg=C.BG, fg=C.TEXT_DIM, hover_bg=C.CARD,
                             width=280, height=32, font_size=9, bold=False)
        new_btn.pack(fill=tk.X, pady=(8, 0))

    # ── Ações ───────────────────────────────────────────

    def _update_scrollbar(self):
        """Mostra/esconde scrollbar conforme necessidade."""
        self._scroll_canvas.update_idletasks()
        canvas_height = self._scroll_canvas.winfo_height()
        content_height = self._list_frame.winfo_reqheight()
        if content_height > canvas_height:
            if not self._scrollbar_visible:
                self._scrollbar.grid(row=0, column=1, sticky="ns")
                self._scrollbar_visible = True
        else:
            if self._scrollbar_visible:
                self._scrollbar.grid_remove()
                self._scrollbar_visible = False

    def _refresh_list(self):
        for card in self._cards:
            card.destroy()
        self._cards.clear()
        self._selected_card = None

        search = self._search_var.get().lower() if hasattr(self, "_search_var") else ""
        connections = storage.list_connections()
        filtered = [c for c in connections
                    if search in c["description"].lower()
                    or search in c["host"].lower()
                    or search in c["username"].lower()] if search else connections

        self._count_label.config(text=f"{len(filtered)} conexões")

        # Estado vazio
        if not filtered:
            self._empty_label.pack(fill=tk.X, padx=20, pady=20)
        else:
            self._empty_label.pack_forget()

        for conn in filtered:
            card = ConnectionCard(self._list_frame, conn,
                                  on_select=self._on_card_select,
                                  on_dblclick=self._on_card_dblclick)
            card.pack(fill=tk.X, padx=4, pady=2)
            self._cards.append(card)

            # Bind scroll nos cards também
            if self._scroll_canvas:
                canvas = self._scroll_canvas

                def _on_mousewheel(event, c=canvas):
                    c.yview_scroll(int(-1 * (event.delta / 120)), "units")

                for w in [card] + card._all_children():
                    w.bind("<MouseWheel>", _on_mousewheel)

            if conn["id"] == self._selected_id:
                card.select()
                self._selected_card = card

        # Atualiza scrollbar após renderizar
        self.after(50, self._update_scrollbar)

    def _navigate_cards(self, direction: int):
        """Navega pelos cards com setas. direction: -1 (cima) ou 1 (baixo)."""
        if not self._cards:
            return

        if self._selected_card is None:
            # Nenhum selecionado: seleciona o primeiro (baixo) ou último (cima)
            index = 0 if direction == 1 else len(self._cards) - 1
        else:
            try:
                current = self._cards.index(self._selected_card)
            except ValueError:
                current = 0
            index = current + direction
            if index < 0 or index >= len(self._cards):
                return  # Já no limite

        self._on_card_select(self._cards[index])

        # Garante que o card selecionado fique visível no scroll
        card = self._cards[index]
        self._scroll_canvas.update_idletasks()
        canvas_height = self._scroll_canvas.winfo_height()
        card_y = card.winfo_y()
        card_h = card.winfo_height()
        total_h = self._list_frame.winfo_reqheight()

        if total_h > canvas_height:
            # Calcula posição relativa e ajusta scroll
            top = self._scroll_canvas.yview()[0] * total_h
            bottom = top + canvas_height
            if card_y < top:
                self._scroll_canvas.yview_moveto(card_y / total_h)
            elif card_y + card_h > bottom:
                self._scroll_canvas.yview_moveto((card_y + card_h - canvas_height) / total_h)

    def _clear_form(self, _event=None):
        self._selected_id = None
        for entry in self.entries.values():
            entry.clear()
        self.entries["porta"].set("3389")
        if self._selected_card:
            self._selected_card.deselect()
            self._selected_card = None

    def _on_card_select(self, card: ConnectionCard):
        if self._selected_card:
            self._selected_card.deselect()
        card.select()
        self._selected_card = card

        self._selected_id = card.conn["id"]

        full_conn = storage.get_connection(card.conn["id"])
        if not full_conn:
            return

        mapping = {
            "descrição": full_conn["description"],
            "host_ip": full_conn["host"],
            "porta": full_conn["port"],
            "usuário": full_conn["username"],
            "senha": full_conn["password"],
        }
        for key, entry in self.entries.items():
            entry.set(mapping.get(key, ""))

    def _on_card_dblclick(self, card: ConnectionCard):
        self._on_card_select(card)
        self._on_connect()

    def _on_save(self, _event=None):
        values = {k: e.get().strip() for k, e in self.entries.items()}
        if not values["host_ip"] or not values["usuário"]:
            messagebox.showwarning("Campos obrigatórios",
                                   "Host e Usuário são obrigatórios.")
            return

        if self._selected_id:
            storage.update_connection(
                self._selected_id,
                values["host_ip"], values["porta"],
                values["usuário"], values["senha"],
                values["descrição"],
            )
        else:
            storage.add_connection(
                values["host_ip"], values["porta"],
                values["usuário"], values["senha"],
                values["descrição"],
            )
        self._refresh_list()
        self._clear_form()

    def _on_delete(self, _event=None):
        if not self._selected_id:
            messagebox.showinfo("Seleção", "Selecione uma conexão para excluir.")
            return
        if not messagebox.askyesno("Confirmar", "Deseja excluir esta conexão?"):
            return
        storage.delete_connection(self._selected_id)
        self._refresh_list()
        self._clear_form()

    def _on_connect(self, _event=None):
        values = {k: e.get().strip() for k, e in self.entries.items()}
        if not values["host_ip"] or not values["usuário"]:
            messagebox.showwarning("Campos obrigatórios",
                                   "Host e Usuário são obrigatórios.")
            return
        try:
            rdp.connect(values["host_ip"], values["porta"],
                        values["usuário"], values["senha"])
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao conectar:\n{e}")
