from pathlib import Path

BOT_DATA_FOLDER = Path(__file__).resolve().parent.parent.parent.parent / "data"
BOT_DATA_FOLDER.mkdir(parents=True, exist_ok=True)
BOT_DATA_PATH = BOT_DATA_FOLDER / "bot_data_cache.json"

if not BOT_DATA_PATH.exists():
    with open(BOT_DATA_PATH, mode="x", encoding="utf-8") as file:
        file.write("{}")

filter_configurations = {
    "websockets_filter": {
        "input_data_key": "recieved_websockets"
    },
    "invoices_filter": {
        "input_data_key": "pending_invoices",
        "output_data_key": "invoices_to_recover",
        "params_to_record": ["id"]
    },
    "subscriptions_filter": {
        "input_data_key": "subscriptions",
        "output_data_key": "subscriptions_to_recover",
        "params_to_record": []
    },
    "user_flags_filter": {
        "input_data_key": "user_flags"
    }
}