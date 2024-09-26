""" This module contains the playlists blueprint. """

import datetime
import requests
from config import ApiUrl
from api.misc import get_error
from flask import Blueprint, session, redirect, render_template



def get_playlists():
    """
    Retrieves playlists from the Spotify API.

    Returns:
        A JSON response containing the playlists.
    """

    if "access_token" not in session:
        return redirect("/login")

    if datetime.datetime.now().timestamp() > session["expires_at"]:
        return redirect("/refresh-token")

    headers = {
        "Authorization": "Bearer " + session["access_token"]
    }
    response = requests.get(
        ApiUrl + "/playlists?offset=0&limit=50", headers=headers)
    get_error(response)
    data = response.json()
    playlists = []

    for playlist in data["items"]:
        playlist_info = {
            "Playlist name": playlist["name"],
            "Owner": playlist["owner"]["display_name"],
            "Total tracks": playlist["tracks"]["total"],
            "Playlist link": playlist["external_urls"]["spotify"],
            "image": playlist["images"][0]["url"]
            if playlist["images"] else None
        }
        playlists.append(playlist_info)

    total_playlists = len(playlists)

    return total_playlists
