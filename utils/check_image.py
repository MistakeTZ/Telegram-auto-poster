from io import BytesIO

import aiohttp
from PIL import Image

from agents.gpt import GPTClient


async def download_image(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            image = await response.read()
            return image


def resize_image(image: bytes, max_width: int = 200):
    with Image.open(BytesIO(image)) as img:
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")

        if img.width <= max_width:
            output = BytesIO()
            img.save(output, format="JPEG", quality=95)
            return output.getvalue()

        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        resized_img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

        output = BytesIO()
        resized_img.save(output, format="JPEG", quality=95)
        return output.getvalue()
