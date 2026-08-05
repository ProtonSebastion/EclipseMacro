import os
import webbrowser
import customtkinter as ctk
from PIL import Image
from ui.themes import THEMES
from core.config import save as save_config

ICON_DIR = os.path.join(os.path.dirname(__file__), "..", "icons")

THEME_LOGOS = {
    "Eclipse":          os.path.join(ICON_DIR, "EclipseLogo.png"),
    "Catppuccin Mocha": os.path.join(ICON_DIR, "CatpuccinMochaLogo.png"),
    "Celeste":          os.path.join(ICON_DIR, "MadelieneLogo.png"),
    "Illusionary":      os.path.join(ICON_DIR, "illusionaryLogo2.png"),
}

GITHUB_URL = "https://github.com/ProtonSebastion/EclipseMacro"


class SettingsTab(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        t: dict,
        current_theme: str,
        theme_changer,
        minimize_var: ctk.BooleanVar,
    ):
        super().__init__(parent, fg_color="transparent")
        self.t             = t
        self.current_theme = current_theme
        self.theme_changer = theme_changer
        self.minimize_var  = minimize_var
        self._build()

    # ── Layout ────────────────────────────────────────────
    def _build(self):
        t = self.t

        left = ctk.CTkFrame(self, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))

        right = ctk.CTkFrame(
            self,
            fg_color=t["bg_tertiary"],
            corner_radius=12,
            border_width=1,
            border_color=t["border"],
        )
        right.pack(side="left", fill="both", expand=True)

        self._build_left(left)
        self._build_right(right)

    # ── Left panel ────────────────────────────────────────
    def _build_left(self, parent):
        t = self.t

        ctk.CTkLabel(
            parent,
            text="Theme",
            font=ctk.CTkFont(family="JetBrains Mono", size=11),
            text_color=t["text_secondary"],
        ).pack(anchor="w", pady=(0, 4))

        ctk.CTkOptionMenu(
            parent,
            values=list(THEMES.keys()),
            variable=ctk.StringVar(value=self.current_theme),
            command=self.theme_changer,
            fg_color=t["bg_tertiary"],
            button_color=t["purple"],
            button_hover_color=t["accent"],
            text_color=t["text_primary"],
            font=ctk.CTkFont(family="JetBrains Mono", size=12),
            width=180,
        ).pack(anchor="w")

        ctk.CTkFrame(parent, height=16, fg_color="transparent").pack()

        ctk.CTkLabel(
            parent,
            text="Minimize to tray on close",
            font=ctk.CTkFont(family="JetBrains Mono", size=11),
            text_color=t["text_secondary"],
        ).pack(anchor="w", pady=(0, 4))

        ctk.CTkSwitch(
            parent,
            text="",
            variable=self.minimize_var,
            onvalue=True, offvalue=False,
            progress_color=t["purple"],
            button_color=t["accent"],
            button_hover_color=t["accent"],
            fg_color=t["bg_primary"],
            command=self._on_toggle,
        ).pack(anchor="w")

    # ── Right panel ───────────────────────────────────────
    def _build_right(self, parent):
        t = self.t

        try:
            img     = self._autocrop(Image.open(THEME_LOGOS.get(self.current_theme, "")).convert("RGBA"))
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(80, 80))
            ctk.CTkLabel(parent, image=ctk_img, text="").pack(pady=(24, 8))
        except Exception:
            ctk.CTkFrame(parent, height=80, fg_color="transparent").pack(pady=(24, 8))

        ctk.CTkLabel(
            parent,
            text="Using Theme",
            font=ctk.CTkFont(family="JetBrains Mono", size=10),
            text_color=t["text_secondary"],
        ).pack()

        ctk.CTkLabel(
            parent,
            text=self.current_theme,
            font=ctk.CTkFont(family="JetBrains Mono", size=13, weight="bold"),
            text_color=t["accent"],
        ).pack(pady=(2, 16))

        buttons = [
            ("⭐  GitHub Repo",   t["purple"],  lambda: webbrowser.open(GITHUB_URL)),
            ("📃  Show Logs",     t["purple"],  lambda: print("Show logs — TODO")),
            ("↺  Reset Defaults", t["danger"],  self._confirm_reset),
        ]

        for label, hover, cmd in buttons:
            ctk.CTkButton(
                parent,
                text=label,
                width=140, height=30, corner_radius=8,
                fg_color=t["bg_primary"],
                hover_color=hover,
                border_width=1,
                border_color=t["border"],
                text_color=t["text_primary"],
                font=ctk.CTkFont(family="JetBrains Mono", size=11),
                command=cmd,
            ).pack(pady=(0, 6))

    # ── Helpers ───────────────────────────────────────────
    def _on_toggle(self):
        save_config(self.current_theme, self.minimize_var.get())

    def _autocrop(self, img: Image.Image) -> Image.Image:
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        _, _, _, a = img.split()
        bbox = a.getbbox()
        return img.crop(bbox) if bbox else img

    def _confirm_reset(self):
        t      = self.t
        dialog = ctk.CTkToplevel(self)
        dialog.title("Reset Defaults")
        dialog.geometry("320x140")
        dialog.resizable(False, False)
        dialog.configure(fg_color=t["bg_secondary"])
        dialog.grab_set()
        dialog.lift()

        ctk.CTkLabel(
            dialog,
            text="Are you sure you want to\nreset to default settings?",
            font=ctk.CTkFont(family="JetBrains Mono", size=12),
            text_color=t["text_primary"],
        ).pack(pady=(24, 16))

        btn_row = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_row.pack()

        ctk.CTkButton(
            btn_row,
            text="Yes, Reset",
            width=120, height=30, corner_radius=8,
            fg_color=t["danger"],
            hover_color="#c04040",
            text_color="#ffffff",
            font=ctk.CTkFont(family="JetBrains Mono", size=11),
            command=lambda: [save_config("Eclipse", False), dialog.destroy()],
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_row,
            text="Cancel",
            width=120, height=30, corner_radius=8,
            fg_color=t["bg_tertiary"],
            hover_color=t["purple"],
            border_width=1,
            border_color=t["border"],
            text_color=t["text_primary"],
            font=ctk.CTkFont(family="JetBrains Mono", size=11),
            command=dialog.destroy,
        ).pack(side="left")