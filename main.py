import asyncio
import json
import logging
from datetime import datetime
from os import getenv
from sys import stdout

from dotenv import load_dotenv

from agents.gpt import GPTClient
from agents.prompt import get_prompt
from database.article import add_article, get_article_by_num, get_existing_articles
from database.orm import Link, Session, init_db
from utils.check_image import download_image, resize_image
from utils.html_parser import get_images_by_url
from utils.json_parser import parse_text

session: Session = None


async def gpt_request(
    prompt,
    model="gpt-4o-mini",
    system_prompt="You are a helpful assistant.",
):
    async with GPTClient(api_key=getenv("api_key"), model=model) as client:
        return await client.send_request(prompt, system_prompt=system_prompt)


async def gpt_image(
    prompt,
    image,
    url,
    model="gpt-4o-mini",
):
    async with GPTClient(api_key=getenv("api_key"), model=model) as client:
        return await client.send_request(prompt, [(image, url)])


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


async def choose_article():
    non_existing_themes = get_existing_articles(session, False, True)

    choose_prompt = get_prompt(
        "choose",
        today=datetime.now().strftime("%d %B %Y"),
        themes=non_existing_themes,
    )

    response = await gpt_request(choose_prompt)

    return int(response) - 1


async def genarete_post(theme):
    article_text_prompt = get_prompt("write_post", theme=theme)
    response = await gpt_request(article_text_prompt)

    article_prompt = get_prompt("telegram_formatting", article=response)
    response = await gpt_request(article_prompt)

    return response


async def add_article_links(article):
    photos_prompt = get_prompt(
        "get_photo",
        theme=article.theme,
    )
    response = await gpt_request(
        photos_prompt,
        "gpt-4o-mini-search-preview",
    )

    links = parse_text(response)

    for link in links:
        session.add(Link(article_id=article.id, link=link))


async def find_best_image(text, image_links):
    check_image_prompt = get_prompt(
        "check_image",
        post=text,
    )
    images = []

    for image_link in image_links:
        downloaded = await download_image(image_link)
        resized = resize_image(downloaded)

        response = await gpt_image(check_image_prompt, resized, image_link)
        images.append((parse_text(response), image_link))

    return max(images, key=lambda x: x[0])[1]


async def get_image(theme, text, links):
    links = [link.link for link in links]
    image_links = []

    for link in links:
        url_images = await get_images_by_url(link)

        if url_images:
            image_prompt = get_prompt(
                "valid_images",
                theme=theme,
                images=json.dumps(url_images),
                max_images=min(8, len(url_images)),
            )

            response = await gpt_request(image_prompt)
            image_links.extend(parse_text(response))

    if not image_links:
        return

    image = await find_best_image(text, image_links)
    logging.info(image)

    return image


async def main():
    # await add_themes()
    # article_number = await choose_article()

    article_number = 1

    article = get_article_by_num(session, article_number)

    # article.text = await genarete_post(article.theme)
    # await add_article_links(article)

    # image = await get_image(article.theme, article.text, article.links)
    # if image:
    #     article.image = image
    # session.commit()

    text = article.text
    image = article.image


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=stdout)
    load_dotenv()
    session = init_db()

    asyncio.run(main())
