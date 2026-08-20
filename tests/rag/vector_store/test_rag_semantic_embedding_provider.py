import sys
from types import ModuleType

from src.app.rag.embedding_provider import (
    get_embedding_provider,
)


class FakeSentenceTransformer:
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name

    def encode(
        self,
        text: str,
        *,
        normalize_embeddings: bool,
    ) -> list[float]:
        assert text == "LangGraph 是什么？"
        assert normalize_embeddings is True
        return [0.25] * 768


def test_sentence_transformers_provider_contract(monkeypatch):
    fake_module = ModuleType("sentence_transformers")
    fake_module.SentenceTransformer = FakeSentenceTransformer
    monkeypatch.setitem(
        sys.modules,
        "sentence_transformers",
        fake_module,
    )

    model_name = "test-semantic-model"

    provider = get_embedding_provider(
        provider="sentence_transformers",
        embedding_model=model_name,
    )

    embedding = provider.embed_text("LangGraph 是什么？")

    assert provider.provider == "sentence_transformers"
    assert provider.model == model_name
    assert len(embedding) == 768
    assert any(value != 0 for value in embedding)
