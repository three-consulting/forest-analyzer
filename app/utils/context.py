import streamlit as st

from llama_index.indices.struct_store import SQLContextContainerBuilder

@st.cache_resource
def init(context_dict, db_name):
    context_builder = SQLContextContainerBuilder(st.session_state[db_name], context_dict=context_dict)
    return context_builder.build_context_container()