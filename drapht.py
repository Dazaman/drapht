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
    team_points,
    concat_team_points,
    calculate_points_bracket,
    gw_live,
)
import duckdb
import os
import streamlit as st


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
    team_points(con=con)
    concat_team_points(con=con)
    gw_live(con=con)


def main():
    con = duckdb.connect("drapht.db")

    email_address = "dazam92@gmail.com"
    league_code = "56578"

    refresh = True
    transform = True

    if os.path.exists(f"data"):
        print("The data folder exists.")
    else:
        os.makedirs(f"data")
        os.makedirs("data/GW")

    if refresh:
        get_data(con=con, email_address=email_address, league_code=league_code)
    if transform:
        transform_load_data(con=con)

    st.set_page_config(layout="wide")
    st.title("FPL Draft Standings")

    df1 = calculate_points_bracket(con=con, bracket="1")
    st.write("Bracket 1")
    st.table(data=df1)

    df2 = calculate_points_bracket(con=con, bracket="2")
    st.write("Bracket 2")
    st.table(data=df2)


if __name__ == "__main__":
    main()
