from langchain_openai import OpenAI
from fastembed import TextEmbedding


def get_embedding(text_chunks):
    model = TextEmbedding(model_name="BAAI/bge-base-en")
    embeddings = list(model.embed(text_chunks))
    return embeddings
