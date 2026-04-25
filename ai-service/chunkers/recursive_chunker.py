from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_text(text, doc_id=None, chunk_size=500, overlap=50):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
    chunks = splitter.split_text(text)
    
    if doc_id:
        return [{"id": f"{doc_id}_chunk_{i}", "text": chunk} for i, chunk in enumerate(chunks)]
    return chunks