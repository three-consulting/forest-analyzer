import streamlit as st

from config import Settings
from utils import llm, db 

def init():
    st.session_state.points = [0, 0, 0, 0]

    conf = Settings()

    OPENAI_MODEL_NAME = conf.openai_model_name
    OPENAI_API_KEY = conf.openai_api_key

    DATABASE_NAME = conf.database_name
    DATABASE_USER = conf.database_user
    DATABASE_PASSWORD = conf.database_password
    DATABASE_PORT = conf.database_port
    DATABASE_HOST = conf.database_host

    st.session_state.llm_predictor = llm.init(
        model_name=OPENAI_MODEL_NAME,
        openai_api_key=OPENAI_API_KEY,
    )
    
    st.session_state.connection_string = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

    st.session_state.db = db.init(connection_string=st.session_state.connection_string, include_tables=["stand_4326"])
    st.session_state.db_all = db.init(connection_string=st.session_state.connection_string)