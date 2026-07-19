from config import GROQ_API_KEY,MILVUS_URI

def validate_configuration():
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is missing.")

    if not MILVUS_URI:
        raise RuntimeError("MILVUS_URI is missing.")