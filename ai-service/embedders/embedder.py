from sentence_transformers import SentenceTransformer
import os

LOCAL_MODEL_PATH = os.path.expanduser("~/local_models/sentence_transformer")

# Load once, reuse forever
_model = None

def get_model():
    global _model
    if _model is None:
        if not os.path.exists(LOCAL_MODEL_PATH):
            raise FileNotFoundError(f"Model not found at {LOCAL_MODEL_PATH}. Run download_model.py first.")
        _model = SentenceTransformer(LOCAL_MODEL_PATH)
    return _model

def get_embedding(chunks):
    model = get_model()
    embeddings = model.encode(chunks, convert_to_numpy=True)
    return embeddings.tolist()