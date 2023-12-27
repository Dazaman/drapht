from extract import (
    get_json,
    get_league_data,
    get_static_data,
    get_GW_data,
    get_team_data,
    get_GW_team_data,
)
from transform import (
    transform_details,
    team_points,
    concat_team_points,
    calculate_points_bracket,
)
import duckdb, os


def get_data(con, email_address, league_code):
    static_files = get_static_data(email_address=email_address)
    league_files = get_league_data(email_address=email_address, league_code=league_code)

    entries, gw = transform_details(con)
    gw = list(range(1, gw[0]))
    print("entries", entries)
    print("max gw ", gw)

    for team in entries:
        get_team_data(email_address=email_address, team_id=team)
        # for week in gw:
        #     get_GW_team_data(email_address=email_address, team_id=team, gw=week)

    for week in gw:
        get_GW_data(email_address=email_address, gw=week)


def main():
    con = duckdb.connect("drapht.db")

    email_address = "dazam92@gmail.com"
    league_code = "56578"
    refresh = False

    if os.path.exists(f"data"):
        print("The data folder exists.")
    else:
        os.makedirs(f"data")
        os.makedirs("data/GW")

    if refresh:
        get_data(con=con, email_address=email_address, league_code=league_code)
        team_points(con=con)
        concat_team_points(con=con)

    for bracket in range(1, 5):
        calculate_points_bracket(con=con, bracket=str(bracket))


if __name__ == "__main__":
    main()
