import json
import pandas as pd


def transform_details(con) -> list:
    with open("data/details.json") as json_data:
        d = json.load(json_data)
        league_entry_df = pd.json_normalize(d["league_entries"])
        league_df = pd.json_normalize(d["league"])
        standings_df = pd.json_normalize(d["standings"])

    con.sql("CREATE TABLE IF NOT EXISTS league_entry AS SELECT * FROM league_entry_df;")
    con.sql("CREATE TABLE IF NOT EXISTS league AS SELECT * FROM league_df;")
    con.sql("CREATE TABLE IF NOT EXISTS standings AS SELECT * FROM standings_df;")

    results = con.sql("SELECT DISTINCT entry_id FROM league_entry").df()
    print(results)
    results.to_csv("standings.csv")

    return results["entry_id"].to_list()
