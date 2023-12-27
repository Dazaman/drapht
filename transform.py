import os
import json
import pandas as pd
from typing import NamedTuple


def transform_details(con) -> NamedTuple("League", [("entries", list), ("gw", list)]):
    with open("data/details.json") as json_data:
        d = json.load(json_data)
        league_entry_df = pd.json_normalize(d["league_entries"])
        league_df = pd.json_normalize(d["league"])
        standings_df = pd.json_normalize(d["standings"])

    with open("data/event_status.json") as json_data:
        d = json.load(json_data)
        event_status_df = pd.json_normalize(d["status"])

    con.sql("CREATE TABLE IF NOT EXISTS league_entry AS SELECT * FROM league_entry_df;")
    con.sql("CREATE TABLE IF NOT EXISTS league AS SELECT * FROM league_df;")
    con.sql("CREATE TABLE IF NOT EXISTS standings AS SELECT * FROM standings_df;")
    con.sql("CREATE TABLE IF NOT EXISTS event_status AS SELECT * FROM event_status_df;")

    results = con.sql("SELECT DISTINCT entry_id FROM league_entry").df()
    gw = con.sql("SELECT DISTINCT event FROM event_status").df()

    return results["entry_id"].to_list(), gw["event"].to_list()


def team_points(con):
    for entry in os.listdir("./data"):
        print(entry)
        if entry.startswith("team_"):
            with open(os.path.join(f"data/{entry}", "history.json")) as json_data:
                data = json.load(json_data)
                history = pd.json_normalize(data["history"])
                history = history.drop(["rank", "rank_sort"], axis=1)
                history.to_csv(f"data/{entry}/history.csv", index=False)
                con.sql(
                    f"CREATE TABLE IF NOT EXISTS {entry} AS FROM read_csv('data/{entry}/history.csv', auto_detect = TRUE)"
                )

    # check = con.sql(f"SELECT * FROM team_249496")
    # print(check)


def concat_team_points(con):
    joined = con.sql(
        """
                     SELECT
                        entry as team_id,
                        event as gw,
                        points as points,
                        total_points as total_points,
                     FROM team_249496
                     UNION ALL
                     SELECT
                        entry as team_id,
                        event as gw,
                        points as points,
                        total_points as total_points,
                     FROM team_230738
                     UNION ALL
                     SELECT
                        entry as team_id,
                        event as gw,
                        points as points,
                        total_points as total_points,
                     FROM team_229056
                     UNION ALL
                     SELECT
                        entry as team_id,
                        event as gw,
                        points as points,
                        total_points as total_points,
                     FROM team_219160
                     UNION ALL
                     SELECT
                        entry as team_id,
                        event as gw,
                        points as points,
                        total_points as total_points,
                     FROM team_218961
                     UNION ALL
                     SELECT
                        entry as team_id,
                        event as gw,
                        points as points,
                        total_points as total_points,
                     FROM team_218851
                     """
    ).df()

    joined.to_csv("data/joined.csv", index=False)
