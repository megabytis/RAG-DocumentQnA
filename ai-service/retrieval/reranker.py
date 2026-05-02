from sentence_transformers import CrossEncoder

MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"
model = CrossEncoder(MODEL_NAME)

def rerank(query, chunks):
    pairs = [[query, chunk["text"]] for chunk in chunks]
    scores = model.predict(pairs)

    # now pairing scores with chunks & then sorting them
    scored = list(zip(chunks, scores))
    scored.sort(key=lambda x: x[1], reverse=True)

    # taking only top 3
    top_chunks = [chunk for chunk, score in scored[:5]]

    return top_chunks
