from os import getenv

from agents.dalle import DalleClient
from agents.gpt import GPTClient


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
        return await client.send_request(
            prompt,
            [(image, url)],
            max_tokens=800,
        )


async def gen_image(prompt, model="dall-e-3"):
    async with DalleClient(api_key=getenv("api_key")) as client:
        urls = await client.generate_image(prompt, model=model)
        return urls[0]
