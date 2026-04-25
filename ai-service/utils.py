def normalize_chunks(chunks):
    if not chunks:
        return chunks
    if isinstance(chunks[0], str):
        return [{"id": None, "text": c} for c in chunks]
    return chunks
