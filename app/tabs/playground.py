import streamlit as st

from utils import index

def init():
    st.session_state.latest_playground_prompt = ""
    
    text = (
        "I have postgreSQL database with PostGis geospatial forest data.\n"
        "The PostGis plugin is available in the database.\n"
        "The forest polygons can be found from the geometry column.\n"
        "Get the geometry as geojson.\n"
    )

    st.session_state.index_tab6 = index.init(
        docs=[],
        db_name="db_all",
        text=text,
    )

@st.cache_data
def query(prompt):
    return st.session_state.index_tab6.query(prompt)

def tab():
    st.header("Playground:")

    st.markdown("Try any prompt you wan't and see what kind of SQL queries the LLM generates for you.")

    st.text_input("Prompt:", key="playground_prompt")

    if len(st.session_state.playground_prompt) > 0:
        #Process
        with st.spinner(text="Getting response..."):
            if st.session_state.playground_prompt != st.session_state.latest_playground_prompt:
                try:
                    st.session_state.playground_response = query(st.session_state.playground_prompt)
                    st.session_state.latest_playground_prompt = st.session_state.playground_prompt
                    
                    st.session_state.playground_query = st.session_state.playground_response.extra_info["sql_query"]
                    
                    st.session_state.playground_result = st.session_state.playground_response.extra_info["result"]
                except Exception as e:
                    st.error(e)
                    st.stop()

        # Draw
        if type(st.session_state.playground_query).__name__ == 'str':
            st.subheader("SQL Query:")
            st.code(st.session_state.playground_query, language="sql", line_numbers=False)
    
        if st.session_state.playground_result:
            st.subheader("Query result:")
            st.write(st.session_state.playground_result)