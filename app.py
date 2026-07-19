import streamlit as st
from utils.loaders import load_uploaded_file
from rag.ingest import ingest_documents
from rag.qa import ask_question
from services.validator import validate_configuration
from rag.document_manager import (list_documents,delete_document,clear_collection,)

# Validate configuration
validate_configuration()

# Page configuration
st.set_page_config(
    page_title="Enterprise RAG Chatbot",
    page_icon="📚",
    layout="wide",
)

# ---------------- Sidebar ----------------
with st.sidebar:
    st.title("📂 Knowledge Base")

    uploaded_files = st.file_uploader(
        "Upload Documents",
        accept_multiple_files=True,
        type=["pdf", "docx", "txt", "csv", "xlsx", "xls", "md", "html"],
    )

    if uploaded_files:
        if st.button("📤 Upload"):
            try:
                docs = []

                with st.spinner("Processing documents..."):
                    for file in uploaded_files:
                        docs.extend(load_uploaded_file(file))

                    ingest_documents(docs)

                st.success("Documents uploaded successfully!")
                st.rerun()

            except Exception as e:
                st.error(f"Upload failed: {e}")

    if st.button("🗑 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.subheader("📑 Document Management")

    documents = list_documents()

    if documents:
        for doc in documents:
            with st.container():
                st.write(f"📄 **{doc['filename']}**")
                st.caption(f"Pages: {doc['pages']}")
                st.caption(f"Chunks: {doc['chunks']}")
                st.caption(f"Uploaded: {doc['uploaded_at'][:10]}")

                if st.button(
                    "Delete",
                    key=f"delete_{doc['document_id']}",
                ):
                    delete_document(doc["document_id"])
                    st.success("Document deleted.")
                    st.rerun()
    else:
        st.info("No documents uploaded.")

    st.divider()

    if st.button("🗑 Clear Knowledge Base"):
        try:
            clear_collection()
            st.success("Knowledge base cleared.")
            st.rerun()
        except Exception as e:
            st.error(f"Failed: {e}")

    # ----------- Statistics -----------
    total_docs = len(documents)
    total_chunks = sum(doc.get("chunks", 0) for doc in documents)

    st.divider()
    st.subheader("📊 Statistics")
    st.metric("Documents", total_docs)
    st.metric("Chunks", total_chunks)

# ---------------- Main Page ----------------
st.title("📚 Enterprise Document Chatbot")
st.caption("Ask questions from your uploaded knowledge base.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
question = st.chat_input("Ask a question...")

if question:
    # Save user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    # Get answer
    with st.spinner("Thinking..."):
        try:
            result = ask_question(question)
        except Exception as e:
            result = {
                "answer": f"Error: {e}",
                "documents": [],
            }

    # Handle different return types
    if isinstance(result, dict):
        answer = result.get("answer", "No answer found.")
        retrieved_docs = result.get("documents", [])
    elif isinstance(result, tuple):
        answer, retrieved_docs = result
    else:
        answer = str(result)
        retrieved_docs = []

    # Display assistant answer
    with st.chat_message("assistant"):
        st.markdown(answer)

        if retrieved_docs:
            with st.expander("📄 Retrieved Sources"):
                for doc in retrieved_docs:
                    filename = doc.get("filename", "Unknown")
                    page = doc.get("page", "-")
                    score = doc.get("score", 0)
                    text = doc.get("text", "")

                    st.markdown(
                        f"""
                    **📄 {filename}**
                    **Page:** {page}
                    **Similarity:** {score:.3f}
                    {text}
                    """
                    )

    # Save assistant message
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )