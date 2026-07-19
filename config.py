import streamlit as st
GROQ_API_KEY = st.secrets['groq_api_key']

MILVUS_URI = st.secrets['server_uri']
MILVUS_TOKEN = st.secrets['server_token']

COLLECTION_NAME = "new_collection"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

LLM_MODEL = "llama-3.1-8b-instant"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

SEARCH_TOP_K = 20
FINAL_TOP_K = 5
MIN_SIMILARITY = 0.2

if not GROQ_API_KEY:
    raise ValueError(
        "Missing GROQ_API_KEY. Please configure your .env file."
    )

if not MILVUS_URI:
    raise ValueError(
        "Missing MILVUS_URI. Please configure your .env file."
    )