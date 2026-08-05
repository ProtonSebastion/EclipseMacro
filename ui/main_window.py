import os
import threading
import customtkinter as ctk
from PIL import Image
from ui.themes import THEMES
from core.config import load as load_config, save as save_config
from ui.Tabs.macro import MacroTab
from ui.Tabs.status import StatusTab
from ui.Tabs.webhook import WebhookTab
from ui.Tabs.settings import SettingsTab

# ── Icon paths ────────────────────────────────────────────
ICON_DIR = os.path.join(os.path.dirname(__file__), "icons")

THEME_ICONS = {
    "Eclipse":          os.path.join(ICON_DIR, "EclipseLogo.png"),
    "Catppuccin Mocha": os.path.join(ICON_DIR, "CatpuccinMochaLogo.png"),
    "Celeste":          os.path.join(ICON_DIR, "MadelieneLogo.png"),
    "Illusionary":      os.path.join(ICON_DIR, "illusionaryLogo2.png"),
}

THEME_ICONS_ICO = {
    "Eclipse":          os.path.join(ICON_DIR, "EclipseLogo.ico"),
    "Catppuccin Mocha": os.path.join(ICON_DIR, "Catpuccin.ico"),
    "Celeste":          os.path.join(ICON_DIR, "Madeliene.ico"),
    "Illusionary":      os.path.join(ICON_DIR, "illusionaryLogo1.ico"),
}

THEME_ICONS_TRAY = {
    "Eclipse":          os.path.join(ICON_DIR, "EclipseLogo.png"),
    "Catppuccin Mocha": os.path.join(ICON_DIR, "CatpuccinMochaLogo.png"),
    "Celeste":          os.path.join(ICON_DIR, "MadelieneLogo.png"),
    "Illusionary":      os.path.join(ICON_DIR, "illusionaryLogo1.png"),
}


def _autocrop(img: Image.Image) -> Image.Image:
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    _, _, _, a = img.split()
    bbox = a.getbbox()
    return img.crop(bbox) if bbox else img


def _load_ctk_image(path: str, size=(28, 28)):
    try:
        img = _autocrop(Image.open(path).convert("RGBA"))
        return ctk.CTkImage(light_image=img, dark_image=img, size=size)
    except Exception:
        return None


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        cfg = load_config()
        self.current_theme  = cfg["theme"]
        self.t              = THEMES[self.current_theme]
        self.active_tab     = "Macro"
        self.minimize_to_tray = ctk.BooleanVar(value=cfg["minimize_to_tray"])

        self._drag_x = 0
        self._drag_y = 0

        self.title("Eclipse Macro")
        self.geometry("800x450")
        self.resizable(False, False)
        self.overrideredirect(True)
        self.after(200, self._fix_taskbar)

        self._setup_tray()
        self._build()

    # ── Taskbar fix ───────────────────────────────────────
    def _fix_taskbar(self):
        try:
            import ctypes
            hwnd  = ctypes.windll.user32.GetParent(self.winfo_id())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, style & ~0x80)
            self.wm_withdraw()
            self.wm_deiconify()
        except Exception:
            pass

    # ── Window icon ───────────────────────────────────────
    def _update_window_icon(self):
        try:
            path = THEME_ICONS_ICO.get(self.current_theme, "")
            if os.path.exists(path):
                self.iconbitmap(path)
        except Exception:
            pass

    # ── System tray ───────────────────────────────────────
    def _setup_tray(self):
        try:
            import pystray
            self._pystray   = pystray
            self._tray_icon = None
            self._start_tray()
        except ImportError:
            self._pystray = None

    def _get_tray_image(self):
        path = THEME_ICONS_TRAY.get(self.current_theme)
        try:
            return _autocrop(Image.open(path).convert("RGBA")).resize((64, 64), Image.LANCZOS)
        except Exception:
            return Image.new("RGBA", (64, 64), "#fcc200")

    def _start_tray(self):
        if not self._pystray:
            return
        if self._tray_icon:
            self._tray_icon.stop()

        menu = self._pystray.Menu(
            self._pystray.MenuItem("Show", self._show_window, default=True),
            self._pystray.MenuItem("Quit", self._quit_app),
        )
        self._tray_icon = self._pystray.Icon(
            "Eclipse Macro", self._get_tray_image(), "Eclipse Macro", menu
        )
        threading.Thread(target=self._tray_icon.run, daemon=True).start()

    def _update_tray_icon(self):
        if self._tray_icon:
            self._tray_icon.icon = self._get_tray_image()

    def _show_window(self):
        self.after(0, self.deiconify)
        self.after(0, self.lift)

    def _quit_app(self):
        from ui.Tabs.webhook import _send_embed
        cfg = load_config()
        url = cfg.get("webhook_url", "").strip()

        if url:
            t = threading.Thread(
                target=_send_embed,
                args=(url, "✦ Macro Turned Off", "notify_macro_stopped"),
                daemon=False,
            )
            t.start()
            t.join(timeout=5)

        if self._tray_icon:
            self._tray_icon.stop()
        self.destroy()

    # ── Build UI ──────────────────────────────────────────
    def _build(self):
        for w in self.winfo_children():
            w.destroy()
        self.configure(fg_color=self.t["bg_primary"])
        self._build_titlebar()
        self._build_body()
        self._switch_tab(self.active_tab)

    # ── Title bar ─────────────────────────────────────────
    def _build_titlebar(self):
        t   = self.t
        bar = ctk.CTkFrame(self, height=48, fg_color=t["bg_secondary"], corner_radius=0)
        bar.pack(fill="x", side="top")
        bar.pack_propagate(False)

        ctk.CTkLabel(
            bar,
            text="✦  ECLIPSE MACRO",
            font=ctk.CTkFont(family="JetBrains Mono", size=16, weight="bold"),
            text_color=t["accent"],
        ).pack(side="left", padx=16)

        ctk.CTkLabel(
            bar,
            text="Project Eclipse - v0.1.0",
            font=ctk.CTkFont(family="JetBrains Mono", size=11),
            text_color=t["text_secondary"],
        ).pack(side="left")

        ctk.CTkButton(
            bar, text="✕", width=36, height=28,
            fg_color="transparent", hover_color=t["danger"],
            text_color=t["text_secondary"],
            font=ctk.CTkFont(size=13),
            command=self._close_action,
        ).pack(side="right", padx=4)

        ctk.CTkButton(
            bar, text="—", width=36, height=28,
            fg_color="transparent", hover_color=t["bg_tertiary"],
            text_color=t["text_secondary"],
            font=ctk.CTkFont(size=13),
            command=self._hide_to_tray,
        ).pack(side="right")

        bar.bind("<ButtonPress-1>", self._start_drag)
        bar.bind("<B1-Motion>",     self._do_drag)

    # ── Close / hide ──────────────────────────────────────
    def _close_action(self):
        if self.minimize_to_tray.get():
            self.withdraw()
        else:
            self._quit_app()

    def _hide_to_tray(self):
        self.withdraw()

    def _start_drag(self, event):
        self._drag_x = event.x_root - self.winfo_x()
        self._drag_y = event.y_root - self.winfo_y()

    def _do_drag(self, event):
        self.geometry(f"+{event.x_root - self._drag_x}+{event.y_root - self._drag_y}")

    # ── Body ──────────────────────────────────────────────
    def _build_body(self):
        body = ctk.CTkFrame(self, fg_color=self.t["bg_primary"], corner_radius=0)
        body.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self._build_sidebar(body)
        self._build_content(body)

    # ── Sidebar ───────────────────────────────────────────
    def _build_sidebar(self, parent):
        t = self.t
        self.sidebar = ctk.CTkFrame(
            parent, width=148, fg_color=t["bg_secondary"], corner_radius=10
        )
        self.sidebar.pack(side="left", fill="y", padx=(0, 10), pady=8)
        self.sidebar.pack_propagate(False)

        ctk.CTkFrame(self.sidebar, height=12, fg_color="transparent").pack()

        self.nav_buttons = {}

        macro_icon = _load_ctk_image(THEME_ICONS.get(self.current_theme, ""), (28, 28))
        self._add_nav_btn("Macro",    display="Macro",         icon=macro_icon)
        self._add_nav_btn("Status",   display="📃  Status")
        self._add_nav_btn("Webhook",  display="🔔  Webhook")
        self._add_nav_btn("Settings", display="⚙️  Settings")

    def _add_nav_btn(self, name: str, display: str = "", icon=None):
        t   = self.t
        btn = ctk.CTkButton(
            self.sidebar,
            text=display or name,
            image=icon if icon else None,
            compound="left",
            anchor="w",
            height=36,
            corner_radius=20,
            fg_color=t["bg_tertiary"],
            hover_color=t["bg_tertiary"],
            border_width=2,
            border_color=t["border"],
            text_color=t["text_secondary"],
            font=ctk.CTkFont(family="JetBrains Mono", size=12),
            command=lambda n=name: self._switch_tab(n),
            background_corner_colors=(
                t["bg_secondary"], t["bg_secondary"],
                t["bg_secondary"], t["bg_secondary"],
            ),
        )
        btn.pack(fill="x", padx=10, pady=3)
        self.nav_buttons[name] = btn

    # ── Content area ──────────────────────────────────────
    def _build_content(self, parent):
        t = self.t
        self.content = ctk.CTkFrame(parent, fg_color=t["bg_secondary"], corner_radius=10)
        self.content.pack(side="left", fill="both", expand=True, pady=8)

        self.tab_frames = {
            "Macro":    MacroTab(self.content, self.t),
            "Status":   StatusTab(self.content, self.t),
            "Webhook":  WebhookTab(self.content, self.t),
            "Settings": SettingsTab(
                self.content, self.t,
                self.current_theme,
                self._do_change_theme,
                self.minimize_to_tray,
            ),
        }

    # ── Tab switching ─────────────────────────────────────
    def _switch_tab(self, name: str):
        t = self.t
        self.active_tab = name

        for tab_name, btn in self.nav_buttons.items():
            if tab_name == name:
                btn.configure(
                    fg_color=t["purple"], border_color=t["purple"],
                    text_color=t["text_primary"], hover_color=t["purple"],
                    background_corner_colors=(
                        t["bg_secondary"], t["bg_secondary"],
                        t["bg_secondary"], t["bg_secondary"],
                    ),
                )
            else:
                btn.configure(
                    fg_color=t["bg_tertiary"], border_color=t["border"],
                    text_color=t["text_secondary"], hover_color=t["bg_tertiary"],
                    background_corner_colors=(
                        t["bg_secondary"], t["bg_secondary"],
                        t["bg_secondary"], t["bg_secondary"],
                    ),
                )

        for tab_name, frame in self.tab_frames.items():
            frame.pack_forget()
        self.tab_frames[name].pack(fill="both", expand=True, padx=16, pady=16)

    # ── Theme change ──────────────────────────────────────
    def _do_change_theme(self, name: str):
        self.current_theme = name
        self.t             = THEMES[name]
        self.active_tab    = "Settings"
        save_config(self.current_theme, self.minimize_to_tray.get())
        self._update_tray_icon()
        self._update_window_icon()
        self._build()