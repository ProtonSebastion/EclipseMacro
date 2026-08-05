import ctypes
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("EclipseMacro")

import customtkinter as ctk
from ui.main_window import MainWindow
from core.config import load as load_config, save as save_config
from ui.Tabs.webhook import startup_notification


def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    cfg = load_config()
    save_config(cfg["theme"], cfg["minimize_to_tray"])

    app = MainWindow()
    app.iconbitmap(r"ui\icons\EclipseLogo.ico")

    app.after(1000, startup_notification)

    app.mainloop()


if __name__ == "__main__":
    main()