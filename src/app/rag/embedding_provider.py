import math
from typing import Protocol

from src.app.rag.vector_index import (
    DEFAULT_EMBEDDING_DIM,
    build_deterministic_embedding,
)

DEFAULT_EMBEDDING_PROVIDER = "deterministic"
DEFAULT_DETERMINISTIC_EMBEDDING_MODEL = "deterministic-hash"
DEFAULT_SENTENCE_TRANSFORMERS_MODEL = "/mnt/f/LLM/maidalun/bce-embedding-base_v1"


class EmbeddingProvider(Protocol):
    provider: str
    model: str

    def embed_text(
        self,
        text: str,
        embedding_dim: int = DEFAULT_EMBEDDING_DIM,
    ) -> list[float]:
        ...

    def embed_documents(
        self,
        texts: list[str],
        embedding_dim: int = DEFAULT_EMBEDDING_DIM,
    ) -> list[list[float]]:
        ...


def _to_float_list(vector: object) -> list[float]:
    if hasattr(vector, "tolist"):
        raw_values = vector.tolist()
    else:
        raw_values = vector

    return [float(value) for value in raw_values]  # type: ignore[arg-type]


def embedding_norm(embedding: list[float]) -> float:
    return round(
        math.sqrt(sum(value * value for value in embedding)),
        6,
    )


class DeterministicEmbeddingProvider:
    provider = "deterministic"
    model = DEFAULT_DETERMINISTIC_EMBEDDING_MODEL

    def embed_text(
        self,
        text: str,
        embedding_dim: int = DEFAULT_EMBEDDING_DIM,
    ) -> list[float]:
        safe_dim = max(embedding_dim, 8)

        return build_deterministic_embedding(
            text=text,
            embedding_dim=safe_dim,
        )

    def embed_documents(
        self,
        texts: list[str],
        embedding_dim: int = DEFAULT_EMBEDDING_DIM,
    ) -> list[list[float]]:
        return [
            self.embed_text(
                text=text,
                embedding_dim=embedding_dim,
            )
            for text in texts
        ]


class SentenceTransformersEmbeddingProvider:
    provider = "sentence_transformers"

    def __init__(
        self,
        model_name: str = DEFAULT_SENTENCE_TRANSFORMERS_MODEL,
    ) -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError(
                "sentence-transformers is not installed. "
                "Install it before using provider='sentence_transformers'."
            ) from exc

        self.model = model_name
        self._model = SentenceTransformer(model_name)

    def embed_text(
        self,
        text: str,
        embedding_dim: int = DEFAULT_EMBEDDING_DIM,
    ) -> list[float]:
        vector = self._model.encode(
            text,
            normalize_embeddings=True,
        )

        return _to_float_list(vector)

    def embed_documents(
        self,
        texts: list[str],
        embedding_dim: int = DEFAULT_EMBEDDING_DIM,
    ) -> list[list[float]]:
        vectors = self._model.encode(
            texts,
            normalize_embeddings=True,
        )

        return [
            _to_float_list(vector)
            for vector in vectors
        ]


def get_embedding_provider(
    provider: str = DEFAULT_EMBEDDING_PROVIDER,
    embedding_model: str | None = None,
) -> EmbeddingProvider:
    normalized_provider = provider.strip().lower()

    if normalized_provider in {"deterministic", "hash", "mock"}:
        return DeterministicEmbeddingProvider()

    if normalized_provider in {"sentence_transformers", "sentence-transformers", "local"}:
        return SentenceTransformersEmbeddingProvider(
            model_name=embedding_model or DEFAULT_SENTENCE_TRANSFORMERS_MODEL,
        )

    raise ValueError(
        f"Unsupported embedding provider: {provider}"
    )


def debug_embeddings(
    query: str,
    documents: list[str] | None = None,
    provider: str = DEFAULT_EMBEDDING_PROVIDER,
    model_name: str | None = None,
    embedding_dim: int = DEFAULT_EMBEDDING_DIM,
) -> dict:
    embedding_provider = get_embedding_provider(
        provider=provider,
        embedding_model=model_name,
    )

    query_embedding = embedding_provider.embed_text(
        text=query,
        embedding_dim=embedding_dim,
    )

    document_texts = documents or []
    document_embeddings = embedding_provider.embed_documents(
        texts=document_texts,
        embedding_dim=embedding_dim,
    )

    return {
        "query": query,
        "provider": embedding_provider.provider,
        "model": embedding_provider.model,
        "requested_embedding_dim": embedding_dim,
        "actual_embedding_dim": len(query_embedding),
        "query_embedding_preview": query_embedding[:8],
        "query_embedding_norm": embedding_norm(query_embedding),
        "documents_count": len(document_texts),
        "documents": [
            {
                "text": text,
                "embedding_dim": len(embedding),
                "embedding_preview": embedding[:8],
                "embedding_norm": embedding_norm(embedding),
            }
            for text, embedding in zip(
                document_texts,
                document_embeddings,
                strict=True,
            )
        ],
    }