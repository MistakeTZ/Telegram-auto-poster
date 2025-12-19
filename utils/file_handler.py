import json
from pathlib import Path

from database.article import Article
from generators.config import session


def write_to_articles():
    articles = session.query(Article).filter_by(is_posted=True).all()

    all_articles = [
        {
            "name": article.name,
            "photo": article.photo,
            "photo_id": article.posted_photo,
            "link": f"https://t.me/{article.posted_channel[1:]}/{article.posted_id}",
            "text": get_text(article.text),
            "hashtags": get_hashtags(article.text),
        }
        for article in articles
    ]

    Path("recipes.json").write_text(
        json.dumps(all_articles, ensure_ascii=False, indent=4),
        encoding="utf-8",
    )


def get_text(text):
    text = text.split("<b>Рецепт:</b>")[0].strip()
    if len(text) > 900:
        chanks = text.split("\n\n")
        text = ""

        for chank in chanks:
            if len(text) + len(chank) < 900:
                text += chank + "\n\n"
            else:
                break
        text = text.strip()

    return text


def get_hashtags(text):
    hashtags = []

    for word in text.split():
        if word.startswith("#"):
            if not word[1:] in hashtags:
                hashtags.append(word[1:])

    return hashtags
