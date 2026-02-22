import json
import re
from typing import TypeVar

from openai import AsyncOpenAI
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class OpenRouterClient:
    def __init__(self, api_key: str) -> None:
        self._client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )

    async def generate(self, model: str, system: str, user: str) -> str:
        """Send a completion request and return the raw text response."""
        response = await self._client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.7,
        )
        content = response.choices[0].message.content
        if content is None:
            raise ValueError(f"Empty response from {model}")
        return content

    async def generate_parsed(
        self, model: str, system: str, user: str, schema: type[T]
    ) -> T:
        """Generate a response and parse it into a Pydantic model."""
        raw = await self.generate(model, system, user)
        cleaned = _extract_json(raw)
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Failed to parse JSON from {model} response: {e}\n"
                f"Raw response:\n{raw}"
            ) from e
        return schema.model_validate(data)


def _extract_json(text: str) -> str:
    """Extract JSON from a response that might have markdown fences or extra text."""
    # Try to find JSON in markdown code blocks first
    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Find the outermost JSON object using brace counting
    start = text.find("{")
    if start != -1:
        depth = 0
        in_string = False
        escape_next = False
        for i in range(start, len(text)):
            ch = text[i]
            if escape_next:
                escape_next = False
                continue
            if ch == "\\":
                escape_next = True
                continue
            if ch == '"' and not escape_next:
                in_string = not in_string
                continue
            if in_string:
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    result = text[start : i + 1]
                    # Strip duplicate outer braces: {{ ... }} → { ... }
                    stripped = result.strip()
                    while stripped.startswith("{{") and stripped.endswith("}}"):
                        stripped = stripped[1:-1].strip()
                    return stripped

    return text.strip()
