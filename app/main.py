import os
import pandas as pd
from dotenv import load_dotenv
import streamlit as st
import json
from geoalchemy2 import Geometry
import pydeck as pdk
from sqlalchemy import create_engine
from llama_index import GPTSQLStructStoreIndex, SQLDatabase
from llama_index.indices.struct_store import SQLContextContainerBuilder
from langchain.chat_models import ChatOpenAI
import pydeck as pdk

##################################################################

    #################
    #               #
    #   Settings    #
    #               #
    #################

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_PORT = os.getenv("DATABASE_PORT")
DATABASE_HOST = os.getenv("DATABASE_HOST")

load_dotenv()

@st.cache_resource
def init_llm(model_name):
    return ChatOpenAI(model_name=model_name)

@st.cache_resource
def init_engine(connection_string):
    return create_engine(connection_string)

@st.cache_resource
def init_db(connection_string, include_tables=None):
    engine = init_engine(connection_string=connection_string)
    return SQLDatabase(
        engine,
        include_tables=include_tables
    )

@st.cache_resource
def init_context(context_dict, db_name):
    context_builder = SQLContextContainerBuilder(st.session_state[db_name], context_dict=context_dict)
    return context_builder.build_context_container()

@st.cache_resource
def init_index(
    docs,
    db_name,
    table_name=None,
    text=None,
):
    sql_context_container=None
    
    if text and table_name:
        table_context_dict = {
            table_name: text,
        }
        sql_context_container = init_context(db_name=db_name, context_dict=table_context_dict)
    
    return GPTSQLStructStoreIndex.from_documents(
        docs,
        sql_database=st.session_state[db_name],
        table_name=table_name,
        sql_context_container=sql_context_container,
    ) 

@st.cache_data
def query_data(query, db_name):
    return st.session_state[db_name].run_sql(query)

@st.cache_data
def initial_view_state(
    latitude,
    longitude,
    zoom,
):
    return pdk.ViewState(
            latitude=latitude,
            longitude=longitude,
            zoom=zoom,
        )

def common_init():
    load_dotenv()

    st.session_state.points = [0, 0, 0, 0]

    st.session_state.llm_predictor = init_llm(model_name="gpt-4")
    
    DATABASE_NAME = os.getenv("DATABASE_NAME")
    DATABASE_USER = os.getenv("DATABASE_USER")
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
    DATABASE_PORT = os.getenv("DATABASE_PORT")
    DATABASE_HOST = os.getenv("DATABASE_HOST")

    st.session_state.connection_string = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

    st.session_state.db = init_db(connection_string=st.session_state.connection_string, include_tables=["stand_4326"])
    st.session_state.db_all = init_db(connection_string=st.session_state.connection_string)

    st.session_state.index_all = init_index(
        docs=[],
        db_name="db_all"
    )
    
    st.session_state.latest_table_prompt = ""
    st.session_state.latest_area_prompt = ""
    st.session_state.latest_distance_prompt = ""
    st.session_state.latest_tree_prompt = ""
    st.session_state.latest_playground_prompt = ""

def tab3_init():
    st.session_state.area_geojson_res = query_data(
        query="""
            SELECT ST_AsGeoJSON(geometry) AS geojson, area 
            FROM stand_4326 
            ORDER BY area DESC 
            LIMIT 1;
        """,
        db_name="db",
    )

    st.session_state.area_geojson_gold_standard = json.dumps(json.loads(st.session_state.area_geojson_res[1]["result"][0][0]))

    stand_4326_text_tab3 = (
        "The PostGis plugin is available in the database.\n"
        "The forest polygons can be found from the geometry column.\n"
        "Get the query as geojson."
    )

    st.session_state.index_tab3 = init_index(
        docs=[],
        db_name="db",
        table_name="stand_4326",
        text=stand_4326_text_tab3,
    )

@st.cache_data
def init_tab4_layers(geojson_name):
    result_1 = json.loads(st.session_state[geojson_name][1]["result"][0][0])
    result_2 = json.loads(st.session_state[geojson_name][1]["result"][0][1])

    point_1 = result_1['coordinates'][0][0][36]
    point_2 = result_2['coordinates'][0][0][67]

    distance_line = [{"start": point_1, "end": point_2}]

    geojson_layer_1 = pdk.Layer(
        "GeoJsonLayer",
        result_1,
        opacity=0.6,
        filled=True,
        get_fill_color="[255, 125, 0]",
        get_line_color="[255, 125, 0]",
        highlight_color=[255, 255, 0],
        auto_highlight=True,
        picking_radius=10,
        pickable=True,
    )

    geojson_layer_2 = pdk.Layer(
        "GeoJsonLayer",
        result_2,
        opacity=0.6,
        filled=True,
        get_fill_color="[255, 125, 0]",
        get_line_color="[255, 125, 0]",
        highlight_color=[255, 255, 0],
        auto_highlight=True,
        picking_radius=10,
        pickable=True,
    )

    line_layer = pdk.Layer(
        "LineLayer",
        distance_line,
        get_color="[255, 125, 0]",
        highlight_color=[255, 255, 0],
        get_source_position="start",
        get_target_position="end",
        get_width=3,
        auto_highlight=True,
        picking_radius=10,
        pickable=True,
    )
    return [geojson_layer_1, geojson_layer_2, line_layer]

def tab4_init():
    stand_4326_text_tab4 = (
        "I have postgreSQL database with PostGis geospatial forest data.\n"
        "The PostGis plugin is available in the database.\n"
        "The forest polygons can be found from the geometry column.\n"
        "Use ST_DistanceSphere function and divide with 1000 when calculating the distance.\n"
    )

    st.session_state.index_tab4 = init_index(
        docs=[],
        db_name="db",
        table_name="stand_4326",
        text=stand_4326_text_tab4,
    )
    
    try:            
        st.session_state.geojson_res = query_data(
            query="""
                SELECT ST_AsGeoJSON(s1.geometry) AS g1, ST_AsGeoJSON(s2.geometry) AS g2
                FROM stand_4326 s1, stand_4326 s2
                WHERE s1.id = 228942 AND s2.id = 298208  
                LIMIT 1;
            """,
            db_name="db",
        )

        st.session_state.distance_initial_view_state = initial_view_state(
            latitude=60.7,
            longitude=21.9,
            zoom=9.5
        )

        st.session_state.tab4_layers = init_tab4_layers(geojson_name="geojson_res")
    except Exception as error:
            st.error("Could not create a map for tab 4.")
            st.error(error)
            st.stop()

def tab5_init():
    st.session_state.tree_geojson_res = query_data(
        query="""
            SELECT id, ST_AsGeoJSON(geometry) FROM stand_4326 WHERE maintreespecies = 2 AND area IS NOT NULL ORDER BY area DESC LIMIT 1;
        """,
        db_name="db",
    )

    st.session_state.tree_geojson_gold_standard = json.dumps(json.loads(st.session_state.tree_geojson_res[1]["result"][0][1]))

    stand_4326_text_tab5 = (
        "I have postgreSQL database with PostGis geospatial forest data.\n"
        "The PostGis plugin is available in the database.\n"
        "The forest polygons can be found from the geometry column.\n"
        "Get the geometry as geojson.\n"
        "Don't include NULL values.\n"
    )

    st.session_state.index_tab5 = init_index(
        docs=[],
        db_name="db",
        table_name="stand_4326",
        text=stand_4326_text_tab5,
    )

def tab6_init():
    stand_4326_text_tab6 = (
        "I have postgreSQL database with PostGis geospatial forest data.\n"
        "The PostGis plugin is available in the database.\n"
        "The forest polygons can be found from the geometry column.\n"
        "Get the geometry as geojson.\n"
    )

    st.session_state.index_tab6 = init_index(
        docs=[],
        db_name="db_all",
        text=stand_4326_text_tab6,
    )


def init():
    common_init()

    tab3_init()

    tab4_init()

    tab5_init()

    tab6_init()

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
@st.cache_data
def tab2_query(prompt):
    return st.session_state.index_all.query(prompt)

def all_tab(points_bar):
    st.header("All tables")
    
    # Get the names of all tables in database
    st.text_input("Get the names of all tables in database", key="table_prompt")
    
    if len(st.session_state.table_prompt) > 0:
        # Process
        with st.spinner(text="Getting response..."):
            if st.session_state.table_prompt != st.session_state.latest_table_prompt:
                try:
                    st.session_state.all_tables_response = tab2_query(st.session_state.table_prompt)
                    st.session_state.latest_table_prompt = st.session_state.table_prompt
                except Exception as e:
                    st.error(e)
                    st.stop()

            try:
                st.info("Creating a SQL query from given prompt..")
                st.session_state.all_tables_query = st.session_state.all_tables_response.extra_info["sql_query"]
            except Exception as error:
                st.error("Could not make a SQL query from given prompt. Why not try some other prompt?")
                st.error(error)
                st.stop()

            try:
                st.info("Processing query data..")
                st.session_state.all_tables_result = st.session_state.all_tables_response.extra_info["result"]

                if type(st.session_state.all_tables_result).__name__ == 'list':
                    st.session_state.all_tables_list = [m[0] for m in st.session_state.all_tables_result]
            except Exception as error:
                st.error("Could not process data into suitable format. Why not try some other prompt?")
                st.error(error)
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

####################################################################

    ##############
    #            #
    #   Tab 3    #
    #            #
    ##############

@st.cache_data
def tab3_query(prompt):
    return st.session_state.index_tab3.query(prompt)

def area_tab(points_bar):
    st.header("Largest Area")

    # Get the forest polygon with largest area
    st.text_input("Get the forest polygon with largest area", key="area_prompt")

    if len(st.session_state.area_prompt) > 0:
        # Process
        with st.spinner(text="Getting response..."):
            if st.session_state.area_prompt != st.session_state.latest_area_prompt:
                try:
                    st.session_state.area_response = tab3_query(st.session_state.area_prompt)
                    st.session_state.latest_area_prompt = st.session_state.area_prompt
                except Exception as e:
                    st.error(e)
                    st.stop()

                try:
                    st.info("Creating a SQL query from given prompt..")
                    st.session_state.area_sql_query = st.session_state.area_response.extra_info['sql_query']
                except Exception as error:
                    st.error("Could not make a SQL query from given prompt. Why not try some other prompt?")
                    st.error(error)
                    st.stop()

                try:
                    st.info("Processing query data..")
                    st.session_state.area_geojson = json.loads(st.session_state.area_response.extra_info["result"][0][0])
                except Exception as error:
                    st.error("Could not process data into suitable format. Why not try some other prompt?")
                    st.error(error)
                    st.stop()

                try:
                    st.info("Creating a map for query data..")
                    st.session_state.is_area_map_ready_to_draw = False
                    
                    coordinates = st.session_state.area_geojson["coordinates"][0][0][0]
                    lat, lon = round(coordinates[1], 2), round(coordinates[0], 2)            
                    st.session_state.area_initial_view_state = pdk.ViewState(
                        latitude=lat,
                        longitude=lon,
                        zoom=10
                    )

                    st.session_state.area_geojson_layer = pdk.Layer(
                        "GeoJsonLayer",
                        st.session_state.area_geojson,
                        opacity=0.6,
                        filled=True,
                        get_fill_color="[255, 125, 0]",
                        get_line_color="[255, 125, 0]",
                        highlight_color=[255, 255, 0],
                        auto_highlight=True,
                        picking_radius=10,
                        pickable=True,
                    )
                    
                    st.session_state.is_area_map_ready_to_draw = True
                except Exception as error:
                    st.error("Could not create a map for query data. Why not try some other prompt?")
                    st.error(error)
                    st.stop()

        # Draw
        if type(st.session_state.area_sql_query).__name__ == 'str':
            st.subheader("SQL Query:")
            st.code(st.session_state.area_sql_query, language="sql", line_numbers=False)

        if type(st.session_state.area_geojson).__name__ == 'dict':
            st.subheader("GeoJson:")
            st.json(st.session_state.area_geojson, expanded=False)

        if st.session_state.is_area_map_ready_to_draw:
            st.subheader("Map:")
            st.pydeck_chart(
                pdk.Deck(
                    map_style="dark",
                    initial_view_state=st.session_state.area_initial_view_state,
                    layers=[st.session_state.area_geojson_layer]
                )
            )

        # Task result
        if type(st.session_state.area_geojson).__name__ == 'dict' and json.dumps(st.session_state.area_geojson) == st.session_state.area_geojson_gold_standard:
            st.session_state.points[1] = 1
            points_bar.progress(
                int(sum(st.session_state.points)/len(st.session_state.points)*100),
                text=f"{sum(st.session_state.points)}/{len(st.session_state.points)}"
            )
            st.success("You did it!")

####################################################################

    ##############
    #            #
    #   Tab 4    #
    #            #
    ##############

@st.cache_data
def tab4_query(prompt):
    return st.session_state.index_tab4.query(prompt)

def distance_tab(points_bar):
    gold_standard = 18.37

    st.header("Distance between two forest areas")
    st.subheader("Map:")
    st.pydeck_chart(
        pdk.Deck(
            map_style="dark",
            initial_view_state=st.session_state.distance_initial_view_state,
            layers=st.session_state.tab4_layers,
        )
    )

    # Query the distance between two forests in km by giving the ids 228942 and 298208 of forests
    st.text_input("Query the distance between two forests in km by giving the ids 228942 and 298208 of forests", key="distance_prompt")
    
    if len(st.session_state.distance_prompt) > 0:
        # Process
        with st.spinner(text="Getting response..."):
            if st.session_state.distance_prompt != st.session_state.latest_distance_prompt:
                try:
                    st.session_state.distance_response = tab4_query(st.session_state.distance_prompt)
                    st.session_state.latest_distance_prompt = st.session_state.distance_prompt
                except Exception as e:
                    st.error(e)
                    st.stop()

                try:
                    st.info("Creating a SQL query from given prompt..")
                    st.session_state.distance_sql_query = st.session_state.distance_response.extra_info['sql_query']
                except Exception as error:
                    st.error("Could not make a SQL query from given prompt. Why not try some other prompt?")
                    st.error(error)
                    st.stop()
            
                try:
                    st.info("Processing query data..")
                    st.session_state.distance_result = round(st.session_state.distance_response.extra_info["result"][0][0], 2)

                except Exception as error:
                    st.error("Could not process data into suitable format. Why not try some other prompt?")
                    st.error(error)
                    st.stop()

        # Draw
        if type(st.session_state.distance_sql_query).__name__ == 'str':
            st.subheader("SQL Query:")
            st.code(st.session_state.distance_sql_query, language="sql", line_numbers=False)

        if type(st.session_state.distance_result).__name__ == 'int':
            st.subheader("Query result:")
            st.metric(
                label="Query Result:",
                value=f"{st.session_state.distance_result} km",
                delta=f"{st.session_state.distance_result - gold_standard} km",
            )

        # Task result
        if st.session_state.distance_result and st.session_state.distance_result - gold_standard == 0.0:
            st.session_state.points[2] = 1
            points_bar.progress(
                int(sum(st.session_state.points)/len(st.session_state.points)*100),
                text=f"{sum(st.session_state.points)}/{len(st.session_state.points)}"
            )
            st.success("You did it!")

####################################################################

    ##############
    #            #
    #   Tab 5    #
    #            #
    ##############

@st.cache_data
def tab5_query(prompt):
    return st.session_state.index_tab5.query(prompt)

def tree_species_tab(points_bar):
    st.header("Main tree species:")

    tree_data = { "maintreespecies": [1, 2, 29], "nimi": ["Mänty", "Kuusi", "Lehtipuu"], "name": ["Pine", "Spruce", "Leafy tree"] }
    tree_df = pd.DataFrame(data=tree_data)

    st.info("Below is a table of maintreespecies found in database.")
    st.dataframe(tree_df)

    # Get the id and forest polygon of forest with larges area that has main tree species 2. Don't include NULL values.
    st.text_input("Get the id and forest polygon of forest with largest area that has main tree species spruce", key="tree_prompt")

    if len(st.session_state.tree_prompt) > 0:
        # Process
        with st.spinner(text="Getting response..."):
            if st.session_state.tree_prompt != st.session_state.latest_tree_prompt:
                try:
                    st.session_state.tree_response = tab5_query(st.session_state.tree_prompt)
                    st.session_state.latest_tree_prompt = st.session_state.tree_prompt
                except Exception as e:
                    st.error(e)
                    st.stop

                try:
                    st.info("Creating a SQL query from givern prompt..")
                    st.session_state.tree_sql_query = st.session_state.tree_response.extra_info['sql_query']
                except Exception as e:
                    st.error(e)
                    st.stop()

                try:
                    st.info("Processing query data..")
                    st.session_state.tree_result = st.session_state.tree_response.extra_info["result"][0]
                    st.session_state.tree_id, tree_polygon = st.session_state.tree_result
                    st.session_state.tree_polygon_geojson = json.loads(tree_polygon)
                except Exception as e:
                    st.error(e)
                    st.stop()

                try:
                    st.info("Creating a map for query data..")
                    st.session_state.is_tree_map_ready_to_draw = False

                    coordinates = st.session_state.tree_polygon_geojson["coordinates"][0][0][0]
                    lat, lon = round(coordinates[1], 2), round(coordinates[0], 2)            
                    st.session_state.tree_initial_view_state = pdk.ViewState(
                        latitude=lat,
                        longitude=lon,
                        zoom=10
                    )

                    st.session_state.tree_geojson_layer = pdk.Layer(
                        "GeoJsonLayer",
                        st.session_state.tree_polygon_geojson,
                        opacity=0.6,
                        filled=True,
                        get_fill_color="[255, 125, 0]",
                        get_line_color="[255, 125, 0]",
                        highlight_color=[255, 255, 0],
                        auto_highlight=True,
                        picking_radius=10,
                        pickable=True,
                    )
                    st.session_state.is_tree_map_ready_to_draw = True
                except Exception as e:
                    st.error(e)
                    st.stop()
        
        #Draw
        if type(st.session_state.tree_sql_query).__name__ == 'str':
            st.subheader("SQL Query:")
            st.code(st.session_state.tree_sql_query, language="sql", line_numbers=False)

        if type(st.session_state.tree_id).__name__ == 'int' and type(st.session_state.tree_polygon_geojson).__name__ == 'dict':
            st.subheader("Query result:")
            st.info(f"Id: {st.session_state.tree_id}")
            st.json(st.session_state.tree_polygon_geojson, expanded=False)

        if st.session_state.is_tree_map_ready_to_draw:
            st.subheader("Map:")
            st.pydeck_chart(
                pdk.Deck(
                    map_style="dark",
                    initial_view_state=st.session_state.tree_initial_view_state,
                    layers=[st.session_state.tree_geojson_layer]
                )
            )

        # Task result
        if type(st.session_state.tree_polygon_geojson).__name__ == 'dict' and json.dumps(st.session_state.tree_polygon_geojson) == st.session_state.tree_geojson_gold_standard:
            st.session_state.points[3] = 1
            points_bar.progress(
                int(sum(st.session_state.points)/len(st.session_state.points)*100),
                text=f"{sum(st.session_state.points)}/{len(st.session_state.points)}"
            )
            st.success("You did it!")

####################################################################

    ##############
    #            #
    #   Tab 6    #
    #            #
    ##############

@st.cache_data
def tab6_query(prompt):
    return st.session_state.index_tab6.query(prompt)

def playground_tab():
    st.header("Playground:")

    st.markdown("Try any prompt you wan't and see what kind of SQL queries the LLM generates for you.")

    st.text_input("Prompt:", key="playground_prompt")

    if len(st.session_state.playground_prompt) > 0:
        #Process
        with st.spinner(text="Getting response..."):
            if st.session_state.playground_prompt != st.session_state.latest_playground_prompt:
                try:
                    st.session_state.playground_response = tab6_query(st.session_state.playground_prompt)
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
    

####################################################################

    ############
    #          #
    #   App    #
    #          #
    ############

def app():
    st.title("Forest Analyzer")

    st.subheader("Points:")
    points_bar = st.progress(
        int(sum(st.session_state.points) / len(st.session_state.points) * 100),
        text=f"{sum(st.session_state.points)}/{len(st.session_state.points)}"
    )

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Intro", "Tables", "Area", "Distance", "Tree species", "Playground"])

    with tab1:
        intro_tab()

    with tab2:
        all_tab(points_bar=points_bar)

    with tab3:
        area_tab(points_bar=points_bar)

    with tab4:
        distance_tab(points_bar=points_bar)
    
    with tab5:
        tree_species_tab(points_bar=points_bar)

    with tab6:
        playground_tab()

####################################################################

    #############
    #           #
    #   Main    #
    #           #
    #############

if __name__ == "__main__":
    init()
    app()