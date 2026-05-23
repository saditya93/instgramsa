import requests

from scripts.quote_bank import INSTAGRAM_QUOTES
from scripts.config import load_dotenv_file
from scripts.quote_state import select_daily_quote

def fetch_quote():
    load_dotenv_file()
    local_quote = select_daily_quote(INSTAGRAM_QUOTES)

    try:
        source = local_quote
        if source and len(source["q"]) <= 140:
            return source
    except Exception as e:
        print("❌ Quote selection error:", e)

    return local_quote
