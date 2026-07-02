from pathlib import Path
from typing import Any


DEFAULT_KNOWLEDGE_DIR = Path("knowledge")
DEFAULT_MAX_CHARS = 500


def _normalize_source_path(path: Path) -> str:
    return path.as_posix()


def _read_markdown_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _split_text_by_blank_lines(text: str) -> list[str]:
    blocks = []

    for block in text.split("\n\n"):
        normalized = block.strip()

        if normalized:
            blocks.append(normalized)

    return blocks


def split_text_into_chunks(text: str, max_chars: int = DEFAULT_MAX_CHARS) -> list[str]:
    safe_max_chars = max(max_chars, 80)
    blocks = _split_text_by_blank_lines(text)

    chunks: list[str] = []
    current_parts: list[str] = []
    current_length = 0

    for block in blocks:
        block_length = len(block)

        if not current_parts:
            current_parts.append(block)
            current_length = block_length
            continue

        candidate_length = current_length + 2 + block_length

        if candidate_length <= safe_max_chars:
            current_parts.append(block)
            current_length = candidate_length
            continue

        chunks.append("\n\n".join(current_parts))
        current_parts = [block]
        current_length = block_length

    if current_parts:
        chunks.append("\n\n".join(current_parts))

    return chunks


def load_markdown_documents(knowledge_dir: Path | str = DEFAULT_KNOWLEDGE_DIR, source_filter: str | None = None) -> list[dict[str, str]]:
    root = Path(knowledge_dir)

    if not root.exists():
        return []

    normalized_filter = (source_filter or "").strip().lower()

    documents = []

    for path in sorted(root.rglob("*.md")):
        source = _normalize_source_path(path)

        if normalized_filter and normalized_filter not in source.lower():
            continue

        content = _read_markdown_file(path)

        documents.append({"source": source, "content": content})

    return documents


def load_knowledge_chunks(knowledge_dir: Path | str = DEFAULT_KNOWLEDGE_DIR, source_filter: str | None = None, max_chars: int = DEFAULT_MAX_CHARS) -> list[dict[str, Any]]:
    documents = load_markdown_documents(knowledge_dir=knowledge_dir, source_filter=source_filter)

    all_chunks = []

    for document in documents:
        source = document["source"]
        content = document["content"]
        chunks = split_text_into_chunks(text=content, max_chars=max_chars)

        for index, chunk in enumerate(chunks, start=1):
            all_chunks.append(
                {
                    "chunk_id": f"{source}::chunk-{index}",
                    "source": source,
                    "index": index,
                    "content": chunk,
                    "preview": chunk[:160],
                    "content_length": len(chunk),
                }
            )
    return all_chunks


def debug_knowledge_chunks(source_filter: str | None = None, max_chars: int = DEFAULT_MAX_CHARS) -> dict[str, Any]:
    chunks = load_knowledge_chunks(source_filter=source_filter, max_chars=max_chars)

    return {
        "source_filter": source_filter,
        "max_chars": max_chars,
        "total_chunks": len(chunks),
        "chunks": chunks,
    }