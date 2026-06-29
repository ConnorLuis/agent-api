from dataclasses import dataclass
from pathlib import Path
import re


PROJECT_ROOT = Path(__file__).resolve().parents[3]
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"


@dataclass
class SearchResult:
    source: str
    content: str
    score: int


def _normalize(text: str) -> str:
    return text.lower().strip()


def _tokenize(text: str) -> list[str]:
    normalized = _normalize(text)

    # Split English words and Chinese character sequences separately.
    tokens = re.findall(r"[a-zA-Z0-9_]+|[\u4e00-\u9fff]+", normalized)

    stopwords = {
        "是",
        "什么",
        "是什么",
        "请",
        "帮我",
        "搜索",
        "检索",
        "知识库",
    }

    return [
        token
        for token in tokens
        if token and token not in stopwords
    ]


def _split_into_chunks(text: str, chunk_size: int = 260) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    if not paragraphs:
        return []

    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        if not current:
            current = paragraph
            continue

        if len(current) + len(paragraph) + 2 <= chunk_size:
            current = f"{current}\n\n{paragraph}"
        else:
            chunks.append(current)
            current = paragraph

    if current:
        chunks.append(current)

    return chunks


def _score_chunk(query_tokens: list[str], chunk: str) -> int:
    normalized_chunk = _normalize(chunk)

    score = 0

    for token in query_tokens:
        if token in normalized_chunk:
            score += 1

    return score


def search_knowledge(query: str, k: int = 3) -> list[SearchResult]:
    """
    Lightweight keyword-based retriever.

    Day12 uses this deterministic retriever instead of vector DB,
    so pytest and CI do not depend on embeddings or external services.
    """
    query_tokens = _tokenize(query)

    if not query_tokens:
        return []

    results: list[SearchResult] = []

    for path in KNOWLEDGE_DIR.glob("*.md"):
        text = path.read_text(encoding="utf-8")

        for chunk in _split_into_chunks(text):
            score = _score_chunk(query_tokens, chunk)

            if score > 0:
                results.append(
                    SearchResult(
                        source=str(path.relative_to(PROJECT_ROOT)),
                        content=chunk,
                        score=score,
                    )
                )

    results = sorted(results, key=lambda item: item.score, reverse=True)
    return results[:k]