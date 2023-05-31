import json
import pandas as pd
import streamlit as st
import pydeck as pdk

from utils import index
from utils.query import sql

def init():
    st.session_state.latest_tree_prompt = ""
    
    st.session_state.tree_geojson_res = sql(
        query="""
            SELECT id, ST_AsGeoJSON(geometry)
            FROM stand_4326 WHERE maintreespecies = 2
            AND area IS NOT NULL
            ORDER BY area DESC LIMIT 1;
        """,
        db_name="db",
    )

    st.session_state.tree_geojson_gold_standard = json.dumps(json.loads(st.session_state.tree_geojson_res[1]["result"][0][1]))

    text = (
        "I have postgreSQL database with PostGis geospatial forest data.\n"
        "The PostGis plugin is available in the database.\n"
        "The forest polygons can be found from the geometry column.\n"
        "Get the geometry as geojson.\n"
        "Don't include NULL values.\n"
    )

    st.session_state.index_tab5 = index.init(
        docs=[],
        db_name="db",
        table_name="stand_4326",
        text=text,
    )


@st.cache_data
def query(prompt):
    return st.session_state.index_tab5.query(prompt)

def tab(points_bar):
    st.header("Main tree species:")

    tree_data = { "maintreespecies": [1, 2, 29], "nimi": ["Mänty", "Kuusi", "Lehtipuu"], "name": ["Pine", "Spruce", "Leafy tree"] }
    tree_df = pd.DataFrame(data=tree_data)

    st.markdown("Below is a table of the most common tree species found in database.")
    st.dataframe(tree_df)

    st.markdown("Your assignment is to discover the ID and polygon of the forest plot with the largest area, which predominantly consists of spruce.")

    # Get the id and forest polygon of forest with larges area that has main tree species 2. Don't include NULL values.
    st.text_input("Prompt", key="tree_prompt")

    if len(st.session_state.tree_prompt) > 0:
        # Process
        with st.spinner(text="Getting response..."):
            if st.session_state.tree_prompt != st.session_state.latest_tree_prompt:
                try:
                    st.session_state.tree_response = query(st.session_state.tree_prompt)
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