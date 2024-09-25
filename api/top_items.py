""" This module contains the endpoints for retrieving
the user's top artists and tracks from Spotify API. """

import datetime
import requests
from config import ApiUrl
from api.misc import get_error
from flask import Blueprint, session, redirect, jsonify, render_template

top_items_blueprint = Blueprint('top_items', __name__)


@top_items_blueprint.route("/top-items")
def top_items():
    """
    Retrieves the user's top artists and tracks from Spotify API.

    Returns:
        A rendered template with the user's top artists and tracks.
    """
    artists = get_artists()
    tracks = get_tracks()

    return render_template("top_artists.html", artists=artists, tracks=tracks)


def get_artists():
    """
    Retrieves the top artists based on the user's access token.

    Returns:
        A JSON response containing a list of dictionaries,
        where each dictionary represents an artist.
        Each artist dictionary contains the following information:
            - Name: The name of the artist.
            - Followers: The total number of followers the artist has.
    """
    if "access_token" not in session:
        return redirect("/login")

    if datetime.datetime.now().timestamp() > session["expires_at"]:
        return redirect("/refresh-token")
    headers = {
        "Authorization": "Bearer " + session["access_token"]
    }
    response = requests.get(
        ApiUrl + "/top/artists?time_range=long_term&limit=50",
        headers=headers)
    get_error(response)
    data = response.json()
    artists = []
    for item in data["items"]:
        artist_info = {
            "Artist name": item["name"],
            "Artist link": item["external_urls"]["spotify"],
            "Artist image": item["images"][1]["url"]
            if len(item["images"]) > 1 else item["images"][0]["url"],
            "Genres": item["genres"]
        }

        artists.append(artist_info)

    return artists


def get_tracks():
    """
    Retrieves the top tracks from Spotify API.

    Returns:
        A JSON response containing information about the top tracks.
    """
    if "access_token" not in session:
        return redirect("/login")

    if datetime.datetime.now().timestamp() > session["expires_at"]:
        return redirect("/refresh-token")
    headers = {
        "Authorization": "Bearer " + session["access_token"]
    }
    response = requests.get(
        ApiUrl + "/top/tracks?time_range=long_term&limit=50",
        headers=headers)
    get_error(response)
    data = response.json()
    tracks = []
    tracks_id = []
    artists_id = []
    for item in data["items"]:
        track_info = {
            "Track name": item["name"],
            "Track link": item["external_urls"]["spotify"],
            "Track image": item["album"]["images"][1]["url"]
            if len(item["album"]["images"]) > 1
            else item["album"]["images"][0]["url"],
            "Album name": item["album"]["name"],
            "Artists": item["artists"],
            "Explicit": "E" if item["explicit"] else None,
        }
        track_ids = item["id"]
        artist_ids = item["artists"][0]["id"]

        tracks.append(track_info)
        tracks_id.append(track_ids)
        artists_id.append(artist_ids)

    return tracks
