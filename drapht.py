from extract import (
    get_json,
    get_league_data,
    get_static_data,
    get_gw_data,
    get_team_data,
    get_gw_team_data,
)
from transform import (
    transform_details,
    load_team_points,
    load_gw_live,
    load_transactions,
    concat_team_points,
    calculate_points_bracket,
)
import duckdb
import os
import streamlit as st
import pandas as pd


def get_data(con, email_address, league_code):
    static_files = get_static_data(email_address=email_address)
    league_files = get_league_data(email_address=email_address, league_code=league_code)

    entries, gw = transform_details(con)
    gw = list(range(1, gw[0]))
    print("entries", entries)
    print("max gw ", gw)

    for team in entries:
        get_team_data(email_address=email_address, team_id=team)
        for week in gw:
            get_gw_team_data(email_address=email_address, team_id=team, gw=week)

    for week in gw:
        get_gw_data(email_address=email_address, gw=week)


def transform_load_data(
    con,
):
    load_team_points(con=con)
    concat_team_points(con=con)
    load_gw_live(con=con)
    load_transactions(con=con)


def main():
    con = duckdb.connect("drapht.db")

    email_address = "dazam92@gmail.com"
    league_code = "56578"

    refresh = False
    transform = False
    load = False

    if not os.path.exists(f"data"):
        os.makedirs(f"data")
        os.makedirs("data/GW")

    if refresh:
        get_data(con=con, email_address=email_address, league_code=league_code)
    if transform:
        transform_load_data(con=con)
    if load:
        calculate_points_bracket(con=con, bracket="1")
        calculate_points_bracket(con=con, bracket="2")
        calculate_points_bracket(con=con, bracket="3")
        calculate_points_bracket(con=con, bracket="4")

    st.set_page_config(layout="wide")
    st.title("FPL Draft Standings")

    gwbracket = st.radio(
        "Choose GW Bracket to look at points for that bracket",
        ["Bracket 1", "Bracket 2", "Bracket 3"],
        captions=["GW 1 - 10", "GW 11 - 20", "GW 21 - 29"],
        horizontal=True,
    )

    if gwbracket == "Bracket 1":
        df = pd.read_csv("data/results_1.csv")
        st.dataframe(df)
    elif gwbracket == "Bracket 2":
        df = pd.read_csv("data/results_2.csv")
        st.dataframe(df)
    elif gwbracket == "Bracket 3":
        df = pd.read_csv("data/results_3.csv")
        st.dataframe(df)


if __name__ == "__main__":
    main()
