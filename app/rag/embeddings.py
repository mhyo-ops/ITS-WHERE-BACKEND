from __future__ import annotations
from typing import List

from langchain_ollama import OllamaEmbeddings

from ..core.config import settings

_embedder = OllamaEmbeddings(
    model=settings.OLLAMA_EMBED_MODEL,
    base_url=settings.OLLAMA_BASE_URL,
)


def embed(text: str) -> List[float]:
    return _embedder.embed_query(text)


def embed_batch(texts: List[str]) -> List[List[float]]:
    return _embedder.embed_documents(texts)
