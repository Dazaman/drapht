import duckdb
import os
import streamlit as st
import pandas as pd
import matplotlib
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.colored_header import colored_header


st.set_page_config(
    page_title="FPL Draft",
    page_icon="⚽",
    initial_sidebar_state="collapsed",
    layout="wide",
)


# @st.cache_data
def load_current_gw_teams():
    # Read current gw, use as gw[0]
    with open(r"data_gw", "r") as fp:
        gw = fp.readlines()
    # Read in team names
    with open(r"data_teams", "r") as fp:
        t = fp.readlines()
        teams = [i.strip() for i in t]

    return gw[0], teams


# @st.cache_data
def load_bracket_dfs():
    bracket_1 = pd.read_csv("data/results_1.csv")
    bracket_1["points"] = bracket_1["points"].astype(int)
    bracket_1 = bracket_1.sort_values(by="points", ascending=False)

    bracket_2 = pd.read_csv("data/results_2.csv")
    bracket_2["points"] = bracket_2["points"].astype(int)
    bracket_2 = bracket_2.sort_values(by="points", ascending=False)

    bracket_3 = pd.read_csv("data/results_3.csv")
    bracket_3["points"] = bracket_3["points"].astype(int)
    bracket_3 = bracket_3.sort_values(by="points", ascending=False)

    bracket_4 = pd.read_csv("data/results_4.csv")
    bracket_4["points"] = bracket_4["points"].astype(int)
    bracket_4 = bracket_4.sort_values(by="points", ascending=False)

    return bracket_1, bracket_2, bracket_3, bracket_4


# @st.cache_data
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


def bench():
    bench_pts = pd.read_csv("data/bench_pts.csv")
    total_bench_pts = pd.read_csv("data/total_bench_pts.csv")

    return bench_pts, total_bench_pts


def transactions(col_names, int_cols):
    top_n = pd.read_csv("data/top_df.csv")
    bottom_n = pd.read_csv("data/bottom_df.csv")

    top_n = top_n.rename(columns=col_names)
    bottom_n = bottom_n.rename(columns=col_names)

    top_n[int_cols] = top_n[int_cols].astype(int)
    bottom_n[int_cols] = bottom_n[int_cols].astype(int)

    return top_n, bottom_n


# @st.cache_data()
def main():
    st.title("FPL Draft 23/24")
    colored_header(
        label="Analysing transfers, team selection and random stuff",
        description="I was very bored in the christmas break ..",
        color_name="violet-70",
    )
    # add_vertical_space(2)

    gw, teams = load_current_gw_teams()
    (bracket_1, bracket_2, bracket_3, bracket_4) = load_bracket_dfs()
    standings_ts, cumm_points = standings()
    bench_pts, total_bench_pts = bench()

    col_names = {
        "team": "Team Name",
        "waiver_or_free": "Type",
        "waiver_gw": "Transfer GW",
        "next_gw": "Next GW",
        "player_in": "IN",
        "player_in_pts": "IN Pts",
        "player_out": "OUT",
        "player_out_pts": "OUT Pts",
        "net_pts": "Net Points",
    }

    int_cols = ["Transfer GW", "Next GW", "IN Pts", "OUT Pts", "Net Points"]

    top_n, bottom_n = transactions(col_names, int_cols)

    col1, col2, col3 = st.sidebar.columns([2, 4, 2])

    with col1:
        st.write("")
    with col2:
        st.image("img/fpl.jpeg", use_column_width=True)
    with col3:
        st.write("")

    st.sidebar.markdown(" ## FPL Draft League")
    st.sidebar.markdown(
        "Some basic visualisations from our FPL Draft 23/24 season. Aim of it is to analyze why I am so bad at this..."
    )
    st.sidebar.info(
        "Feel free to fork this repo from [Github](https://github.com/Dazaman/drapht).",
        icon="ℹ️",
    )
    # Space out the maps so the first one is 2x the size of the other three
    c1, c2, c3 = st.columns((0.7, 0.05, 1.3))

    c3.header("Transfers!")
    c3.caption(
        "** Currently does not take into account whether Transferred in player was on the bench or not."
    )
    blunders, smart_moves, transactions_gw = c3.tabs(
        [
            "Top Blunders",
            "Top Transfers",
            "Transactions by GW",
        ]
    )

    c1.header("Standings by GW Bracket")
    gwbracket = c1.radio(
        "Choose GW Bracket. **\$50** Bracket Winner, **\$25** for Runner-up",
        ["Bracket 1", "Bracket 2", "Bracket 3", "Bracket 4"],
        captions=["GW 1 - 10", "GW 11 - 20", "GW 21 - 29", "GW 30 - 38"],
        horizontal=True,
        index=1,
    )

    if gwbracket == "Bracket 1":
        c1.dataframe(
            bracket_1.style.background_gradient(cmap="YlGn"),
            column_config={
                "img": st.column_config.ImageColumn(
                    "DP", help="Streamlit app preview screenshots"
                )
            },
            hide_index=True,
            use_container_width=True,
        )
    elif gwbracket == "Bracket 2":
        c1.dataframe(
            bracket_2.style.background_gradient(cmap="YlGn"),
            column_config={
                "img": st.column_config.ImageColumn(
                    "DP", help="Streamlit app preview screenshots"
                )
            },
            hide_index=True,
            use_container_width=True,
        )
    elif gwbracket == "Bracket 3":
        c1.dataframe(
            bracket_3.style.background_gradient(cmap="YlGn"),
            column_config={
                "img": st.column_config.ImageColumn(
                    "DP", help="Streamlit app preview screenshots"
                )
            },
            hide_index=True,
            use_container_width=True,
        )
    elif gwbracket == "Bracket 4":
        c1.dataframe(
            bracket_4.style.background_gradient(cmap="YlGn"),
            column_config={
                "img": st.column_config.ImageColumn(
                    "DP", help="Streamlit app preview screenshots"
                )
            },
            hide_index=True,
            use_container_width=True,
        )

    c1.header("Points lost on Bench")
    c1.caption(
        "* Current Method of Calculation is to compare MIN pts per position (GK, DEF, MID, FWD) of starting 11 vs MAX pts per position on bench."
    )
    c1.caption(
        "* Only cases where the bench points were higher than starting are displayed as 'lost' points"
    )
    c1.caption(
        "* It currently doesn't account for the case where for example two defs are substituted in"
    )

    total_bench_pts_, bench_pts_ = c1.tabs(
        [
            "Total Bench Points",
            "Bench Points by Position",
        ]
    )
    with total_bench_pts_:
        st.dataframe(
            total_bench_pts.style.background_gradient(
                cmap="YlOrRd_r", subset=["bench_pts"]
            ),
            hide_index=True,
            use_container_width=True,
        )
    with bench_pts_:
        st.dataframe(
            bench_pts.style.background_gradient(cmap="YlOrRd_r", subset=["pts_lost"]),
            hide_index=True,
            use_container_width=True,
        )

    with blunders:
        st.subheader("Top 10 Blunders - Should have held on!")
        st.dataframe(
            bottom_n.style.background_gradient(cmap="YlOrRd_r", subset=["Net Points"]),
            hide_index=True,
            use_container_width=True,
        )

    with smart_moves:
        st.subheader("Top 10 Smart Transfers - Timely pick!")
        st.dataframe(
            top_n.style.background_gradient(cmap="YlGn", subset=["Net Points"]),
            hide_index=True,
            use_container_width=True,
        )

    with transactions_gw:
        st.subheader("Ranked Transactions by GW")

        option = st.selectbox(
            "Blunders for which GW?", [i for i in range(1, int(gw) + 1)]
        )
        blunders_df = pd.read_csv(f"data/blunders_{option}.csv")
        blunders_df_sorted = blunders_df.sort_values(by="net_pts", ascending=True)
        blunders_df_sorted = blunders_df_sorted.rename(columns=col_names)

        blunders_df_sorted[int_cols] = blunders_df_sorted[int_cols].astype(int)
        st.dataframe(
            blunders_df_sorted.style.background_gradient(
                cmap="coolwarm", subset=["Net Points"]
            ),
            hide_index=True,
            use_container_width=True,
        )

    c3.header("Timeline")
    c3.caption("** Ignore minus sign, will fix later")
    c3.line_chart(standings_ts, x="Gameweek", y="Position", color="Name")


if __name__ == "__main__":
    main()


## @TODO https://arnaudmiribel.github.io/streamlit-extras/extras/dataframe_explorer/
## @TODO https://arnaudmiribel.github.io/streamlit-extras/extras/chart_annotations/
## @TODO https://arnaudmiribel.github.io/streamlit-extras/extras/colored_header/
