import json
import streamlit as st
import pydeck as pdk

from utils import index, view
from utils.query import sql

@st.cache_data
def init_layers(geojson_name):
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

def init():
    st.session_state.latest_distance_prompt = ""

    text = (
        "I have postgreSQL database with PostGis geospatial forest data.\n"
        "The PostGis plugin is available in the database.\n"
        "The forest polygons can be found from the geometry column.\n"
        "Use ST_DistanceSphere function and divide with 1000 when calculating the distance.\n"
    )

    st.session_state.index_tab4 = index.init(
        docs=[],
        db_name="db",
        table_name="stand_4326",
        text=text,
    )
    
    try:            
        st.session_state.geojson_res = sql(
            query="""
                SELECT ST_AsGeoJSON(s1.geometry) AS g1, ST_AsGeoJSON(s2.geometry) AS g2
                FROM stand_4326 s1, stand_4326 s2
                WHERE s1.id = 228942 AND s2.id = 298208  
                LIMIT 1;
            """,
            db_name="db",
        )

        st.session_state.distance_initial_view_state = view.initial_view_state(
            latitude=60.7,
            longitude=21.9,
            zoom=9.5
        )

        st.session_state.tab4_layers = init_layers(geojson_name="geojson_res")
    except Exception as error:
            st.error("Could not create a map for tab 4.")
            st.error(error)
            st.stop()

@st.cache_data
def query(prompt):
    return st.session_state.index_tab4.query(prompt)

def tab(points_bar):
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
    st.markdown("We have to forest plots with `id` values `228942` and `298208`. Your taks is to get the distance between the two forests in kilometers.")
    st.text_input("Prompt", key="distance_prompt")
    
    if len(st.session_state.distance_prompt) > 0:
        # Process
        with st.spinner(text="Getting response..."):
            if st.session_state.distance_prompt != st.session_state.latest_distance_prompt:
                try:
                    st.session_state.distance_response = query(st.session_state.distance_prompt)
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

        if st.session_state.distance_result:
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