import streamlit as st

from llama_index import SQLDatabase
from utils import engine

@st.cache_resource
def init(connection_string, include_tables=None):
    return SQLDatabase(
        engine.init(connection_string=connection_string),
        include_tables=include_tables
    )