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

with st.spinner('Wait for it...'):
    st.session_state.points = [0, 0, 0, 0]

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

    db_all = SQLDatabase(engine)
    db = SQLDatabase(engine, include_tables=["stand_4326"])

    index_all = GPTSQLStructStoreIndex.from_documents(
        [],
        sql_database=db_all,
    )

        ####################
        #                  #
        #   Tab 3 Index    #
        #                  #
        ####################

    stand_4326_text_tab3 = (
        "The PostGis plugin is available in the database.\n"
        "The forest polygons can be found from the geometry column.\n"
        "Get the query as geojson."
    )

    table_context_dict_tab3 = {
        "stand_4326": stand_4326_text_tab3,
    }
    context_builder_tab3 = SQLContextContainerBuilder(db, context_dict=table_context_dict_tab3)
    context_container_tab3 = context_builder_tab3.build_context_container()
    index_tab3 = GPTSQLStructStoreIndex.from_documents(
        [],
        sql_database=db,
        table_name="stand_4326",
        sql_context_container=context_container_tab3,
    )

        ####################
        #                  #
        #   Tab 4 Index    #
        #                  #
        ####################

    stand_4326_text_tab4 = (
        "I have postgreSQL database with PostGis geospatial forest data.\n"
        "The PostGis plugin is available in the database.\n"
        "The forest polygons can be found from the geometry column.\n"
        "Use ST_DistanceSphere function and divide with 1000 when calculating the distance.\n"
    )

    table_context_dict_tab4 = {
        "stand_4326": stand_4326_text_tab4,
    }
    context_builder_tab4 = SQLContextContainerBuilder(db, context_dict=table_context_dict_tab4)
    context_container_tab4 = context_builder_tab4.build_context_container()
    index_tab4 = GPTSQLStructStoreIndex.from_documents(
        [],
        sql_database=db,
        table_name="stand_4326",
        sql_context_container=context_container_tab4,
    )

        ####################
        #                  #
        #   Tab 5 Index    #
        #                  #
        ####################

    stand_4326_text_tab5 = (
        "I have postgreSQL database with PostGis geospatial forest data.\n"
        "The PostGis plugin is available in the database.\n"
        "The forest polygons can be found from the geometry column.\n"
        "Get the geometry as geojson.\n"
        "Don't include NULL values.\n"
    )

    table_context_dict_tab5 = {
        "stand_4326": stand_4326_text_tab5,
    }
    context_builder_tab5 = SQLContextContainerBuilder(db, context_dict=table_context_dict_tab5)
    context_container_tab5 = context_builder_tab5.build_context_container()
    index_tab5 = GPTSQLStructStoreIndex.from_documents(
        [],
        sql_database=db,
        table_name="stand_4326",
        sql_context_container=context_container_tab5,
    )

        #################
        #               #
        #   Tab 4 Map   #
        #               #
        #################

    try:            
        geojson_res = db.run_sql(
            """
                SELECT ST_AsGeoJSON(s1.geometry) AS g1, ST_AsGeoJSON(s2.geometry) AS g2
                FROM stand_4326 s1, stand_4326 s2
                WHERE s1.id = 228942 AND s2.id = 298208  
                LIMIT 1;
            """
        )

        initial_view_state = pdk.ViewState(
            latitude=60.7,
            longitude=21.9,
            zoom=9.5
        )

        result_1 = json.loads(geojson_res[1]["result"][0][0])
        result_2 = json.loads(geojson_res[1]["result"][0][1])

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

        st.session_state.tab4_layers = [geojson_layer_1, geojson_layer_2, line_layer]
    except Exception as error:
            st.error("Could not create a map for tab 4.")
            st.error(error)
            st.stop()

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

def all_tab(points_bar):
    st.header("All tables")
    
    # Get the names of all tables in database
    st.text_input("Get the names of all tables in database", key="table_prompt")
    
    if len(st.session_state.table_prompt) > 0:
        try:
            st.info("Creating a SQL query from given prompt..")
            
            all_tables_response = index_all.query(st.session_state.table_prompt)
            all_tables_query = all_tables_response.extra_info["sql_query"]

            st.subheader("SQL Query:")
            st.code(all_tables_query, language='sql', line_numbers=False)
        except Exception as error:
            st.error("Could not make a SQL query from given prompt. Why not try some other prompt?")
            st.error(error)
            st.stop()

        try:
            st.info("Processing query data..")

            all_tables_result = all_tables_response.extra_info["result"]

            if type(all_tables_result).__name__ == 'list':
                all_tables_list = [m[0] for m in all_tables_result]

                st.subheader("Tables:")
                
                df = pd.DataFrame(
                    all_tables_list,
                    columns=['Tables']
                )
                
                st.table(df)

                if True:
                    st.session_state.points[0] = 1
                    points_bar.progress(
                        int(sum(st.session_state.points)/len(st.session_state.points)*100),
                        text=f"{sum(st.session_state.points)}/{len(st.session_state.points)}"
                    )
                    st.success("You did it!")
            else:
                raise Exception("Result is not a list")
        except Exception as error:
            st.error("Could not process data into suitable format. Why not try some other prompt?")
            st.error(error)
            st.stop()

####################################################################

    ##############
    #            #
    #   Tab 3    #
    #            #
    ##############
def area_tab(points_bar):
    st.header("Largest Area")

    # Get the forest polygon with largest area
    st.text_input("Get the forest polygon with largest area", key="prompt")

    if len(st.session_state.prompt) > 0:
        try:
            st.info("Creating a SQL query from given prompt..")
            st.session_state.response = index_tab3.query(st.session_state.prompt)
            
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

            st.subheader("GeoJson:")
            st.json(st.session_state.geojson, expanded=False)
        except Exception as error:
            st.error("Could not process data into suitable format. Why not try some other prompt?")
            st.error(error)
            st.stop()

        try:
            st.info("Creating a map for query data..")
            
            coordinates = st.session_state.geojson["coordinates"][0][0][0]
            lat, lon = round(coordinates[1], 2), round(coordinates[0], 2)            
            initial_view_state = pdk.ViewState(
                latitude = lat,
                longitude=lon,
                zoom=10
            )

            geojson_layer = pdk.Layer(
                "GeoJsonLayer",
                st.session_state.geojson,
                opacity=0.6,
                filled=True,
                get_fill_color="[255, 125, 0]",
                get_line_color="[255, 125, 0]",
                highlight_color=[255, 255, 0],
                auto_highlight=True,
                picking_radius=10,
                pickable=True,
            )
            
            st.subheader("Map:")
            st.pydeck_chart(
                pdk.Deck(
                    map_style="dark",
                    initial_view_state=initial_view_state,
                    layers=[geojson_layer]
                )
            )
            
            if True:
                st.session_state.points[1] = 1
                points_bar.progress(
                    int(sum(st.session_state.points)/len(st.session_state.points)*100),
                    text=f"{sum(st.session_state.points)}/{len(st.session_state.points)}"
                )
                st.success("You did it!")
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

def distance_tab(points_bar):
    st.header("Distance between two forest areas")
    st.subheader("Map:")
    st.pydeck_chart(
        pdk.Deck(
            map_style="dark",
            initial_view_state=initial_view_state,
            layers=st.session_state.tab4_layers,
        )
    )

    # Query the distance between two forests in km by giving the ids 228942 and 298208 of forests
    st.text_input("Query the distance between two forests in km by giving the ids 228942 and 298208 of forests", key="distance_prompt")

    if len(st.session_state.distance_prompt) > 0:
        try:
            st.info("Creating a SQL query from givern prompt..")
            st.session_state.response = index_tab4.query(st.session_state.distance_prompt)

            st.session_state.sql_query = st.session_state.response.extra_info['sql_query']

            st.subheader("SQL Query:")
            st.code(st.session_state.sql_query, language="sql", line_numbers=False)
        except Exception as error:
            st.error("Could not make a SQL query from given prompt. Why not try some other prompt?")
            st.error(error)
            st.stop()

        try:
            st.info("Processing query data..")
            st.session_state.distance_result = round(st.session_state.response.extra_info["result"][0][0], 2)
            gold_standard = 18.37

            st.subheader("Query result:")
            st.metric(
                label="Query Result:",
                value=f"{st.session_state.distance_result} km",
                delta=f"{st.session_state.distance_result - gold_standard} km",
            )
            
            if st.session_state.distance_result - gold_standard == 0.0:
                st.session_state.points[2] = 1
                points_bar.progress(
                    int(sum(st.session_state.points)/len(st.session_state.points)*100),
                    text=f"{sum(st.session_state.points)}/{len(st.session_state.points)}"
                )
                st.success("You did it!")
        except Exception as error:
            st.error("Could not process data into suitable format. Why not try some other prompt?")
            st.error(error)
            st.stop()

####################################################################

    ##############
    #            #
    #   Tab 5    #
    #            #
    ##############

def tree_species_tab(points_bar):
    st.header("Main tree species:")

    tree_data = { "maintreespecies": [1, 2, 29], "nimi": ["Mänty", "Kuusi", "Lehtipuu"], "name": ["Pine", "Spruce", "Leafy tree"] }
    tree_df = pd.DataFrame(data=tree_data)

    st.info("Below is a table of maintreespecies found in database.")
    st.dataframe(tree_df)

    # Get the id and forest polygon of forest with larges area that has main tree species 2. Don't include NULL values.
    st.text_input("Get the id and forest polygon of forest with largest area that has main tree species spruce", key="tree_prompt")

    if len(st.session_state.tree_prompt) > 0:
        try:
            st.info("Creating a SQL query from givern prompt..")
            st.session_state.tree_response = index_tab5.query(st.session_state.tree_prompt)

            st.session_state.tree_sql_query = st.session_state.tree_response.extra_info['sql_query']

            st.subheader("SQL Query:")
            st.code(st.session_state.tree_sql_query, language="sql", line_numbers=False)
        except Exception as e:
            st.error(e)
            st.stop()

        try:
            st.info("Processing query data..")
            
            st.session_state.tree_result = st.session_state.tree_response.extra_info["result"][0]
            tree_id, tree_polygon = st.session_state.tree_result
            tree_polygon_geojson = json.loads(tree_polygon)
            
            st.subheader("Query result:")
            st.info(f"Id: {tree_id}")
            st.json(tree_polygon_geojson, expanded=False)
        except Exception as e:
            st.error(e)
            st.stop()

        try:
            st.info("Creating a map for query data..")
            
            coordinates = tree_polygon_geojson["coordinates"][0][0][0]
            lat, lon = round(coordinates[1], 2), round(coordinates[0], 2)            
            initial_view_state = pdk.ViewState(
                latitude=lat,
                longitude=lon,
                zoom=10
            )

            tree_geojson_layer = pdk.Layer(
                "GeoJsonLayer",
                tree_polygon_geojson,
                opacity=0.6,
                filled=True,
                get_fill_color="[255, 125, 0]",
                get_line_color="[255, 125, 0]",
                highlight_color=[255, 255, 0],
                auto_highlight=True,
                picking_radius=10,
                pickable=True,
            )
            
            st.subheader("Map:")
            st.pydeck_chart(
                pdk.Deck(
                    map_style="dark",
                    initial_view_state=initial_view_state,
                    layers=[tree_geojson_layer]
                )
            )
        except Exception as e:
            st.error(e)
            st.stop()

        try:
            if True:
                st.session_state.points[3] = 1
                points_bar.progress(
                    int(sum(st.session_state.points)/len(st.session_state.points)*100),
                    text=f"{sum(st.session_state.points)}/{len(st.session_state.points)}"
                )
                st.success("You did it!")
        except Exception as e:
            st.error(e)
            st.stop()

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

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Intro", "Tables", "Area", "Distance", "Tree species"])

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

####################################################################

    #############
    #           #
    #   Main    #
    #           #
    #############

if __name__ == "__main__":
    app()