import json
import os
import random
from datetime import date


STATE_FILE = "output/quote_state.json"


def _ensure_output_dir():
    os.makedirs("output", exist_ok=True)


def _load_state():
    if not os.path.exists(STATE_FILE):
        return {"daily_quotes": {}, "used_quotes": []}

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as handle:
            data = json.load(handle)
            if "daily_quotes" not in data:
                data["daily_quotes"] = {}
            if "used_quotes" not in data:
                data["used_quotes"] = []
            return data
    except Exception:
        return {"daily_quotes": {}, "used_quotes": []}


def _save_state(state):
    _ensure_output_dir()
    with open(STATE_FILE, "w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=2, ensure_ascii=False)


def select_daily_quote(quotes):
    if not quotes:
        return None

    today = date.today().isoformat()
    state = _load_state()

    if today in state["daily_quotes"]:
        return state["daily_quotes"][today]

    used_quotes = set(state["used_quotes"])
    available_quotes = [quote for quote in quotes if quote["q"] not in used_quotes]

    if not available_quotes:
        used_quotes = set()
        available_quotes = list(quotes)

    selected = random.choice(available_quotes)
    state["daily_quotes"][today] = selected
    state["used_quotes"] = sorted(used_quotes | {selected["q"]})
    _save_state(state)
    return selected
