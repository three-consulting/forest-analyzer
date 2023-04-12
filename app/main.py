import os
from dotenv import load_dotenv
import streamlit as st
import json
import folium
from streamlit_folium import st_folium
from sqlalchemy import create_engine
from llama_index import GPTSQLStructStoreIndex, SQLDatabase
from llama_index.indices.struct_store import SQLContextContainerBuilder
from langchain import OpenAI

##################################################################

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_PORT = os.getenv("DATABASE_PORT")
DATABASE_HOST = os.getenv("DATABASE_HOST")

llm_predictor = OpenAI(model_name="gpt-4")

connection_string = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
engine = create_engine(connection_string)

db = SQLDatabase(engine, include_tables=["stand_4326"])

stand_4326_text = (
    "The PostGis plugin is available in the database.\n"
    "The forest polygons can be found from the geometry column.\n"
    "Get the query as geojson."
)

table_context_dict = {
    "stand_4326": stand_4326_text,
}
context_builder = SQLContextContainerBuilder(db, context_dict=table_context_dict)
context_container = context_builder.build_context_container()

index = GPTSQLStructStoreIndex.from_documents(
    [],
    sql_database=db,
    table_name="stand_4326",
    sql_context_container=context_container,
)

####################################################################

def app():
    st.title("Forest Analyzer")

    tab1, tab2, tab3 = st.tabs(["Intro", "Tables", "Area"])

    with tab1:
        st.header("Intro")
        st.write("This is intro page..")

    with tab2:
        st.header("All tables")
        
        st.text_input("How many tables is in the database?", key="table_prompt")
        st.info(st.session_state.table_prompt)

    with tab3:
        st.header("Largest Area")

        st.text_input("Get the forest polygon with largest area?", key="prompt")

        if len(st.session_state.prompt) > 0:
            try:
                st.info("Creating a SQL query from given prompt..")
                st.session_state.response = index.query(st.session_state.prompt)
                
                st.session_state.sql_query = st.session_state.extra_info['sql_query']
                
                st.subheader("SQL Query:")
                st.code(st.session_state.sql_query, language="sql", line_numbers=False)
            except Exception as _:
                st.error("Could not make a SQL query from given prompt. Why not try some other prompt?")
                st.stop()
            
            try:
                st.info("Processing query data..")
                st.session_state.geojson = json.loads(st.session_state.response.extra_info["result"][0][0])
            except Exception as _:
                st.error("Could not process data into suitable format. Why not try some other prompt?")
                st.stop()

            try:
                st.info("Creating a map for query data..")
                coordinates = st.session_state.geojson["coordinates"][0][0][0]
                lat, lon = round(coordinates[1], 2), round(coordinates[0], 2)            
                loc = [lat, lon]
                st.session_state.folium_map = folium.Map(location=loc,zoom_start=12)
                folium.GeoJson(st.session_state.geojson).add_to(st.session_state.folium_map)

                st.subheader("Map:")
                st_folium(st.session_state.folium_map)
            except Exception as _:
                st.error("Could not create a map for query data. Why not try some other prompt?")
                st.stop()

if __name__ == "__main__":
    app()