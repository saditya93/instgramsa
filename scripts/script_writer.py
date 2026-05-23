# scripts/script_writer.py
def write_script(news_items, fashion_item):
    script = "Welcome to your daily tech update.\n"
    for i, item in enumerate(news_items, 1):
        script += f"News {i}: {item['title']}\n"

    script += "\nToday's brand spotlight:\n"
    script += f"{fashion_item['title']}\nCheck it out now!\n"
    return script
