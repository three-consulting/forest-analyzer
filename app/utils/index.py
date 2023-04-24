import streamlit as st

from dotenv import load_dotenv
from utils import context
from llama_index import GPTSQLStructStoreIndex

@st.cache_resource
def init(
    docs,
    db_name,
    table_name=None,
    text=None,
):
    load_dotenv()

    sql_context_container = context.init(
        db_name=db_name,
        context_dict={
            table_name: text,
        }
    ) if text and table_name else None
    
    return GPTSQLStructStoreIndex.from_documents(
        docs,
        sql_database=st.session_state[db_name],
        table_name=table_name,
        sql_context_container=sql_context_container,
    ) 