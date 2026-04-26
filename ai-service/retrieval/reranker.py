from sentence_transformers import CrossEncoder

model_path = "/home/megabytis/local_models/cross_encoder"

model = CrossEncoder(model_path)

def rerank(query, chunks):
    pairs = [[query, chunk["text"]] for chunk in chunks]
    scores = model.predict(pairs)

    # now pairing scores with chunks & then sorting them
    scored = list(zip(chunks, scores))
    scored.sort(key=lambda x: x[1], reverse=True)

    # taking only top 3
    top_chunks = [chunk for chunk, score in scored[:5]]

    return top_chunks
