import duckdb
import os
import streamlit as st
import pandas as pd
import matplotlib


# @st.cache()
def main():
    # Read current gw, use as gw[0]
    with open(r"data_gw", "r") as fp:
        gw = fp.readlines()
    # Read in team names
    with open(r"data_teams", "r") as fp:
        t = fp.readlines()
        teams = [i.strip() for i in t]

    st.set_page_config(layout="wide")
    st.title("FPL Draft Standings")

    # Space out the maps so the first one is 2x the size of the other three
    c1, c2, c3 = st.columns((0.5, 1, 1))

    gwbracket = c1.radio(
        "Choose GW Bracket to look at points for that bracket",
        ["Bracket 1", "Bracket 2", "Bracket 3"],
        captions=["GW 1 - 10", "GW 11 - 20", "GW 21 - 29"],
        horizontal=True,
    )

    if gwbracket == "Bracket 1":
        gw_pts_df = pd.read_csv("data/results_1.csv")
        c1.dataframe(gw_pts_df.style.background_gradient(cmap="YlGn"), hide_index=True)
    elif gwbracket == "Bracket 2":
        gw_pts_df = pd.read_csv("data/results_2.csv")
        c1.dataframe(gw_pts_df.style.background_gradient(cmap="YlGn"), hide_index=True)
    elif gwbracket == "Bracket 3":
        gw_pts_df = pd.read_csv("data/results_3.csv")
        c1.dataframe(gw_pts_df.style.background_gradient(cmap="YlGn"), hide_index=True)
    elif gwbracket == "Bracket 4":
        gw_pts_df = pd.read_csv("data/results_4.csv")
        c1.dataframe(gw_pts_df.style.background_gradient(cmap="YlGn"), hide_index=True)

    standings_ts = pd.read_csv("data/standings_ts.csv")
    standings_ts["pos"] = standings_ts["pos"] * -1
    c2.line_chart(standings_ts, x="gw", y="pos", color="name")

    cumm_points = pd.read_csv("data/cumm_points.csv")
    c2.line_chart(cumm_points, x="gw", y="points", color="name")

    option = c3.selectbox("Blunders for which GW?", [i for i in range(1, 18)])
    blunders_df = pd.read_csv(f"data/blunders_{option}.csv")
    blunders_df_sorted = blunders_df.sort_values(by="net_pts", ascending=True)
    c3.dataframe(
        blunders_df_sorted.style.background_gradient(
            cmap="coolwarm", subset=["net_pts"]
        ),
        hide_index=True,
    )


if __name__ == "__main__":
    main()
