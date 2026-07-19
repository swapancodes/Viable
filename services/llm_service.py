import streamlit as st
from langchain_groq import ChatGroq
from config import GROQ_API_KEY, LLM_MODEL

@st.cache_resource
def get_llm():
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model=LLM_MODEL,
        temperature=0,
    )