import asyncio
import logging
from datetime import datetime
from os import getenv

from agents.prompt import get_prompt
from generators.ai import gen_image
from generators.article import create_new_article, generate_post
from generators.config import session
from telegram.poster import post_and_database
from utils.check_image import download_image
from utils.file_handler import write_to_articles


async def send_article(post_time: datetime, day_time="any"):
    start_time = datetime.now()

    article = await create_new_article(day_time)
    if not article:
        logging.error("Failed to create article")
        return

    article.text = await generate_post(article.name)

    prompt = get_prompt("gen_image", text=article.text)
    image = await gen_image(prompt)

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

    write_to_articles()
