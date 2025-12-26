from typing import Optional

import aiohttp


class DalleClient:
    API_URL = "https://api.openai.com/v1/images/generations"

    def __init__(
        self,
        api_key: str,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        self.api_key = api_key
        self._owned_session = session is None
        self.session = session or aiohttp.ClientSession()

    async def close(self):
        if self._owned_session:
            await self.session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def generate_image(
        self,
        prompt: str,
        model: str = "dall-e-3",
        size: str = "1024x1024",
        quality: str = "standard",
        style: str = "vivid",
        n: int = 1,
        response_format: str = "url",  # or "b64_json"
    ) -> list[str]:  # Returns list of URLs or base64 strings
        payload = {
            "model": model,
            "prompt": prompt,
            "n": n,
            "size": size,
            "response_format": response_format,
        }
        if model == "dall-e-2":
            payload.update({"quality": quality, "style": style})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with self.session.post(
            self.API_URL, headers=headers, json=payload
        ) as resp:
            resp.raise_for_status()
            data = await resp.json()

        if response_format == "url":
            return [img["url"] for img in data["data"]]
        else:
            return [img["b64_json"] for img in data["data"]]
