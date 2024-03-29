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
    load_gw_event,
    load_transactions,
    concat_team_points,
    calc_points_bracket,
    calc_running_standings,
    calc_cumm_points,
    calc_blunders,
    top_n_transfers,
    calc_bench_pts,
)
from typing import List
import duckdb
import os
import streamlit as st
import pandas as pd
import matplotlib
import argparse


def get_data(con, league_code):
    static_files = get_static_data()
    league_files = get_league_data(league_code=league_code)

    entries, gw = transform_details(con)
    gw = list(range(1, gw[0] + 1))
    print("entries", entries)
    print("max gw ", gw)

    for team in entries:
        get_team_data(team_id=team)
        for week in gw:
            get_gw_team_data(team_id=team, gw=week)

    for week in gw:
        get_gw_data(gw=week)


def transform_load_data(
    con,
):
    entries, gw = transform_details(con)
    gw = list(range(1, gw[0] + 1))

    load_team_points(con=con)
    concat_team_points(con=con)
    load_gw_live(con=con)
    load_transactions(con=con)
    load_gw_event(con=con, teams=entries)
    calc_bench_pts(con=con)

    for i in gw:
        calc_blunders(con=con, gw=i)


def parse_arguments(cli_args: list[str] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("--refresh", default=True, type=bool)
    parser.add_argument("--transform", default=True, type=bool)
    parser.add_argument("--load", default=True, type=bool)
    parser.add_argument("--league_code", default="56578", type=str)

    return parser.parse_args(args=cli_args)


def main(cli_args: List[str]):
    args = parse_arguments(cli_args=cli_args)
    league_code = args.league_code

    brackets = {
        "1": ("1", "10"),
        "2": ("11", "20"),
        "3": ("21", "29"),
        "4": ("30", "38"),
    }

    refresh = args.refresh
    transform = args.transform
    load = args.load

    if not os.path.exists(f"data"):
        os.makedirs(f"data")
        os.makedirs("data/GW")

    con = duckdb.connect("drapht.db")

    if refresh:
        get_data(con=con, league_code=league_code)
    if transform:
        transform_load_data(con=con)
    if load:
        for i in brackets.keys():
            calc_points_bracket(con=con, brackets=brackets, bracket=i)
        calc_running_standings(con=con)
        calc_cumm_points(con=con)
        top_n_transfers(con=con)


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
