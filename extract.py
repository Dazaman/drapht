import getpass
import requests
import json
import pandas as pd
import re
import os


def get_json(json_files, apis) -> None:
    """
    Pulls fpl draft league data using an api call, and stores the output
    in a json file at the specified location.

    This code has been modified from https://github.com/leej11/fpl_draft_league/blob/master/fpl_draft_league/utils.py

    :json_files: The file path and name of the json file you wish to create
    :apis: The api url/endpoints to call for the files
    :param : Your email address to authenticate with premierleague.com
    :returns:
    """

    # Post credentials for authentication
    # pwd = getpass.getpass("Enter Password: ")
    session = requests.session()

    ### Login api doesnt work anymore due to captchas
    # session.proxies = {
    #     "http": "http://10.10.10.10:8000",
    #     "https": "http://10.10.10.10:8000",
    # }

    # url = "https://users.premierleague.com/accounts/login/"
    # # payload = {
    # #     "password": pwd,
    # #     "login": ,
    # #     "app": "plfpl-web",
    # # }
    # status = session.get(url)

    # print("Status", status.status_code)

    # Loop over the api(s), call them and capture the response(s)
    for file, i in zip(json_files, apis):
        print(file, i)
        r = session.get(i)

        jsonResponse = r.json()
        with open(file, "w") as outfile:
            json.dump(jsonResponse, outfile)


def get_static_data() -> list:
    apis = [
        "https://draft.premierleague.com/api/bootstrap-dynamic",
        "https://draft.premierleague.com/api/game",
        "https://draft.premierleague.com/api/bootstrap-static",
        "https://draft.premierleague.com/api/pl/event-status",
    ]
    json_files = [
        "data/bootstrap-dynamic.json",
        "data/game.json",
        "data/bootstrap-static.json",
        "data/event_status.json",
    ]

    get_json(json_files=json_files, apis=apis)

    return json_files


def get_league_data(league_code) -> list:
    apis = [
        f"https://draft.premierleague.com/api/league/{league_code}/details",
        f"https://draft.premierleague.com/api/league/{league_code}/element-status",
        f"https://draft.premierleague.com/api/draft/league/{league_code}/transactions",
        f"https://draft.premierleague.com/api/draft/{league_code}/choices",
    ]
    json_files = [
        "data/details.json",
        "data/element-status.json",
        "data/transactions.json",
        "data/choices.json",
    ]

    get_json(json_files=json_files, apis=apis)

    return json_files


def get_team_data(team_id):
    apis = [
        f"https://draft.premierleague.com/api/entry/{team_id}/public",
        f"https://draft.premierleague.com/api/entry/{team_id}/history",
        f"https://draft.premierleague.com/api/entry/{team_id}/my-team",
        # f"https://draft.premierleague.com/api/entry/{team_id}/transactions",
        f"https://draft.premierleague.com/api/watchlist/{team_id}",
    ]
    if os.path.exists(f"data/team_{team_id}"):
        print("The file exists.")
    else:
        os.makedirs(f"data/team_{team_id}")
    json_files = [
        f"data/team_{team_id}/public.json",
        f"data/team_{team_id}/history.json",
        f"data/team_{team_id}/my_team.json",
        # f"data/team_{team_id}/transactions.json",
        f"data/team_{team_id}/watchlist.json",
    ]

    get_json(json_files=json_files, apis=apis)


def get_gw_data(gw):
    apis = [
        f"https://draft.premierleague.com/api/event/{gw}/live",
    ]
    json_files = [
        f"data/gw/{gw}_live.json",
    ]

    get_json(json_files=json_files, apis=apis)


def get_gw_team_data(team_id, gw):
    apis = [
        f"https://draft.premierleague.com/api/entry/{team_id}/event/{gw}",
    ]
    json_files = [
        f"data/team_{team_id}/{gw}_event.json",
    ]

    get_json(json_files=json_files, apis=apis)
