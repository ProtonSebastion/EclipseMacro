import configparser
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "settings.ini")

DEFAULTS = {
    "theme":            "Eclipse",
    "minimize_to_tray": False,
    "webhook_url":      "",
    "mention_everyone": False,
    "mention_user_id":  "",
}


def load() -> dict:
    
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_PATH):
        config.read(CONFIG_PATH)

    return {
        "theme":            config.get("Settings", "theme",              fallback=DEFAULTS["theme"]),
        "minimize_to_tray": config.getboolean("Settings", "minimize_to_tray", fallback=DEFAULTS["minimize_to_tray"]),
        "webhook_url":      config.get("Webhook", "url",                 fallback=DEFAULTS["webhook_url"]),
        "mention_everyone": config.getboolean("Webhook", "mention_everyone",  fallback=DEFAULTS["mention_everyone"]),
        "mention_user_id":  config.get("Webhook", "mention_user_id",     fallback=DEFAULTS["mention_user_id"]),
    }


def save(theme: str, minimize_to_tray: bool):
    """Save only [Settings] — never touches [Webhook]."""
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_PATH):
        config.read(CONFIG_PATH)

    config["Settings"] = {
        "theme":            theme,
        "minimize_to_tray": str(minimize_to_tray),
    }

    with open(CONFIG_PATH, "w") as f:
        config.write(f)


def save_webhook(url: str,
                 mention_everyone: bool = False,
                 mention_user_id:  str  = ""):
    """Save only [Webhook] — never touches [Settings]."""
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_PATH):
        config.read(CONFIG_PATH)

    config["Webhook"] = {
        "url":              url,
        "mention_everyone": str(mention_everyone),
        "mention_user_id":  mention_user_id,
    }

    with open(CONFIG_PATH, "w") as f:
        config.write(f)


def reset_defaults():
    """Wipe settings.ini and restore all defaults."""
    config = configparser.ConfigParser()

    config["Settings"] = {
        "theme":            DEFAULTS["theme"],
        "minimize_to_tray": str(DEFAULTS["minimize_to_tray"]),
    }
    config["Webhook"] = {
        "url":              DEFAULTS["webhook_url"],
        "mention_everyone": str(DEFAULTS["mention_everyone"]),
        "mention_user_id":  DEFAULTS["mention_user_id"],
    }

    with open(CONFIG_PATH, "w") as f:
        config.write(f)