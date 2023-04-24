import streamlit as st

from langchain.chat_models import ChatOpenAI

@st.cache_resource
def init(model_name, openai_api_key):
    return ChatOpenAI(
        model_name=model_name,
        openai_api_key=openai_api_key,
    )