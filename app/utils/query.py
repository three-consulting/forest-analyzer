import streamlit as st

@st.cache_data
def sql(query, db_name):
    return st.session_state[db_name].run_sql(query)