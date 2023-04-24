import streamlit as st
import pandas as pd

from utils import index

def init():
    st.session_state.latest_table_prompt = ""

    st.session_state.index_all = index.init(
        docs=[],
        db_name="db_all"
    )

@st.cache_data
def query(prompt):
    return st.session_state.index_all.query(prompt)

def tab(points_bar):
    st.header("All tables")
    
    st.markdown("We have a SQL database containing more than one tables. Your task is to try and get the names of all of the tables by giving instructions in natural languge.")
    st.text_input("Prompt", key="table_prompt")
    
    if len(st.session_state.table_prompt) > 0:
        # Process
        if st.session_state.table_prompt != st.session_state.latest_table_prompt:
            try:
                st.session_state.all_tables_response = query(st.session_state.table_prompt)
                st.session_state.latest_table_prompt = st.session_state.table_prompt
            except Exception as e:
                st.error(e)
                st.stop()

        try:
            st.session_state.all_tables_query = st.session_state.all_tables_response.extra_info["sql_query"]
            
            if type(st.session_state.all_tables_query).__name__ != 'str':
                raise TypeError("SQL query is not a string: ", st.session_state.all_tables_query)

        except TypeError as e:
            st.error("Could not make a SQL query from given prompt. Why not try some other prompt?")
            st.error(e)
            st.stop()

        try:
            st.session_state.all_tables_result = st.session_state.all_tables_response.extra_info["result"]

            if type(st.session_state.all_tables_result).__name__ == 'list':
                st.session_state.all_tables_list = [m[0] for m in st.session_state.all_tables_result]
            else:
                raise TypeError("Query result is not a list: ", st.session_state.all_tables_result)
            
        except TypeError as e:
            st.error("Could not process data into suitable format. Why not try some other prompt?")
            st.error(e)
            st.stop()

        # Draw
        if type(st.session_state.all_tables_query).__name__ == 'str':
            st.subheader("SQL Query:")
            st.code(st.session_state.all_tables_query, language='sql', line_numbers=False)

        if type(st.session_state.all_tables_list).__name__ == 'list':
            st.subheader("Tables:")
            df = pd.DataFrame(
                st.session_state.all_tables_list,
                columns=['Tables']
            )
            st.table(df)
        
        # Task result
        all_tables_gold_standard = ['treestratum', 'treestandsummary', 'treestand', 'specification', 'specialfeature', 'datasource', 'restriction', 'assortment', 'stand', 'stand_4326', 'operation']
        
        st.session_state.all_tables_list.sort()
        all_tables_gold_standard.sort()

        if type(st.session_state.all_tables_list).__name__ == 'list' and all_tables_gold_standard == st.session_state.all_tables_list:
            st.session_state.points[0] = 1
            points_bar.progress(
                int(sum(st.session_state.points)/len(st.session_state.points)*100),
                text=f"{sum(st.session_state.points)}/{len(st.session_state.points)}"
            )
            st.success("You did it!")