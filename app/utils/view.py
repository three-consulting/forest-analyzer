import streamlit as st
import pydeck as pdk

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