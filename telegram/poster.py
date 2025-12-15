import logging
from datetime import datetime
from typing import Optional

import aiohttp

from database.orm import Article


async def post_and_database(
    article: Article,
    channel: str | int,
    token: str,
    text: str,
    image: Optional[bytes] = None,
):
    logging.info("Posting to channel %s: %s", channel, text)
    post = await post_to_channel(channel, token, text, image)

    if post.get("ok"):
        logging.info(post)
        article.is_posted = True
        article.posted_channel = channel
        article.posted_id = post["result"]["message_id"]
        article.posted_time = datetime.fromtimestamp(post["result"]["date"])
        if image:
            article.posted_photo = post["result"]["photo"][-1]["file_id"]
    else:
        logging.error(post)


async def post_to_channel(
    channel: str | int,
    token: str,
    text: str,
    image: Optional[bytes] = None,
):
    """
    Posts a message (with optional image as photo + caption) to a Telegram channel using the Bot API.
    """
    base_url = f"https://api.telegram.org/bot{token}"
    photo = None

    if image:
        method = "sendPhoto"
        url = f"{base_url}/{method}"

        form = aiohttp.FormData()
        form.add_field("chat_id", str(channel))

        if len(text) <= 1024:
            form.add_field("caption", text)

        form.add_field("parse_mode", "HTML")
        form.add_field(
            "photo",
            image,
            filename="image.jpg",
        )

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=form) as resp:
                response = await resp.json()
                if not text:
                    return response
                photo = response["result"]["photo"]

    method = "sendMessage"
    url = f"{base_url}/{method}"

    params = {
        "chat_id": str(channel),
        "text": text,
        "disable_web_page_preview": 1,
        "parse_mode": "HTML",
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            response = await resp.json()

    if photo:
        response["result"]["photo"] = photo

    return response
