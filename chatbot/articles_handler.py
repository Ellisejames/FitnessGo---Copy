# chatbot/articles_handler.py

import json
import random
from typing import List, Dict

# Stores the last article shown per user
last_article_cache = {}


def load_articles():
    """Load articles from JSON with UTF-8 encoding"""
    try:
        # ✅ FIX: Add encoding='utf-8' to handle special characters
        with open('assets/articles.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: articles.json not found in assets folder")
        return {}
    except UnicodeDecodeError as e:
        print(f"Error loading articles (encoding issue): {e}")
        return {}
    except Exception as e:
        print(f"Error loading articles: {e}")
        return {}


def search_articles(query: str) -> List[Dict]:
    """Search articles by keyword"""
    articles_data = load_articles()

    if not articles_data:
        return []

    query = query.lower()
    results = []

    # Search in featured article
    featured = articles_data.get("featured", {})
    if any(keyword in featured.get("title", "").lower() or
           keyword in featured.get("body", "").lower()
           for keyword in query.split()):
        results.append(featured)

    # Search in popular articles
    for article in articles_data.get("popular", []):
        if any(keyword in article.get("title", "").lower() or
               keyword in article.get("body", "").lower()
               for keyword in query.split()):
            results.append(article)

    return results


def get_random_article() -> Dict:
    """Get a random article"""
    articles_data = load_articles()

    if not articles_data:
        return {}

    popular = articles_data.get("popular", [])

    if popular:
        return random.choice(popular)
    return articles_data.get("featured", {})


def format_article(article: Dict, user_id: int, full: bool = False) -> str:
    """Format article for display"""
    if not article:
        return "No articles available at the moment."

    # Save last article for "read more"
    last_article_cache[user_id] = article

    title = article.get("title", "Untitled")
    category = article.get("category", "")
    author = article.get("author", "")

    response = f"[b]{title}[/b]\n"
    response += f"{category}\n"
    response += f"{author}\n\n"

    body = article.get("body", "")

    if full:
        response += body
    else:
        preview = body[:300] + "..." if len(body) > 300 else body
        response += preview
        response += "\n\nWant to read more? Just ask!"

    return response


def get_full_article(user_id: int) -> str:
    """Return full content of last shown article"""
    article = last_article_cache.get(user_id)

    if not article:
        return "No article to continue. Ask me for an article first."

    return format_article(article, user_id=user_id, full=True)