import getpass
import requests
import json
import pandas as pd
import re
import os


def get_json(json_files, apis, email_address) -> None:
    """
    Pulls fpl draft league data using an api call, and stores the output
    in a json file at the specified location.

    This code has been modified from https://github.com/leej11/fpl_draft_league/blob/master/fpl_draft_league/utils.py

    :json_files: The file path and name of the json file you wish to create
    :apis: The api url/endpoints to call for the files
    :param email_address: Your email address to authenticate with premierleague.com
    :returns:
    """

    # Post credentials for authentication
    pwd = getpass.getpass("Enter Password: ")
    session = requests.session()
    url = "https://users.premierleague.com/accounts/login/"
    payload = {
        "password": pwd,
        "login": email_address,
        "app": "plfpl-web",
    }
    session.post(url, data=payload)

    # Loop over the api(s), call them and capture the response(s)
    for file, i in zip(json_files, apis):
        print(file, i)
        r = session.get(i)

        jsonResponse = r.json()
        with open(file, "w") as outfile:
            json.dump(jsonResponse, outfile)


def get_static_data(email_address) -> list:
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

    get_json(json_files=json_files, apis=apis, email_address=email_address)

    return json_files


def get_league_data(email_address, league_code) -> list:
    apis = [
        f"https://draft.premierleague.com/api/league/{league_code}/details",
        f"https://draft.premierleague.com/api/league/{league_code}/element-status",
        f"https://draft.premierleague.com/api/draft/league/{league_code}/trades",
        f"https://draft.premierleague.com/api/draft/{league_code}/choices",
    ]
    json_files = [
        "data/details.json",
        "data/element-status.json",
        "data/trades.json",
        "data/choices.json",
    ]

    get_json(json_files=json_files, apis=apis, email_address=email_address)

    return json_files


def get_team_data(email_address, team_id):
    apis = [
        f"https://draft.premierleague.com/api/entry/{team_id}/public",
        f"https://draft.premierleague.com/api/entry/{team_id}/my-team",
        f"https://draft.premierleague.com/api/watchlist/{team_id}",
    ]
    os.makedirs(f"data/{team_id}")
    json_files = [
        f"data/{team_id}/public.json",
        f"data/{team_id}/element-status.json",
        f"data/{team_id}/trades.json",
    ]

    get_json(json_files=json_files, apis=apis, email_address=email_address)


def get_GW_data(email_address, GW):
    apis = [
        f"https://draft.premierleague.com/api/event/{GW}/live",
        # f"https://draft.premierleague.com/api/entry/{team_id}/event/{GW}",
    ]
    json_files = [
        f"data/{GW}_live.json",
        # f"data/{GW}_event.json",
    ]

    get_json(json_files=json_files, apis=apis, email_address=email_address)
