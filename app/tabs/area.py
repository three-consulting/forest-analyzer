import json
import streamlit as st
import pydeck as pdk

from utils import index, query, view
from utils.query import sql

def init():
    st.session_state.latest_area_prompt = ""
    
    st.session_state.area_geojson_res = sql(
        query="""
            SELECT ST_AsGeoJSON(geometry) AS geojson, area 
            FROM stand_4326 
            ORDER BY area DESC 
            LIMIT 1;
        """,
        db_name="db",
    )

    st.session_state.area_geojson_gold_standard = json.dumps(json.loads(st.session_state.area_geojson_res[1]["result"][0][0]))

    text = (
        "The PostGis plugin is available in the database.\n"
        "The forest polygons can be found from the geometry column.\n"
        "Get the query as geojson."
    )

    st.session_state.index_tab3 = index.init(
        docs=[],
        db_name="db",
        table_name="stand_4326",
        text=text,
    )

@st.cache_data
def query(prompt):
    return st.session_state.index_tab3.query(prompt)

def tab(points_bar):
    st.header("Largest Area")

    # Get the forest polygon with largest area
    st.markdown("In table `stand_4326` we have general informations about forest plots. The shape of the forest is in polygon form. Your task is to find polygon of forest with largest area.")
    st.text_input("Prompt", key="area_prompt")

    if len(st.session_state.area_prompt) > 0:
        # Process
        if st.session_state.area_prompt != st.session_state.latest_area_prompt:
            try:
                st.session_state.area_response = query(st.session_state.area_prompt)
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
                st.session_state.area_initial_view_state = view.initial_view_state(
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