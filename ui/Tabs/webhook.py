import os
import threading
import customtkinter as ctk
from core.config import load as load_config, save_webhook

WEBHOOK_ICON_DIR = os.path.join(os.path.dirname(__file__), "..", "icons", "webhook")

EVENT_IMAGES = {
    "notify_macro_started": "macro_started.png",
    "notify_macro_stopped": "macro_stopped.png",
    "testing_macro":        "Testing.png",
}

EVENT_COLORS = {
    "notify_macro_started": "39ff14",
    "notify_macro_stopped": "dc143c",
    "testing_macro":        "cd853f",
}

BIOMES = ["Starfall", "Windy"]


class WebhookTab(ctk.CTkFrame):
    def __init__(self, parent, t: dict):
        super().__init__(parent, fg_color="transparent")
        self.t    = t
        self.cfg  = load_config()
        self.mention_everyone_var = ctk.BooleanVar(value=self.cfg.get("mention_everyone", False))
        self.biome_vars           = {biome: ctk.BooleanVar(value=False) for biome in BIOMES}
        self.selected_item        = ctk.StringVar(value="Biome Randomizer")
        self.user_id_entry        = None
        self._build()

    # ── Layout ────────────────────────────────────────────
    def _build(self):
        t = self.t

        ctk.CTkLabel(
            self,
            text="Discord Webhook URL",
            font=ctk.CTkFont(family="JetBrains Mono", size=11),
            text_color=t["text_secondary"],
        ).pack(anchor="w", pady=(0, 4))

        url_row = ctk.CTkFrame(self, fg_color="transparent")
        url_row.pack(fill="x", pady=(0, 12))

        self.url_entry = ctk.CTkEntry(
            url_row,
            placeholder_text="https://discord.com/api/webhooks/...",
            fg_color=t["bg_tertiary"],
            border_color=t["border"],
            border_width=1,
            text_color=t["text_primary"],
            placeholder_text_color=t["text_secondary"],
            font=ctk.CTkFont(family="JetBrains Mono", size=11),
            height=34,
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        if self.cfg.get("webhook_url"):
            self.url_entry.insert(0, self.cfg["webhook_url"])

        self.url_entry.bind("<FocusOut>", lambda e: self._save_all())
        self.url_entry.bind("<Return>",   lambda e: self._save_all())

        ctk.CTkButton(
            url_row,
            text="Test",
            width=60, height=34, corner_radius=8,
            fg_color=t["purple"],
            hover_color=t["accent"],
            text_color=t["text_primary"],
            font=ctk.CTkFont(family="JetBrains Mono", size=11),
            command=self._test_webhook,
        ).pack(side="left")

        ctk.CTkFrame(self, height=1, fg_color=t["border"]).pack(fill="x", pady=(0, 12))

        selector_row = ctk.CTkFrame(self, fg_color="transparent")
        selector_row.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            selector_row,
            text="Select Item",
            font=ctk.CTkFont(family="JetBrains Mono", size=11),
            text_color=t["text_secondary"],
        ).pack(side="left", padx=(0, 12))

        ctk.CTkOptionMenu(
            selector_row,
            values=["Biome Randomizer", "Discord Mention"],
            variable=self.selected_item,
            command=self._on_select,
            fg_color=t["bg_tertiary"],
            button_color=t["purple"],
            button_hover_color=t["accent"],
            text_color=t["text_primary"],
            font=ctk.CTkFont(family="JetBrains Mono", size=12),
            width=180,
        ).pack(side="left")

        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True)

        self._build_biomes()

    # ── Save File Lol ──────────────────────────────────────────────
    def _save_all(self, user_id: str = ""):
        save_webhook(
            url=self.url_entry.get().strip(),
            mention_everyone=self.mention_everyone_var.get(),
            mention_user_id=user_id,
        )

    # ── Selector ──────────────────────────────────────────
    def _on_select(self, choice: str):
        if choice == "Biome Randomizer":
            self._build_biomes()
        elif choice == "Discord Mention":
            self._build_mention()

    # ── Biome panel ───────────────────────────────────────
    def _build_biomes(self):
        for w in self.content_frame.winfo_children():
            w.destroy()

        t = self.t
        ctk.CTkLabel(
            self.content_frame,
            text="Notify on Biome",
            font=ctk.CTkFont(family="JetBrains Mono", size=11),
            text_color=t["text_secondary"],
        ).pack(anchor="w", pady=(0, 8))

        for biome in BIOMES:
            row = ctk.CTkFrame(self.content_frame, fg_color="transparent")
            row.pack(fill="x", pady=3)

            ctk.CTkLabel(
                row, text=biome,
                font=ctk.CTkFont(family="JetBrains Mono", size=12),
                text_color=t["text_primary"],
                width=160, anchor="w",
            ).pack(side="left")

            ctk.CTkSwitch(
                row, text="",
                variable=self.biome_vars[biome],
                onvalue=True, offvalue=False,
                progress_color=t["purple"],
                button_color=t["accent"],
                button_hover_color=t["accent"],
                fg_color=t["bg_primary"],
                width=44,
                command=self._save_all,
            ).pack(side="left")

    # ── Mention panel ─────────────────────────────────────
    def _build_mention(self):
        for w in self.content_frame.winfo_children():
            w.destroy()

        t = self.t
        ctk.CTkLabel(
            self.content_frame,
            text="Discord Mention",
            font=ctk.CTkFont(family="JetBrains Mono", size=11),
            text_color=t["text_secondary"],
        ).pack(anchor="w", pady=(0, 8))

        everyone_row = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        everyone_row.pack(fill="x", pady=3)

        ctk.CTkLabel(
            everyone_row, text="@everyone",
            font=ctk.CTkFont(family="JetBrains Mono", size=12),
            text_color=t["text_primary"],
            width=160, anchor="w",
        ).pack(side="left")

        ctk.CTkSwitch(
            everyone_row, text="",
            variable=self.mention_everyone_var,
            onvalue=True, offvalue=False,
            progress_color=t["purple"],
            button_color=t["accent"],
            button_hover_color=t["accent"],
            fg_color=t["bg_primary"],
            width=44,
            command=lambda: self._save_all(
                self.user_id_entry.get().strip() if self.user_id_entry else ""
            ),
        ).pack(side="left")

        ctk.CTkFrame(self.content_frame, height=10, fg_color="transparent").pack()

        ctk.CTkLabel(
            self.content_frame,
            text="User ID to Mention",
            font=ctk.CTkFont(family="JetBrains Mono", size=11),
            text_color=t["text_secondary"],
        ).pack(anchor="w", pady=(0, 4))

        self.user_id_entry = ctk.CTkEntry(
            self.content_frame,
            placeholder_text="e.g. 123456789012345678",
            fg_color=t["bg_tertiary"],
            border_color=t["border"],
            border_width=1,
            text_color=t["text_primary"],
            placeholder_text_color=t["text_secondary"],
            font=ctk.CTkFont(family="JetBrains Mono", size=11),
            height=34,
        )
        self.user_id_entry.pack(fill="x")

        if self.cfg.get("mention_user_id"):
            self.user_id_entry.insert(0, self.cfg["mention_user_id"])

        self.user_id_entry.bind(
            "<FocusOut>", lambda e: self._save_all(self.user_id_entry.get().strip())
        )
        self.user_id_entry.bind(
            "<Return>", lambda e: self._save_all(self.user_id_entry.get().strip())
        )

    # ── Test webhook ──────────────────────────────────────
    def _test_webhook(self):
        url = self.url_entry.get()
        if not url.strip():
            self._show_toast("⚠  Please enter a webhook URL first.", error=True)
            return
        threading.Thread(target=self._send_test, args=(url,), daemon=True).start()

    def _send_test(self, url: str):
        try:
            from discord_webhook import DiscordWebhook, DiscordEmbed

            webhook = DiscordWebhook(url=url.strip(), username="EclipseMacro")
            embed   = DiscordEmbed(
                title="**WEBHOOK TEST SUCCESSFUL**",
                color="cd853f",
                description="This is a test message. All Notifications are ready.",
            )
            embed.set_footer(text="Project Eclipse v0.1.0")
            embed.set_timestamp()

            img_path = os.path.join(WEBHOOK_ICON_DIR, "Testing.png")
            if os.path.exists(img_path):
                with open(img_path, "rb") as f:
                    webhook.add_file(file=f.read(), filename="Testing.png")
                embed.set_thumbnail(url="attachment://Testing.png")

            webhook.add_embed(embed)
            resp = webhook.execute()

            if resp.status_code in (200, 204):
                self.after(0, lambda: self._show_toast("✓  Test message sent!"))
            else:
                self.after(0, lambda: self._show_toast(f"✕  HTTP {resp.status_code}", error=True))

        except ImportError:
            self.after(0, lambda: self._show_toast("✕  discord-webhook not installed!", error=True))
        except Exception as e:
            self.after(0, lambda: self._show_toast(f"✕  Error: {e}", error=True))

    # ── Toast ─────────────────────────────────────────────
    def _show_toast(self, message: str, error: bool = False):
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkLabel) and getattr(widget, "_is_toast", False):
                widget.destroy()

        toast = ctk.CTkLabel(
            self, text=message,
            font=ctk.CTkFont(family="JetBrains Mono", size=11),
            text_color=self.t["danger"] if error else self.t["success"],
        )
        toast._is_toast = True
        toast.pack(anchor="w", pady=(8, 0))
        self.after(3000, toast.destroy)


# ── Module-level helpers (used by Main.py / _quit_app) ───
def startup_notification():
    send_notification("notify_macro_started", "✦ Macro Turned On")


def send_notification(event_key: str, description: str):
    cfg = load_config()
    url = cfg.get("webhook_url", "").strip()
    if not url:
        return
    threading.Thread(
        target=_send_embed,
        args=(url, description, event_key),
        daemon=True,
    ).start()


def _send_embed(url: str, description: str, event_key: str = ""):
    try:
        from discord_webhook import DiscordWebhook, DiscordEmbed

        webhook = DiscordWebhook(url=url, username="EclipseMacro")
        color   = EVENT_COLORS.get(event_key, "fcc200").replace("#", "")
        embed   = DiscordEmbed(title=description, color=color)
        embed.set_footer(text="Project Eclipse v0.1.0")
        embed.set_timestamp()

        img_file = EVENT_IMAGES.get(event_key, "")
        img_path = os.path.join(WEBHOOK_ICON_DIR, img_file)

        if img_file and os.path.exists(img_path):
            with open(img_path, "rb") as f:
                webhook.add_file(file=f.read(), filename=img_file)
            embed.set_thumbnail(url=f"attachment://{img_file}")

        webhook.add_embed(embed)
        resp = webhook.execute()
        print(f"[Webhook] Response: {resp.status_code}")

    except Exception as e:
        print(f"[Webhook] ERROR: {e}")