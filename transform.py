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

    with open(r"data_gw", "w") as fp:
        fp.writelines(gw["event"].astype(str).to_list())

    with open(r"data_teams", "w") as fp:
        # fp.writelines(results["entry_id"].astype(str).to_list())
        fp.write("\n".join(results["entry_id"].astype(str).to_list()))

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


def calculate_points_bracket(con, brackets, bracket) -> pd.DataFrame:
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
        b.entry_name AS team_name,
        CONCAT(b.player_first_name,' ', b.player_last_name) AS full_name,
        a.points AS points,
    FROM pts_table a
    LEFT JOIN league_entry b
    ON a.team_id = b.entry_id
    ORDER BY 3 desc      

    """
    # CONCAT('GW',{brackets[bracket][0]},' - ', 'GW',{brackets[bracket][1]}) as gw_bracket,
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
    players as (
        SELECT *
        FROM main.static
    ),
    merged as (
        SELECT 
            tr.*, 
            gwl_out.gw,
            gwl_out.total_points as out_pts,
            gwl_in.total_points as in_pts,
        FROM transactions_c tr
        LEFT JOIN gwl gwl_out 
        ON tr.event = gwl_out.prev_week
        AND tr.element_out = gwl_out.id
        LEFT JOIN gwl gwl_in 
        ON tr.event = gwl_in.prev_week
        AND tr.element_in = gwl_in.id
    ),
    details as (
        SELECT 
            m.*,
            b.entry_name AS team_name,
            pi.web_name element_in_name,
            po.web_name element_out_name,
            in_pts - out_pts as diff
        FROM merged m
        LEFT JOIN players pi
        ON m.element_in = pi.id
        LEFT JOIN players po
        ON m.element_out = po.id
        LEFT JOIN league_entry b
        ON m.entry = b.entry_id
    )
    SELECT 
        team_name as team,
        event as waiver_gw,
        element_in_name as player_in,
        element_out_name as player_out,
        kind as waiver_or_free,
        gw as next_gw,
        in_pts as player_in_pts,
        out_pts as player_out_pts,
        diff as net_pts,
    FROM details
    ORDER BY diff asc
    """
    blunders = con.sql(sql).df()
    blunders.to_csv(f"data/blunders_{gw}.csv", index=False)
    con.sql(
        f"CREATE TABLE IF NOT EXISTS blunders_{gw} AS FROM read_csv('data/blunders_{gw}.csv', auto_detect = TRUE);"
    )


def top_n_transfers(con):
    df_list = []

    for file in os.listdir("data/."):
        if file.startswith("blunders"):
            df = pd.read_csv(file)
            df_list.append(df)

    top_df = pd.concat(df_list)

    top_df.to_csv("data/top_df.csv")
    con.sql(
        f"CREATE TABLE IF NOT EXISTS top_n_transfers AS FROM read_csv('data/top_n_transfers.csv', auto_detect = TRUE);"
    )
