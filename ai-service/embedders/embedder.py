from sentence_transformers import SentenceTransformer

MODEL_NAME = "BAAI/bge-base-en-v1.5"

# Load once, reuse forever
_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def get_embedding(chunks):
    model = get_model()
    embeddings = model.encode(chunks, convert_to_numpy=True)
    return embeddings.tolist()