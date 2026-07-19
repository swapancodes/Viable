import os
import tempfile
from langchain_community.document_loaders import (
    PyMuPDFLoader,
    TextLoader,
    CSVLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredExcelLoader,
    UnstructuredHTMLLoader,
    UnstructuredMarkdownLoader,
)
import streamlit as st
import hashlib

def load_uploaded_file(uploaded_file):
    suffix = os.path.splitext(uploaded_file.name)[1].lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getvalue())
        temp_path = tmp.name

    try:
        if suffix == ".pdf":
            loader = PyMuPDFLoader(temp_path)

        elif suffix == ".docx":
            loader = UnstructuredWordDocumentLoader(temp_path)

        elif suffix == ".txt":
            loader = TextLoader(temp_path, encoding="utf-8")

        elif suffix == ".csv":
            loader = CSVLoader(temp_path)

        elif suffix in [".xlsx", ".xls"]:
            loader = UnstructuredExcelLoader(temp_path)

        elif suffix == ".html":
            loader = UnstructuredHTMLLoader(temp_path)

        elif suffix == ".md":
            loader = UnstructuredMarkdownLoader(temp_path)

        else:
            st.warning(f"Unsupported file: {uploaded_file.name}")
            return []

        docs = loader.load()

        full_text = "\n".join(doc.page_content for doc in docs)
        document_id = hashlib.sha256(full_text.encode("utf-8")).hexdigest()
        for doc in docs:
            doc.metadata.update(
               {
                  "filename": uploaded_file.name,
                  "document_id": document_id,
                  "page": doc.metadata.get("page",1),
                  "file_type": suffix.replace(".", "")    
                }
             )

    except Exception as e:
        st.error(f"Error loading {uploaded_file.name}: {e}")
        docs = []

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return docs
