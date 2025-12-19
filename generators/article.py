import logging

from agents.prompt import get_prompt
from database.article import add_article, get_existing_articles
from database.orm import Hashtag
from generators.ai import gpt_request
from generators.config import session
from generators.theme import choose_theme
from telegram.formatter import format_text
from utils.json_parser import parse_text


async def create_new_article(day_time):
    theme = choose_theme(day_time)
    logging.info(f"Chosen theme: {theme.name}")

    existing_themes = get_existing_articles(session, maximum=200)

    choose_prompt = get_prompt(
        "choose_theme",
        theme=theme.name,
        existingThemes=existing_themes,
        format=get_prompt("choose_theme_format"),
    )

    response = await gpt_request(choose_prompt, "gpt-4o")
    article_dict = parse_text(response, {})

    if article_dict:
        article = add_article(
            session,
            name=article_dict["name"],
            level=int(article_dict["level"]),
            theme=article_dict["theme"],
            time=int(article_dict["time"]),
        )
        return article

    return


async def generate_post(theme):
    hashtags = session.query(Hashtag).all()
    hashtag_names = [hashtag.name for hashtag in hashtags]

    article_text_prompt = get_prompt(
        "write_post",
        theme=theme,
        hashtags="\n".join(hashtag_names),
        format=get_prompt("post_format"),
    )
    response = await gpt_request(article_text_prompt, "gpt-4o")

    formatted = format_text(response)

    for word in formatted.split():
        if word.startswith("#"):
            if not word[1:] in hashtag_names:
                hashtag = Hashtag(name=word[1:])
                session.add(hashtag)
    session.commit()

    return formatted
