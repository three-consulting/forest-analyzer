import streamlit as st

from tabs import *
from utils import common

##################################################################

    #################
    #               #
    #   Settings    #
    #               #
    #################

def init():
    common.init()

    tables.init()

    area.init()

    distance.init()

    tree.init()

    playground.init()


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

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Intro",
        "Tables",
        "Area",
        "Distance",
        "Tree species",
        "Playground"
    ])

    with tab1:
        intro.tab()

    with tab2:
        tables.tab(points_bar=points_bar)

    with tab3:
        area.tab(points_bar=points_bar)

    with tab4:
        distance.tab(points_bar=points_bar)
    
    with tab5:
        tree.tab(points_bar=points_bar)

    with tab6:
        playground.tab()

####################################################################

    #############
    #           #
    #   Main    #
    #           #
    #############

if __name__ == "__main__":
    init()
    app()