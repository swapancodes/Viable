from services.milvus_service import get_milvus_client
from config import COLLECTION_NAME

def list_documents():
    client = get_milvus_client()

    results = client.query(
        collection_name=COLLECTION_NAME,
        filter='document_id != ""',
        output_fields=[
            "document_id",
            "filename",
            "uploaded_at",
            "page",
            "chunk",
        ],
        limit=1000,
    )
    documents = {}
    for row in results:
        doc_id = row["document_id"]
        if doc_id not in documents:
            documents[doc_id] = {
                "document_id": doc_id,
                "filename": row["filename"],
                "uploaded_at": row["uploaded_at"],
                "pages": set(),
                "chunks": 0,
            }
        documents[doc_id]["pages"].add(row["page"])
        documents[doc_id]["chunks"] += 1
    return [
        {
            **doc,
            "pages": len(doc["pages"]),
        }
        for doc in documents.values()
    ]

def delete_document(document_id):
    client = get_milvus_client()
    client.delete(
        collection_name=COLLECTION_NAME,
        filter=f'document_id == "{document_id}"'
    )

def clear_collection():
    client = get_milvus_client()
    client.delete(
        collection_name=COLLECTION_NAME,
        filter='document_id != ""'
    )