import uuid
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import *
from services.embeddings import get_embedding_model
from services.milvus_service import (create_collection_if_not_exists)
from datetime import datetime

def ingest_documents(docs):
    if not docs:
        raise ValueError("No documents provided.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    chunks = splitter.split_documents(docs)
    
    for index, chunk in enumerate(chunks):
       chunk.metadata["chunk"] = index + 1
       chunk.metadata["document_id"] = chunk.metadata.get(
           "document_id",
           "unknown",
       )

    if not chunks:
       raise ValueError("No text found in uploaded documents.")

    embedding = get_embedding_model()
    vectors = embedding.embed_documents(
        [chunk.page_content for chunk in chunks]
    )

    client = create_collection_if_not_exists(len(vectors[0]))

    data = []

    for chunk, vector in zip(chunks, vectors):
        data.append(
            {
                "id": uuid.uuid4().int & ((1 << 63) - 1),
                "vector": vector,
                "text": chunk.page_content,
                "document_id": chunk.metadata["document_id"],
                "filename": chunk.metadata.get("filename", "Unknown"),
                "page": chunk.metadata.get("page", 1),
                "chunk": chunk.metadata.get("chunk", 1),
                "uploaded_at": datetime.now().isoformat(),
                "file_type":chunk.metadata.get("file_type","unknown"),
            }
        )

    # Delete existing chunks for every uploaded document
    document_ids = {
        chunk.metadata["document_id"]
        for chunk in chunks
    }    

    for doc_id in document_ids:
        client.delete(
            collection_name=COLLECTION_NAME,
            filter=f'document_id == "{doc_id}"'
        )

    client.insert(
        collection_name=COLLECTION_NAME,
        data=data
    )