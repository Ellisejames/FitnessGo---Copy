# chatbot/motivation_handler.py

import json
import random


def load_quotes():
    """Load motivational quotes from JSON with UTF-8 encoding"""
    try:
        # ✅ FIX: Add encoding='utf-8'
        with open('assets/quotes.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: quotes.json not found in assets folder")
        return []
    except Exception as e:
        print(f"Error loading quotes: {e}")
        return []


def get_random_quote() -> str:
    """Get a random motivational quote"""
    quotes = load_quotes()

    if not quotes:
        return "[i]You've got this! Keep pushing forward, you can stop but don't ever give up![/i]"

    quote_data = random.choice(quotes)
    quote = quote_data.get("q", "")
    author = quote_data.get("a", "Unknown")

    return f" [i]\"{quote}\"[/i]\n\n— {author}"