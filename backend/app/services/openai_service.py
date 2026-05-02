from __future__ import annotations

from openai import OpenAI

from app.core.config import settings


class OpenAIService:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    @property
    def enabled(self) -> bool:
        return self.client is not None

    def generate_json(self, instructions: str, input_text: str, schema: dict, name: str) -> str:
        if self.client is None:
            raise RuntimeError("OPENAI_API_KEY is not configured")

        response = self.client.responses.create(
            model=settings.openai_chat_model,
            instructions=instructions,
            input=input_text,
            text={
                "format": {
                    "type": "json_schema",
                    "name": name,
                    "schema": schema,
                    "strict": False,
                }
            },
        )
        return response.output_text

    def embed_text(self, text: str) -> list[float]:
        if self.client is None:
            raise RuntimeError("OPENAI_API_KEY is not configured")

        response = self.client.embeddings.create(
            model=settings.openai_embedding_model,
            input=text,
        )
        return response.data[0].embedding
