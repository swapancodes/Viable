import streamlit as st
from pymilvus import MilvusClient, DataType
from config import COLLECTION_NAME, MILVUS_URI, MILVUS_TOKEN


@st.cache_resource
def get_milvus_client():
    return MilvusClient(
        uri=MILVUS_URI,
        token=MILVUS_TOKEN
    )

def create_collection_if_not_exists(dimension):

    client = get_milvus_client()

    if not client.has_collection(COLLECTION_NAME):
        
        schema = client.create_schema(auto_id=False, enable_dynamic_field=True)

        schema.add_field("id", DataType.INT64, is_primary=True)
        schema.add_field("vector", DataType.FLOAT_VECTOR, dim=dimension)
        schema.add_field("text", DataType.VARCHAR, max_length=65535)
        schema.add_field("filename", DataType.VARCHAR, max_length=512)
        schema.add_field("document_id", DataType.VARCHAR, max_length=64)
        schema.add_field("page", DataType.INT64)
        schema.add_field("chunk", DataType.INT64)
        schema.add_field("uploaded_at", DataType.VARCHAR, max_length=64)
        schema.add_field("file_type",DataType.VARCHAR,max_length=50)
 
        index_params = client.prepare_index_params()

        index_params.add_index(
            field_name="vector",
            index_type="AUTOINDEX",
            metric_type="COSINE"
        )

        client.create_collection(
            collection_name=COLLECTION_NAME,
            schema=schema,
            index_params=index_params,
        )

    return client