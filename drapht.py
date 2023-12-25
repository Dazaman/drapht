from api_requests import (
    get_json,
    get_league_data,
    get_static_data,
    get_GW_data,
    get_team_data,
)
from transform import transform_details
import duckdb


def get_data(con, email_address, league_code):
    static_files = get_static_data(email_address=email_address)
    # league_files = get_league_data(email_address=email_address, league_code=league_code)

    entries, gw = transform_details(con)
    print("entries", entries)
    print("max gw ", max(gw))

    for team in entries:
        get_team_data(email_address=email_address, team_id=team)
        break

    for week in gw:
        get_GW_data(email_address=email_address, gw=week)
        break


# @click.command()


def main():
    # cursor = duckdb.connect()
    con = duckdb.connect("drapht.db")

    email_address = "dazam92@gmail.com"
    league_code = "56578"
    get_data(con=con, email_address=email_address, league_code=league_code)
    print("Let's start")


if __name__ == "__main__":
    main()
