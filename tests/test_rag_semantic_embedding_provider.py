import importlib.util
from pathlib import Path

import pytest

from src.app.rag.embedding_provider import get_embedding_provider


LOCAL_SEMANTIC_MODEL_PATH = Path("/mnt/f/LLM/maidalun/bce-embedding-base_v1")


def test_sentence_transformers_provider_with_local_model_or_skipped():
    if importlib.util.find_spec("sentence_transformers") is None:
        pytest.skip("sentence-transformers is optional and not installed in CI")

    if not LOCAL_SEMANTIC_MODEL_PATH.exists():
        pytest.skip("local semantic embedding model is not available in CI")

    provider = get_embedding_provider(
        provider="sentence_transformers",
        embedding_model=str(LOCAL_SEMANTIC_MODEL_PATH),
    )

    embedding = provider.embed_text("LangGraph 是什么？")

    assert provider.provider == "sentence_transformers"
    assert len(embedding) == 768
    assert any(value != 0 for value in embedding)
