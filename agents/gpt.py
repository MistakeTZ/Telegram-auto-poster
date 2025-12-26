import base64
import logging
from typing import List, Optional

import aiohttp


class GPTClient:
    """
    An asynchronous class to send requests to OpenAI's GPT models
    supporting multimodal input: text + images.

    Uses aiohttp for fully async HTTP requests.
    Handles both text-only and text+image prompts.
    """

    API_URL = "https://api.openai.com/v1/chat/completions"

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        session: Optional[aiohttp.ClientSession] = None,
    ):
        """
        :param api_key: Your OpenAI API key.
        :param model: The vision-capable model (e.g., 'gpt-4o', 'gpt-4o-mini').
        :param session: Optional existing aiohttp.ClientSession for reuse.
        """
        self.api_key = api_key
        self.model = model
        self._owned_session = session is None
        self.session = session or aiohttp.ClientSession()
        logging.debug("GPTClient initialized")

    async def close(self):
        """Close the aiohttp session if owned by this client."""
        logging.debug("Closing aiohttp session...")
        if self._owned_session:
            await self.session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    @staticmethod
    def _encode_image_to_base64(image: bytes, url: str) -> str:
        """Encode a local image bytes to base64 data URL."""
        logging.debug("Encoding image to base64...")
        encoded = base64.b64encode(image).decode("utf-8")
        # Guess MIME type from extension (fallback to jpeg)
        mime_type = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }.get(url[url.rfind("."):], "image/jpeg")
        return f"data:{mime_type};base64,{encoded}"

    async def send_request(
        self,
        prompt: str,
        images: Optional[List[tuple[str, str]]] = None,
        system_prompt: str = "You are a helpful assistant.",
        max_tokens: int = 500,
        temperature: float = 0.7,
    ) -> str:
        """
        Send a multimodal request to the GPT vision model.

        :param prompt: The user text prompt.
        :param images: List of image URLs or local file paths.
        :param system_prompt: Optional system message.
        :param max_tokens: Maximum tokens in response.
        :param temperature: Sampling temperature.
        :return: The model's text response.
        """
        # Build the content array for the user message
        content: List[dict] = [{"type": "text", "text": prompt}]
        logging.debug("Sending request with prompt: %s", prompt)

        if images:
            for img in images:
                image_url = self._encode_image_to_base64(*img)
                content.append(
                    {"type": "image_url", "image_url": {"url": image_url}},
                )

        # Build messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content},
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
        }
        if "search" not in self.model:
            payload["temperature"] = temperature

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with self.session.post(
                self.API_URL, headers=headers, json=payload
            ) as response:
                response.raise_for_status()
                data = await response.json()

            logging.info("Received response: %s", data)
            return data["choices"][0]["message"]["content"]

        except aiohttp.ClientError as e:
            logging.error("Error sending request: %s", e)
            return ""
