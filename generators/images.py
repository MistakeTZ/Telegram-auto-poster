import json
import logging

from agents.prompt import get_prompt
from generators.ai import gpt_image, gpt_request
from utils.check_image import download_image, resize_image
from utils.html_parser import get_image_size, get_images_by_url
from utils.json_parser import parse_text


async def find_best_image(theme, text, image_links):
    check_image_prompt = get_prompt(
        "check_image",
        theme=theme,
        recipe=text,
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

    image = await find_best_image(theme, text, image_links)
    logging.info(image)

    return image
