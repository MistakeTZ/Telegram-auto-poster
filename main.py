import asyncio
import logging
from datetime import datetime
from os import getenv
from sys import stdout

from dotenv import load_dotenv

from agents.gpt import GPTClient
from agents.prompt import get_prompt
from database.article import add_article, get_article_by_num, get_existing_articles
from database.orm import Link, Session, init_db
from utils.json_parser import parse_text

session: Session = None


async def gpt_request(prompt, model="gpt-4o-mini"):
    async with GPTClient(api_key=getenv("api_key"), model=model) as client:
        return await client.send_request(prompt)


async def add_themes():
    actual_themes_prompt = get_prompt(
        "actual_events",
        today=datetime.now().strftime("%d %B %Y"),
    )

    response = await gpt_request(actual_themes_prompt)

    events = parse_text(response)
    existing = get_existing_articles(session)

    new_post_prompt = get_prompt(
        "themes",
        actualEvents="\n".join(events),
        existingThemes=existing,
        format=get_prompt("themes_format"),
    )

    response = await gpt_request(new_post_prompt)

    themes = parse_text(response)

    for theme in themes:
        add_article(session, theme["topic"], theme["level"], theme["type"])
    session.commit()


async def main():
    # await add_themes()

    # non_existing_themes = get_existing_articles(session, False, True)

    # choose_prompt = get_prompt(
    #     "choose",
    #     today=datetime.now().strftime("%d %B %Y"),
    #     themes=non_existing_themes,
    # )

    # response = await gpt_request(choose_prompt)

    # chosen_theme = int(response) - 1
    chosen_theme = 1

    article = get_article_by_num(session, chosen_theme)

    # photos_prompt = get_prompt(
    #     "get_photo",
    #     theme=article.theme,
    # )
    # response = await gpt_request(
    #     photos_prompt,
    #     "gpt-4o-mini-search-preview",
    # )

    # links = parse_text(response)

    # for link in links:
    #     session.add(Link(article_id=article.id, link=link))
    # session.commit()

    # article_text_prompt = get_prompt("write_post", theme=article.theme)

    # response = await gpt_request(article_text_prompt)

    # article_prompt = get_prompt("telegram_formatting", article=response)

    # response = await gpt_request(article_prompt)

    # text = response
    # article.text = text
    # session.commit()

    links = [link.link for link in article.links]
    text = article.text
    print(text, links)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=stdout)
    load_dotenv()
    session = init_db()

    asyncio.run(main())
