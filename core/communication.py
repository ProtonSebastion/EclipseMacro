import json
import os
import subprocess
import time

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

COMM_PATH = os.path.join(BASE_DIR, "communication.json")
PATHING_PATH = os.path.join(BASE_DIR, "Pathing")

AHK_SCRIPT_PATH = os.path.join(BASE_DIR, "AHK", "Procedural.ahk")
AUTOHOTKEY_EXE = r"C:\Program Files\AutoHotkey\AutoHotkey.exe"

REQUIRED_FILES = [
    "FishingPathing.csv",
    "SellingPathing.csv",
]

DEFAULT_STATE = {
    "command": "idle",
    "pathing": "",
    "status": "idle",
    "FishingCycle": 0,
    "SellCycle": 0,
    "CurrentCycle": 0,
    "debug": False,
}


class Communication:
    def __init__(self):
        if not os.path.exists(COMM_PATH):
            self.reset()

    # ── State Um or something idk lowkey ─────────────────────────────────────────────
    def reset(self):
        self._write(DEFAULT_STATE.copy())

    # ── AHK ───────────────────────────────────────────────
    def start_ahk(self):
        if not os.path.exists(AHK_SCRIPT_PATH):
            raise FileNotFoundError(f"AHK script not found: {AHK_SCRIPT_PATH}")

        if not os.path.exists(AUTOHOTKEY_EXE):
            raise FileNotFoundError(f"AutoHotkey not found: {AUTOHOTKEY_EXE}")

        subprocess.Popen(
            [AUTOHOTKEY_EXE, AHK_SCRIPT_PATH],
            cwd=os.path.dirname(AHK_SCRIPT_PATH),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def exit_ahk(self):
        debug = self._read().get("debug", False)

        data = DEFAULT_STATE.copy()
        data["command"] = "exit"
        data["status"] = "idle"
        data["debug"] = debug

        self._write(data)

    # ── Read / Write ──────────────────────────────────────
    def _write(self, data: dict):
        temp_path = COMM_PATH + ".tmp"

        with open(temp_path, "w") as f:
            json.dump(data, f, indent=2)

        os.replace(temp_path, COMM_PATH)

    def _read(self) -> dict:
        for _ in range(5):
            try:
                with open(COMM_PATH, "r") as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                time.sleep(0.05)

        return DEFAULT_STATE.copy()

    # ── Commands Specifically For AHK ──────────────────────────────────────────
    def send_command(
        self,
        command: str,
        pathing: str,
        fishing_cycle: int,
        sell_cycle: int,
        debug: bool = False,
    ):
        self.start_ahk()

        self._write({
            "command": command,
            "pathing": pathing,
            "status": "busy",
            "FishingCycle": fishing_cycle,
            "SellCycle": sell_cycle,
            "CurrentCycle": 0,
            "debug": debug,
        })

    def stop(self):
        self.exit_ahk()

    def set_debug(self, debug: bool):
        data = self._read()
        data["debug"] = debug
        self._write(data)

    def get_status(self) -> str:
        return self._read().get("status", "idle")

    def is_debug(self) -> bool:
        return self._read().get("debug", False)

    def get_state(self) -> dict:
        return self._read()

    # ── Pathing for yeah ───────────────────────────────────────────
    @staticmethod
    def get_packs() -> list:
        if not os.path.exists(PATHING_PATH):
            return []

        return [
            f for f in os.listdir(PATHING_PATH)
            if os.path.isdir(os.path.join(PATHING_PATH, f))
        ]

    @staticmethod
    def validate_pack(pack_name: str) -> tuple:
        pack_path = os.path.join(PATHING_PATH, pack_name)

        missing = [
            f for f in REQUIRED_FILES
            if not os.path.exists(os.path.join(pack_path, f))
        ]

        return len(missing) == 0, missing

    # ── Polling and a bit of waiting ofc ───────────────────────────────────────────
    def wait_for_done(self, timeout: int = 300) -> bool:
        start = time.time()

        while time.time() - start < timeout:
            if self.get_status() == "done":
                return True
            time.sleep(0.1)

        return False

    def wait_for_status(self, status: str, timeout: int = 300) -> bool:
        start = time.time()

        while time.time() - start < timeout:
            if self.get_status() == status:
                return True
            time.sleep(0.1)

        return False