from services.embeddings import get_embedding_model
from services.milvus_service import get_milvus_client
from config import (COLLECTION_NAME,SEARCH_TOP_K,FINAL_TOP_K,MIN_SIMILARITY,)

def retrieve(question, filename=None, file_type=None):
    filters = []

    if filename:
        filters.append(f'filename == "{filename}"')

    if file_type:
        filters.append(f'file_type == "{file_type}"')

    filter_expr = " and ".join(filters) if filters else None

    embedding = get_embedding_model()
    client = get_milvus_client()
    vector = embedding.embed_query(question)

    search_params = {
        "collection_name": COLLECTION_NAME,
        "data": [vector],
        "anns_field": "vector",
        "search_params": {"metric_type": "COSINE"},
        "limit": SEARCH_TOP_K,
        "output_fields": ["text","filename","page","chunk","document_id","uploaded_at","file_type"]
    }

    # Apply filter only if it exists
    if filter_expr:
        search_params["filter"] = filter_expr

    results = client.search(**search_params)

    documents = []

    for hit in results[0]:
        score = hit["distance"]

        # Keep only results above the similarity threshold
        if score >= MIN_SIMILARITY:
            entity = hit["entity"]
            documents.append(
                {
                    "text": entity["text"],
                    "filename": entity["filename"],
                    "page": entity["page"],
                    "chunk": entity["chunk"],
                    "document_id": entity.get("document_id"),
                    "uploaded_at": entity.get("uploaded_at"),
                    "file_type": entity.get("file_type"),
                    "score": score,
                }
            )
    documents.sort(key=lambda x: x["score"], reverse=True)
    return documents[:FINAL_TOP_K]