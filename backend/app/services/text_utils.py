from __future__ import annotations

import hashlib
import json
import math
import re
from typing import Any


def split_terms(value: str) -> list[str]:
    terms = [part.strip() for part in re.split(r"[,;\n]", value or "")]
    return [term for term in terms if term]


def extract_json_object(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(cleaned[start : end + 1])


def local_embedding(text: str, size: int = 64) -> list[float]:
    vector = [0.0] * size
    tokens = re.findall(r"[a-zA-Z0-9]+", text.lower())
    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % size
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[index] += sign

    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


def profile_search_text(profile: dict[str, Any]) -> str:
    parts: list[str] = [
        profile.get("name", ""),
        profile.get("headline", ""),
        profile.get("location", ""),
        profile.get("availability", ""),
        profile.get("current_need", ""),
        profile.get("profile_summary", ""),
    ]
    for key in ("interests", "expertise", "goals", "preferred_formats", "constraints"):
        value = profile.get(key, [])
        if isinstance(value, list):
            parts.append(", ".join(str(item) for item in value))
        else:
            parts.append(str(value))
    return "\n".join(part for part in parts if part)
