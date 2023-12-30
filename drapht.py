import duckdb
import os
import streamlit as st
import pandas as pd
import matplotlib


st.set_page_config(
    page_title="FPL Draft",
    page_icon="⚽",
    initial_sidebar_state="expanded",
    layout="wide",
)


@st.cache_data
def load_current_gw_teams():
    # Read current gw, use as gw[0]
    with open(r"data_gw", "r") as fp:
        gw = fp.readlines()
    # Read in team names
    with open(r"data_teams", "r") as fp:
        t = fp.readlines()
        teams = [i.strip() for i in t]

    return gw[0], teams


@st.cache_data
def load_bracket_dfs():
    bracket_1 = pd.read_csv("data/results_1.csv")
    bracket_1["points"] = bracket_1["points"].astype(int)
    bracket_2 = pd.read_csv("data/results_2.csv")
    bracket_2["points"] = bracket_2["points"].astype(int)
    bracket_3 = pd.read_csv("data/results_3.csv")
    bracket_3["points"] = bracket_3["points"].astype(int)
    bracket_4 = pd.read_csv("data/results_4.csv")
    bracket_4["points"] = bracket_4["points"].astype(int)

    return bracket_1, bracket_2, bracket_3, bracket_4


@st.cache_data
def standings():
    col_names = {
        "gw": "Gameweek",
        "pos": "Position",
        "name": "Name",
    }
    standings_ts = pd.read_csv("data/standings_ts.csv")
    standings_ts["pos"] = standings_ts["pos"] * -1
    standings_ts = standings_ts.rename(columns=col_names)
    standings_ts["Gameweek"] = standings_ts["Gameweek"].astype(int)

    cumm_points = pd.read_csv("data/cumm_points.csv")

    return standings_ts, cumm_points


def transactions():
    col_names = {
        "team": "Team Name",
        "waiver_or_free": "Waiver/Free Agent",
        "waiver_gw": "Transfer GW",
        "next_gw": "Next GW",
        "player_in": "IN",
        "player_in_pts": "IN Points",
        "player_out": "OUT",
        "player_out_pts": "OUT Points",
        "net_pts": "Net Points",
    }

    top_n = pd.read_csv("data/top_df.csv")
    # top_n = top_n.drop("Unnamed: 0", axis=1)

    bottom_n = pd.read_csv("data/bottom_df.csv")
    # bottom_n = bottom_n.drop("Unnamed: 0", axis=1)

    top_n = top_n.rename(columns=col_names)
    bottom_n = bottom_n.rename(columns=col_names)
    return top_n, bottom_n


# @st.cache_data()
def main():
    st.title("FPL Draft Standings")

    gw, teams = load_current_gw_teams()
    (bracket_1, bracket_2, bracket_3, bracket_4) = load_bracket_dfs()
    standings_ts, cumm_points = standings()
    top_n, bottom_n = transactions()

    # Space out the maps so the first one is 2x the size of the other three
    c1, c2, c3 = st.columns((1, 0.2, 2))

    c3.header("Transfers!")
    blunders, smart_moves, transactions_gw = c3.tabs(
        ["Top Blunders", "Top Transfers", "Transactions by GW"]
    )

    gwbracket = c1.radio(
        "Choose GW Bracket to look at points for that bracket",
        ["Bracket 1", "Bracket 2", "Bracket 3"],
        captions=["GW 1 - 10", "GW 11 - 20", "GW 21 - 29"],
        horizontal=True,
    )

    if gwbracket == "Bracket 1":
        c1.dataframe(
            bracket_1.style.background_gradient(cmap="YlGn"),
            hide_index=True,
            use_container_width=True,
        )
    elif gwbracket == "Bracket 2":
        c1.dataframe(
            bracket_2.style.background_gradient(cmap="YlGn"),
            hide_index=True,
            use_container_width=True,
        )
    elif gwbracket == "Bracket 3":
        c1.dataframe(
            bracket_3.style.background_gradient(cmap="YlGn"),
            hide_index=True,
            use_container_width=True,
        )
    elif gwbracket == "Bracket 4":
        c1.dataframe(
            bracket_4.style.background_gradient(cmap="YlGn"),
            hide_index=True,
            use_container_width=True,
        )
    c1.caption("** Ignore the minus sign lol, will fix it later")
    c1.line_chart(standings_ts, x="Gameweek", y="Position", color="Name")
    # c1.line_chart(cumm_points, x="gw", y="points", color="name")

    with blunders:
        st.subheader("Top 10 Blunders")
        st.dataframe(
            bottom_n.style.background_gradient(cmap="YlOrRd_r", subset=["Net Points"]),
            hide_index=True,
            use_container_width=True,
        )

    with smart_moves:
        st.subheader("Top 10 Smart Transfers")
        st.dataframe(
            top_n.style.background_gradient(cmap="YlGn", subset=["Net Points"]),
            hide_index=True,
            use_container_width=True,
        )

    with transactions_gw:
        st.subheader("Transactions by GW")

        option = st.selectbox("Blunders for which GW?", [i for i in range(1, 18)])
        col_names = {
            "team": "Team Name",
            "waiver_or_free": "Waiver/Free Agent",
            "waiver_gw": "Transfer GW",
            "next_gw": "Next GW",
            "player_in": "IN",
            "player_in_pts": "IN Points",
            "player_out": "OUT",
            "player_out_pts": "OUT Points",
            "net_pts": "Net Points",
        }
        blunders_df = pd.read_csv(f"data/blunders_{option}.csv")
        blunders_df_sorted = blunders_df.sort_values(by="net_pts", ascending=True)
        blunders_df_sorted = blunders_df_sorted.rename(columns=col_names)

        st.dataframe(
            blunders_df_sorted.style.background_gradient(
                cmap="coolwarm", subset=["Net Points"]
            ),
            hide_index=True,
            use_container_width=True,
        )


if __name__ == "__main__":
    main()
