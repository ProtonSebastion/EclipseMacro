import customtkinter as ctk


class StatusTab(ctk.CTkFrame):
    def __init__(self, parent, t: dict):
        super().__init__(parent, fg_color="transparent")
        self.t = t
        self._build()

    def _build(self):
        ctk.CTkLabel(
            self,
            text="Status info coming soon...",
            font=ctk.CTkFont(family="JetBrains Mono", size=12),
            text_color=self.t["text_secondary"],
        ).pack(expand=True)