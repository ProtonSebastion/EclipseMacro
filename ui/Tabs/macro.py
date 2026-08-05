import customtkinter as ctk
from core.communication import Communication


class MacroTab(ctk.CTkFrame):
    def __init__(self, parent, t: dict):
        super().__init__(parent, fg_color="transparent")
        self.t = t
        self.running = False
        self.fishing_count = ctk.IntVar(value=45)
        self.sell_count = ctk.IntVar(value=56)
        self.selected_pack = ctk.StringVar()
        self.debug = ctk.BooleanVar(value=False)
        self.comm = Communication()
        self._countdown_remaining = 0
        self._build()

        self.winfo_toplevel().bind("<F8>", self._hotkey_start)
        self.winfo_toplevel().bind("<F9>", self._hotkey_stop)

    def _build(self):
        t = self.t

        ctk.CTkLabel(
            self,
            text="Fishing",
            font=ctk.CTkFont(family="JetBrains Mono", size=15, weight="bold"),
            text_color=t["text_primary"],
        ).pack(anchor="w", pady=(0, 12))

        pack_row = ctk.CTkFrame(self, fg_color="transparent")
        pack_row.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            pack_row,
            text="Pathing Pack:",
            font=ctk.CTkFont(family="JetBrains Mono", size=12),
            text_color=t["text_primary"],
            width=160,
            anchor="w",
        ).pack(side="left")

        packs = Communication.get_packs()
        self.pack_dropdown = ctk.CTkOptionMenu(
            pack_row,
            values=packs if packs else ["No packs found"],
            variable=self.selected_pack,
            width=180,
            fg_color=t["bg_tertiary"],
            button_color=t["purple"],
            button_hover_color=t["accent"],
            text_color=t["text_primary"],
            font=ctk.CTkFont(family="JetBrains Mono", size=12),
        )
        self.pack_dropdown.pack(side="left")

        if packs:
            self.selected_pack.set(packs[0])

        self._count_row("Fishing Loop Count:", self.fishing_count)
        self._count_row("Sell Loop Count:", self.sell_count)

        debug_row = ctk.CTkFrame(self, fg_color="transparent")
        debug_row.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(
            debug_row,
            text="Debug Mode",
            font=ctk.CTkFont(family="JetBrains Mono", size=12),
            text_color=t["text_primary"],
            width=160,
            anchor="w",
        ).pack(side="left")

        ctk.CTkSwitch(
            debug_row,
            variable=self.debug,
            text="",
            onvalue=True,
            offvalue=False,
            progress_color=t["purple"],
            command=self._on_debug_toggle,
        ).pack(side="left")

        self.debug_label = ctk.CTkLabel(
            debug_row,
            text="Off",
            font=ctk.CTkFont(family="JetBrains Mono", size=11),
            text_color=t["text_secondary"],
        )
        self.debug_label.pack(side="left", padx=(8, 0))

        ctk.CTkFrame(self, height=1, fg_color=t["border"]).pack(fill="x", pady=(12, 16))

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(anchor="w")

        ctk.CTkButton(
            btn_row,
            text="Start (F8)",
            width=120,
            height=40,
            corner_radius=10,
            fg_color=t["purple"],
            hover_color=t["accent"],
            text_color=t["text_primary"],
            font=ctk.CTkFont(family="JetBrains Mono", size=13, weight="bold"),
            command=self._start,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_row,
            text="Stop (F9)",
            width=120,
            height=40,
            corner_radius=10,
            fg_color=t["bg_tertiary"],
            hover_color=t["danger"],
            border_width=1,
            border_color=t["border"],
            text_color=t["text_secondary"],
            font=ctk.CTkFont(family="JetBrains Mono", size=13, weight="bold"),
            command=self._stop,
        ).pack(side="left")

        self.status_label = ctk.CTkLabel(
            self,
            text="Idle",
            font=ctk.CTkFont(family="JetBrains Mono", size=11),
            text_color=t["text_secondary"],
        )
        self.status_label.pack(anchor="w", pady=(10, 0))

    def _count_row(self, label: str, var: ctk.IntVar):
        t = self.t
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(
            row,
            text=label,
            font=ctk.CTkFont(family="JetBrains Mono", size=12),
            text_color=t["text_primary"],
            width=160,
            anchor="w",
        ).pack(side="left")

        ctk.CTkEntry(
            row,
            textvariable=var,
            width=80,
            height=32,
            fg_color=t["bg_tertiary"],
            border_color=t["border"],
            border_width=1,
            text_color=t["text_primary"],
            font=ctk.CTkFont(family="JetBrains Mono", size=12),
            justify="center",
        ).pack(side="left")

    def _hotkey_start(self, event=None):
        self._start()

    def _hotkey_stop(self, event=None):
        self._stop()

    def _on_debug_toggle(self):
        enabled = self.debug.get()

        self.debug_label.configure(
            text="On" if enabled else "Off",
            text_color=self.t["success"] if enabled else self.t["text_secondary"],
        )

        if self.running:
            self.comm.set_debug(enabled)

    def _start(self):
        if self.running:
            return

        if not self._validate():
            return

        pack = self.selected_pack.get()

        if pack == "No packs found":
            self.status_label.configure(
                text="No pathing packs found in Pathing folder.",
                text_color=self.t["danger"],
            )
            return

        valid, missing = Communication.validate_pack(pack)
        if not valid:
            self.status_label.configure(
                text=f"Pack '{pack}' missing: {', '.join(missing)}",
                text_color=self.t["danger"],
            )
            return

        self.running = True
        self._countdown_remaining = 10
        self._countdown_start(pack)

    def _countdown_start(self, pack: str):
        if not self.running:
            return

        if self._countdown_remaining > 0:
            self.status_label.configure(
                text=f"Starting in {self._countdown_remaining}...",
                text_color=self.t["success"],
            )
            self._countdown_remaining -= 1
            self.after(1000, lambda: self._countdown_start(pack))
            return

        try:
            self.comm.send_command(
                command="fishing",
                pathing=pack,
                fishing_cycle=self.fishing_count.get(),
                sell_cycle=self.sell_count.get(),
                debug=self.debug.get(),
            )
        except FileNotFoundError as e:
            self.running = False
            self.status_label.configure(
                text=str(e),
                text_color=self.t["danger"],
            )
            return

        self.status_label.configure(
            text=f"Running - 0 / {self.fishing_count.get()} caught",
            text_color=self.t["success"],
        )

        self.after(200, self._poll_progress)

    def _stop(self):
        self.running = False
        self._countdown_remaining = 0
        self.comm.stop()

        self.status_label.configure(
            text="Idle",
            text_color=self.t["text_secondary"],
        )

    def _validate(self) -> bool:
        try:
            for var, name in [(self.fishing_count, "Fishing"), (self.sell_count, "Sell")]:
                if var.get() <= 0:
                    raise ValueError(name)
            return True
        except (ValueError, ctk.TclError) as e:
            self.status_label.configure(
                text=f"{e} count must be above 0.",
                text_color=self.t["danger"],
            )
            return False

    def _poll_progress(self):
        if not self.running:
            return

        state = self.comm.get_state()
        caught = state.get("CurrentCycle", 0)
        status = state.get("status", "idle")
        total = self.fishing_count.get()

        if status == "done":
            self.running = False
            self.status_label.configure(
                text=f"Done - {caught} / {total} caught",
                text_color=self.t["success"],
            )
            return

        if status == "idle":
            self.running = False
            self.status_label.configure(
                text="Idle",
                text_color=self.t["text_secondary"],
            )
            return

        self.status_label.configure(
            text=f"Running - {caught} / {total} caught",
            text_color=self.t["success"],
        )

        self.after(200, self._poll_progress)

    def update_progress(self, caught: int):
        total = self.fishing_count.get()

        self.status_label.configure(
            text=f"Running - {caught} / {total} caught",
            text_color=self.t["success"],
        )

        if caught >= total:
            self._stop()