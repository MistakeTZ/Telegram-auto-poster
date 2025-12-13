import logging
import re

import aiohttp
from bs4 import BeautifulSoup


async def get_image_size(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return response.content.total_bytes


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
        size = await get_image_size(image["src"])
        if size >= 1200:
            normal_images.append(image)
            normal_images[-1]["size"] = size
            normal_images[-1]["score"] += size // 1000

    normal_images.sort(key=lambda x: x["score"], reverse=True)
    return normal_images
