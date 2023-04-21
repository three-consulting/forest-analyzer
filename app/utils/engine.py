import streamlit as st

from sqlalchemy import create_engine

@st.cache_resource
def init(connection_string):
    return create_engine(connection_string)