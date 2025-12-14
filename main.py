import asyncio
import json
import logging
from datetime import datetime, timedelta
from os import getenv
from sys import stdout, argv

from dotenv import load_dotenv

from agents.gpt import GPTClient
from agents.prompt import get_prompt
from database.article import (
    add_article,
    get_article_by_num,
    get_existing_articles,
)
from database.orm import Link, Session, init_db
from telegram.formatter import format_text
from telegram.poster import post_and_database
from utils.check_image import download_image, resize_image
from utils.html_parser import get_image_size, get_images_by_url
from utils.json_parser import parse_text

session: Session = None
start_time = datetime.now()


async def gpt_request(
    prompt,
    model="gpt-4o-mini",
    system_prompt="You are a helpful assistant.",
):
    async with GPTClient(api_key=getenv("api_key"), model=model) as client:
        return await client.send_request(
            prompt,
            system_prompt=system_prompt,
        )


async def gpt_image(
    prompt,
    image,
    url,
    model="gpt-4o-mini",
):
    async with GPTClient(api_key=getenv("api_key"), model=model) as client:
        return await client.send_request(prompt, [(image, url)], max_tokens=800)


async def add_themes():
    # actual_themes_prompt = get_prompt(
    #     "actual_events",
    #     today=datetime.now().strftime("%d %B %Y"),
    # )

    # response = await gpt_request(actual_themes_prompt)

    # events = parse_text(response, ["определи сам"])
    existing = get_existing_articles(session, maximum=100)

    new_post_prompt = get_prompt(
        "themes",
        today=datetime.now().strftime("%d %B %Y"),
        # actualEvents="\n".join(events),
        existingThemes=existing,
        format=get_prompt("themes_format"),
    )

    response = await gpt_request(new_post_prompt, "gpt-4o")

    themes = parse_text(response, [])

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

    response = await gpt_request(choose_prompt, "gpt-4o")

    return int(response) - 1


async def genarete_post(theme):
    article_text_prompt = get_prompt(
        "write_post", theme=theme, today=datetime.now().strftime("%d %B %Y"),
    )
    response = await gpt_request(article_text_prompt, "gpt-4o")
    response = response.replace("*", "")

    article_prompt = get_prompt("telegram_formatting", article=response)
    response = await gpt_request(article_prompt, "gpt-4o")

    formatted = format_text(response)
    return formatted


async def add_article_links(article):
    photos_prompt = get_prompt(
        "get_photo",
        theme=article.theme,
    )
    response = await gpt_request(
        photos_prompt,
        "gpt-4o-search-preview",
    )

    links = parse_text(response, [])

    for link in links:
        session.add(Link(article_id=article.id, link=link))


async def find_best_image(text, image_links):
    check_image_prompt = get_prompt(
        "check_image",
        post=text,
    )
    images = []
    logging.info(image_links)

    for image_link in image_links:
        try:
            downloaded = await download_image(image_link)
            resized = resize_image(downloaded)

            response = await gpt_image(check_image_prompt, resized, image_link)
            image_percentage = parse_text(response, 0)
            images.append((image_percentage, image_link))
        except Exception as e:
            logging.warning(e)

    logging.info(images)

    max_value = max(images, key=lambda x: x[0])[0]
    images_with_max = [image[1] for image in images if image[0] == max_value]
    logging.info(images_with_max)

    max_size = 0
    post_image = None

    for image in images_with_max:
        size = await get_image_size(image)
        if size >= max_size:
            max_size = size
            post_image = image

    return post_image


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
                max_images=min(4, len(url_images)),
            )

            response = await gpt_request(image_prompt)
            image_links.extend(parse_text(response, []))

    if not image_links:
        return

    image = await find_best_image(text, image_links)
    logging.info(image)

    return image


async def send_article(post_time: datetime):
    start_time = datetime.now()
    await add_themes()
    article_number = await choose_article()

    article = get_article_by_num(session, article_number)

    article.text = await genarete_post(article.theme)
    await add_article_links(article)

    image = await get_image(article.theme, article.text, article.links)
    if image:
        article.photo = image
    session.commit()

    text = article.text + getenv("article_end").replace("\\n", "\n")
    image = article.photo

    image_bytes = None
    if image:
        try:
            image_bytes = await download_image(image)
        except Exception as e:
            logging.warning(e)

    logging.info("Article ready in %s", (datetime.now() - start_time).total_seconds())
    if datetime.now() < post_time:
        await asyncio.sleep((post_time - datetime.now()).total_seconds())

    await post_and_database(
        article,
        getenv("channel"),
        getenv("token"),
        text,
        image_bytes,
    )
    session.commit()
    logging.info("Article sent")


async def main():
    if "send_now" in argv:
        logging.info("Sending article now")
        await send_article(datetime.now())

    else:
        send_times = [int(time) for time in getenv("send_times").split(",")]
        logging.info(send_times)

        while True:
            now = datetime.now()
            current_hour = now.hour

            future_hours_today = [h for h in send_times if h > current_hour]

            if future_hours_today:
                next_hour = future_hours_today[0]
                next_day_offset = 0
            else:
                next_hour = send_times[0]
                next_day_offset = 1

            target_time = datetime(
                year=now.year,
                month=now.month,
                day=now.day,
                hour=next_hour,
                minute=0,
                second=0,
                microsecond=0,
            )

            target_time += timedelta(days=next_day_offset)

            if target_time <= now:
                target_time += timedelta(days=1)
                target_time = target_time.replace(hour=send_times[0])

            wait_seconds = (target_time - timedelta(minutes=5) - now).total_seconds()
            if wait_seconds < 0:
                wait_seconds = 0

            logging.info(
                f"Next send scheduled for {target_time} (in {wait_seconds:.0f} seconds)"
            )

            await asyncio.sleep(wait_seconds)

            await send_article(target_time)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=stdout)
    load_dotenv()
    session = init_db()

    asyncio.run(main())
