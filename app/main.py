import os
from dotenv import load_dotenv
import streamlit as st
import json
from geoalchemy2 import Geometry
import folium
from streamlit_folium import st_folium
from sqlalchemy import create_engine
from llama_index import GPTSQLStructStoreIndex, SQLDatabase
from llama_index.indices.struct_store import SQLContextContainerBuilder
from langchain.chat_models import ChatOpenAI

##################################################################

    #################
    #               #
    #   Settings    #
    #               #
    #################

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_PORT = os.getenv("DATABASE_PORT")
DATABASE_HOST = os.getenv("DATABASE_HOST")

llm_predictor = ChatOpenAI(model_name="gpt-4")

connection_string = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
engine = create_engine(connection_string)

db = SQLDatabase(engine, include_tables=["stand_4326"])
st.session_state.folium_map = folium.Map()

####################################################################

    ##############
    #            #
    #   Tab 1    #
    #            #
    ##############

def intro_tab():
    st.header("SQL queries with Natural Language Processing")

    st.markdown("Thank you for joining us today! We are Three Point Consulting and we have prepaired a little game for you to play today. We'll tell you more about it shortly, but let's kick things off with a short introduction to Natural Language Processing or NLP in short.")

    st.subheader("A short introduction to NLP")
    st.markdown("NLP is a branch of artificial intelligence that focuses on enabling computers to understand, interpret, and generate human language. Many of you may have experienced this technology with OpenAI's ChatGPT. In fact, this game is powered by the same language model as the ChatGPT+, which is GPT-4. NLP's applications include topics, such as chatbots, semantic search, machine translation, document- and sentiment analysis. We don't want to bother you with the mathematical or technical details of language models or NLP in general, but we are more than happy to discuss these topics if you are interested so don't be afraid to ask!")
    
    st.subheader("SQL and Geospatial data")
    st.markdown("You might also be pretty well acquinted with SQL. If you are not, SQL is a declarative language which allows user to search (or query) data from databases. Today we are going to introduce you to quering data using only natural language, so no more annoying joins, subqueries, etc!")
    
    st.subheader("Your task")
    st.markdown("We are running a Supabase instance locally where different geospatial forest data is stored. PLACEHOLDER You are supposed search (or prompt) the largest forest polygon from our database using only natural language. The SQL query which is created from the prompt is displayed on the exercise page.")

####################################################################

    ##############
    #            #
    #   Tab 2    #
    #            #
    ##############

def all_tab():
    st.header("All tables")
    
    st.text_input("How many tables is in the database?", key="table_prompt")
    st.info(st.session_state.table_prompt)

####################################################################

    ##############
    #            #
    #   Tab 3    #
    #            #
    ##############

def area_tab():
    # Context
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

    # Content
    st.header("Largest Area")

    st.text_input("Get the forest polygon with largest area?", key="prompt")

    if len(st.session_state.prompt) > 0:
        try:
            st.info("Creating a SQL query from given prompt..")
            st.session_state.response = index.query(st.session_state.prompt)
            
            st.session_state.sql_query = st.session_state.response.extra_info['sql_query']
            
            st.subheader("SQL Query:")
            st.code(st.session_state.sql_query, language="sql", line_numbers=False)
        except Exception as error:
            st.error("Could not make a SQL query from given prompt. Why not try some other prompt?")
            st.error(error)
            st.stop()
        
        try:
            st.info("Processing query data..")
            st.session_state.geojson = json.loads(st.session_state.response.extra_info["result"][0][0])
        except Exception as error:
            st.error("Could not process data into suitable format. Why not try some other prompt?")
            st.error(error)
            st.stop()

        try:
            st.info("Creating a map for query data..")
            
            coordinates = st.session_state.geojson["coordinates"][0][0][0]
            
            lat, lon = round(coordinates[1], 2), round(coordinates[0], 2)            
            loc = [lat, lon]
            
            st.session_state.folium_map = folium.Map(location=loc, zoom_start=12)

            folium.GeoJson(st.session_state.geojson).add_to(st.session_state.folium_map)

            st.subheader("Map:")
            st_folium(st.session_state.folium_map)
        except Exception as error:
            st.error("Could not create a map for query data. Why not try some other prompt?")
            st.error(error)
            st.stop()

####################################################################

    ##############
    #            #
    #   Tab 4    #
    #            #
    ##############

def distance_tab():
    # Context
    stand_4326_text = (
        "I have postgreSQL database with PostGis geospatial forest data.\n"
        "The PostGis plugin is available in the database.\n"
        "The forest polygons can be found from the geometry column.\n"
        "Use ST_DistanceSphere function and divide with 1000 when calculating the distance.\n"
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

    # Content
    st.header("Distance between two forest areas")

    try:            
        geojson_res = db.run_sql(
            """
                SELECT ST_AsGeoJSON(s1.geometry) AS g1, ST_AsGeoJSON(s2.geometry) AS g2
                FROM stand_4326 s1, stand_4326 s2
                WHERE s1.id = 228942 AND s2.id = 69028  
                LIMIT 1;
            """
        )

        loc = [60.2, 22.3]
        st.session_state.folium_map = folium.Map(location=loc, zoom_start=9)
        
        folium.GeoJson(json.loads(geojson_res[1]["result"][0][0])).add_to(st.session_state.folium_map)
        folium.GeoJson(json.loads(geojson_res[1]["result"][0][1])).add_to(st.session_state.folium_map)

        st.subheader("Map:")
        st_folium(st.session_state.folium_map)
    except Exception as error:
        st.error("Could not create a map for task.")
        st.error(error)
        st.stop()

    st.text_input("Query the distance between two forests in km by giving the ids 228942 and 69028 of forests", key="distance_prompt")

    if len(st.session_state.distance_prompt) > 0:
        try:
            st.info("Creating a SQL query from givern prompt..")
            st.session_state.response = index.query(st.session_state.distance_prompt)

            st.session_state.sql_query = st.session_state.response.extra_info['sql_query']

            st.subheader("SQL Query:")
            st.code(st.session_state.sql_query, language="sql", line_numbers=False)
        except Exception as error:
            st.error("Could not make a SQL query from given prompt. Why not try some other prompt?")
            st.error(error)
            st.stop()

####################################################################

    ############
    #          #
    #   App    #
    #          #
    ############

def app():
    st.title("Forest Analyzer")

    tab1, tab2, tab3, tab4 = st.tabs(["Intro", "Tables", "Area", "Distance"])

    with tab1:
        intro_tab()

    with tab2:
        all_tab()

    with tab3:
        area_tab()

    with tab4:
        distance_tab()

####################################################################

    #############
    #           #
    #   Main    #
    #           #
    #############

if __name__ == "__main__":
    app()