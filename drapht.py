from api_requests import (
    get_json,
    get_league_data,
    get_static_data,
    get_GW_data,
    get_team_data,
)

import duckdb


def get_data(con, email_address, league_code):
    get_static_data(email_address=email_address)
    get_league_data(email_address=email_address, league_code=league_code)

    con.sql(
        "CREATE TABLE IF NOT EXISTS standings AS SELECT * FROM read_json_auto('data/details.json');"
    )
    # Get latest GW / team_list from above,

    results = con.sql("SELECT * FROM standings").df()
    print(results)
    results.to_csv("standings.csv")


def main():
    # cursor = duckdb.connect()
    con = duckdb.connect("drapht.db")

    email_address = "dazam92@gmail.com"
    league_code = "56578"
    get_data(con=con, email_address=email_address, league_code=league_code)
    print("Let's start")


if __name__ == "__main__":
    main()
