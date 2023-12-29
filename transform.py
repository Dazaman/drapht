import os
import json
import pandas as pd
from typing import NamedTuple


def transform_details(con) -> NamedTuple("League", [("entries", list), ("gw", list)]):
    """Reads in details and event status json files and creates tables in the database
    The output is used to loop over teams and GWs to ingest further data.

    Args:
        con (_type_): duck db connection

    Returns:
        entries: the list of team ids
        gw: the number of game weeks currently available
    """
    with open("data/details.json") as json_data:
        d = json.load(json_data)
        league_entry_df = pd.json_normalize(d["league_entries"])
        league_df = pd.json_normalize(d["league"])
        standings_df = pd.json_normalize(d["standings"])
        con.sql(
            "CREATE TABLE IF NOT EXISTS league_entry AS SELECT * FROM league_entry_df;"
        )
        con.sql("CREATE TABLE IF NOT EXISTS league AS SELECT * FROM league_df;")
        con.sql("CREATE TABLE IF NOT EXISTS standings AS SELECT * FROM standings_df;")

    with open("data/event_status.json") as json_data:
        d = json.load(json_data)
        event_status_df = pd.json_normalize(d["status"])
        con.sql(
            "CREATE TABLE IF NOT EXISTS event_status AS SELECT * FROM event_status_df;"
        )

    with open("data/bootstrap-static.json") as json_data:
        d = json.load(json_data)
        static_df = pd.json_normalize(d["elements"])
        con.sql("CREATE TABLE IF NOT EXISTS static AS SELECT * FROM static_df;")

    results = con.sql("SELECT DISTINCT entry_id FROM league_entry").df()
    gw = con.sql("SELECT DISTINCT event FROM event_status").df()

    return results["entry_id"].to_list(), gw["event"].to_list()


def load_team_points(con):
    for entry in os.listdir("./data"):
        if entry.startswith("team_"):
            with open(os.path.join(f"data/{entry}", "history.json")) as json_data:
                data = json.load(json_data)
                history = pd.json_normalize(data["history"])
                history = history.drop(["rank", "rank_sort"], axis=1)
                history.to_csv(f"data/{entry}/history.csv", index=False)
                con.sql(
                    f"CREATE TABLE IF NOT EXISTS {entry} AS FROM read_csv('data/{entry}/history.csv', auto_detect = TRUE)"
                )


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
    con.sql(
        f"CREATE TABLE IF NOT EXISTS total_points AS FROM read_csv('data/joined.csv', auto_detect = TRUE);"
    )


def calculate_points_bracket(con, bracket) -> pd.DataFrame:
    brackets = {
        "1": ("1", "10"),
        "2": ("11", "20"),
        "3": ("21", "29"),
        "4": ("30", "38"),
    }

    sql = f"""
    WITH 
    gw AS (
        SELECT 
            *,
        FROM total_points
        WHERE gw >= {brackets[bracket][0]} AND gw <= {brackets[bracket][1]} 
    ),
    pts_table AS (
        SELECT 
            team_id,
            SUM(points) as points
        FROM gw
        GROUP BY 1
    )
    SELECT 
        CONCAT('GW',{brackets[bracket][0]},' - ', 'GW',{brackets[bracket][1]}) as gw_bracket,
        b.entry_name AS team_name,
        CONCAT(b.player_first_name,' ', b.player_last_name) AS full_name,
        a.points AS points,
    FROM pts_table a
    LEFT JOIN league_entry b
    ON a.team_id = b.entry_id
    ORDER BY 4 desc      

    """
    results = con.sql(sql).df()
    results.to_csv(f"data/results_{bracket}.csv", index=False)

    # return results


def load_gw_live(con):
    df_list = []

    for file in os.listdir("data/gw/."):
        if file.endswith(".json"):
            with open(f"data/gw/{file}") as json_data:
                d = json.load(json_data)
                rows = []
                for value in d["elements"]:
                    row_dict = d["elements"][str(value)]["stats"]
                    row_dict["id"] = value
                    row_dict["gw"] = file.split(".")[0].split("_")[0]
                    rows.append(row_dict)
                df = pd.DataFrame(rows)
                # df = df.set_index("id")

                df_list.append(df)

    gw_live = pd.concat(df_list)
    gw_live.to_csv("data/gw_live.csv")
    con.sql(
        f"CREATE TABLE IF NOT EXISTS gw_live AS FROM read_csv('data/gw_live.csv', auto_detect = TRUE);"
    )


def load_transactions(con):
    with open("data/transactions.json") as json_data:
        d = json.load(json_data)
        transactions_df = pd.json_normalize(d["transactions"])

    con.sql("CREATE TABLE IF NOT EXISTS transactions AS SELECT * FROM transactions_df;")


def calc_running_standings(con):
    sql = """
    WITH 
    points as (
        SELECT team_id, gw, points, total_points
        FROM drapht.main.total_points
    )
    SELECT 
        CONCAT(b.player_first_name,' ', b.player_last_name) AS name, 
        a.gw,
        RANK() OVER (PARTITION BY a.gw order by a.total_points DESC) as pos
    FROM points a
    LEFT JOIN league_entry b
    ON a.team_id = b.entry_id 
    ORDER BY gw
    """

    standings_ts = con.sql(sql).df()
    standings_ts.to_csv("data/standings_ts.csv", index=False)
    con.sql(
        f"CREATE TABLE IF NOT EXISTS standings_ts AS FROM read_csv('data/standings_ts.csv', auto_detect = TRUE);"
    )


def calc_cumm_points(con):
    sql = """
    WITH 
    points as (
        SELECT team_id, gw, points, total_points
        FROM drapht.main.total_points
    )
    SELECT 
        CONCAT(b.player_first_name,' ', b.player_last_name) AS name,
        a.gw AS gw,
        a.total_points AS points,
    FROM points a
    LEFT JOIN league_entry b
    ON a.team_id = b.entry_id
    ORDER BY gw, total_points desc
    """

    cumm_points = con.sql(sql).df()
    cumm_points.to_csv("data/cumm_points.csv", index=False)
    con.sql(
        f"CREATE TABLE IF NOT EXISTS cumm_points AS FROM read_csv('data/cumm_points.csv', auto_detect = TRUE);"
    )


def calculate_blunders(con, gw):
    sql = f"""
    WITH transactions_c AS (
        SELECT * 
        FROM main.transactions tr
        WHERE result = 'a'
        AND event = {gw}
    ),
    gwl as (
        SELECT 
            *,
            gw - 1 AS prev_week
        FROM main.gw_live
    ),
    merged as (
        SELECT 
            tr.*, 
            gwl.gw, 
            gwl.id,
            gwl.total_points,
        FROM transactions_c tr
        LEFT JOIN gwl 
        ON tr.event = gwl.prev_week
        AND tr.element_out = gwl.id
    )
    SELECT * FROM merged
    """
    blunders = con.sql(sql).df()
    blunders.to_csv(f"data/blunders_{gw}.csv", index=False)
    con.sql(
        f"CREATE TABLE IF NOT EXISTS blunders_{gw} AS FROM read_csv('data/blunders_{gw}.csv', auto_detect = TRUE);"
    )
