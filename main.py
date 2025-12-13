import asyncio
from datetime import datetime
from os import getenv

from dotenv import load_dotenv

from agents.gpt import GPTClient
from agents.prompt import get_prompt
from utils.json_parser import parse_text


async def main():
    actual_themes_prompt = get_prompt(
        "actual_events",
        today=datetime.now().strftime("%d %B %Y"),
    )

    async with GPTClient(api_key=getenv("api_key"), model="gpt-4o-mini") as client:
        response = await client.send_request(actual_themes_prompt)

    events = parse_text(response)

    new_post_prompt = get_prompt(
        "themes",
        actualEvents="\n".join(events),
        existingThemes="отсутствуют",
        format=get_prompt("themes_format"),
    )

    async with GPTClient(api_key=getenv("api_key"), model="gpt-4o-mini") as client:
        response = await client.send_request(new_post_prompt)

    themes = parse_text(response)


if __name__ == "__main__":
    load_dotenv()

    asyncio.run(main())
