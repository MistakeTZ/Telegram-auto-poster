import asyncio
import logging
from datetime import datetime
from os import getenv
from sys import stdout

from dotenv import load_dotenv

from agents.gpt import GPTClient
from agents.prompt import get_prompt
from database.article import add_article, get_article_by_num, get_existing_articles
from database.orm import Session, init_db
from utils.json_parser import parse_text

session: Session = None


async def main():
    actual_themes_prompt = get_prompt(
        "actual_events",
        today=datetime.now().strftime("%d %B %Y"),
    )

    async with GPTClient(api_key=getenv("api_key"), model="gpt-4o-mini") as client:
        response = await client.send_request(actual_themes_prompt)

    events = parse_text(response)
    existing = get_existing_articles(session)

    new_post_prompt = get_prompt(
        "themes",
        actualEvents="\n".join(events),
        existingThemes=existing,
        format=get_prompt("themes_format"),
    )

    async with GPTClient(api_key=getenv("api_key"), model="gpt-4o-mini") as client:
        response = await client.send_request(new_post_prompt)

    themes = parse_text(response)

    for theme in themes:
        add_article(session, theme["topic"], theme["level"], theme["type"])
    session.commit()

    non_existing_themes = get_existing_articles(session, False, True)

    choose_prompt = get_prompt(
        "choose",
        today=datetime.now().strftime("%d %B %Y"),
        themes=non_existing_themes,
    )

    async with GPTClient(api_key=getenv("api_key"), model="gpt-4o-mini") as client:
        response = await client.send_request(choose_prompt)

    chosen_theme = int(response) - 1

    article = get_article_by_num(session, chosen_theme)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=stdout)
    load_dotenv()
    session = init_db()

    asyncio.run(main())
