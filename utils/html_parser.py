import logging
import re
import urllib.parse
from io import BytesIO

import aiohttp
from bs4 import BeautifulSoup
from PIL import Image


async def get_image_size(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    image_data = await response.read()
                    image = Image.open(BytesIO(image_data))
                    return image.size[0]
    except Exception as e:
        logging.warning(f"Can't load image {url}: {e}")
    return 0


def extract_image_candidates(soup: BeautifulSoup) -> dict:
    """
    Extract image candidates from an HTML document.
    Returns a dictionary of image candidates with metadata and score.
    """
    for tag in soup.select(
        "nav, aside, footer, header, .sidebar, .related, .recommend, .promo, .ads, .comments"
    ):
        tag.decompose()

    images = []
    position = 0

    for img in soup.find_all("img"):
        position += 1

        src = img.get("src")
        if not src:
            continue

        alt = img.get("alt", "").lower()
        classes = " ".join(img.get("class", [])).lower()

        if re.search(r"avatar|icon|logo", alt + classes):
            continue

        parent_tags = [p.name for p in img.parents if hasattr(p, "name")]
        in_article = any(t in parent_tags for t in ("article", "main", "figure"))

        caption = ""
        if img.parent.name == "figure":
            figcaption = img.parent.find("figcaption")
            if figcaption:
                caption = figcaption.get_text(strip=True)

        near_text = ""
        p = img.find_parent("p")
        if p:
            near_text = p.get_text(strip=True)

        width = img.get("width")
        height = img.get("height")

        score = 0
        if in_article:
            score += 3
        if caption:
            score += 2
        if len(near_text) > 120:
            score += 2
        if width and height:
            try:
                if int(width) * int(height) > 300_000:
                    score += 2
            except ValueError:
                pass

        images.append(
            {
                "src": src,
                "alt": alt,
                "caption": caption,
                "near_text": near_text[:300],
                "position": position,
                "score": score,
            }
        )

    images.sort(key=lambda x: x["score"], reverse=True)

    return images


async def get_html(url: str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                soup = BeautifulSoup(await response.text(), "html.parser")
                return soup
    except Exception as e:
        logging.error(e)
        return


async def get_images_by_url(url: str):
    html = await get_html(url)
    if not html:
        return
    images = extract_image_candidates(html)

    normal_images = []
    for image in images:
        src = image["src"]
        if src.startswith("/_next/image"):
            continue
        if src.startswith("/"):
            src = urllib.parse.urljoin(url, src)
        try:
            size = await get_image_size(src)
            if size >= 600:
                normal_image = image.copy()
                normal_image["src"] = src
                normal_image["size"] = size
                normal_image["score"] += size // 100
                normal_images.append(normal_image)
        except Exception as e:
            logging.debug("Failed to get size for %s: %s", src, e)
    normal_images.sort(key=lambda x: x["score"], reverse=True)
    return normal_images


if __name__ == "__main__":
    import asyncio
    import sys

    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    asyncio.run(get_images_by_url("https://1000.menu/cooking/14290-kurica-vino"))
