from ...app.config import ROOT_DIR

BOT_INFO_PATH = ROOT_DIR / "templates" / "bot_info.txt"
INFO = BOT_INFO_PATH.read_text(encoding="utf-8").strip()

def info_text() -> str:
    return INFO