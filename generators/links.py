from config import session

from agents.prompt import get_prompt
from database.orm import Link
from generators.ai import gpt_request
from utils.json_parser import parse_text


async def add_article_links(article):
    photos_prompt = get_prompt(
        "get_photo",
        theme=article.name,
    )
    response = await gpt_request(
        photos_prompt,
        "gpt-4o-search-preview",
    )

    links = parse_text(response, [])

    for link in links:
        session.add(Link(article_id=article.id, link=link))
