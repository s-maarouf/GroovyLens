""" This module contains the profile blueprint."""

from flask import Blueprint, session, redirect, render_template
import datetime
import requests
from config import ApiUrl
from api.top_items import get_tracks, get_artists

profile_blueprint = Blueprint('profile', __name__)
reccomendations_blueprint = Blueprint('reccomendations', __name__)


@profile_blueprint.route("/profile")
def get_profile():
    """
    Retrieves the current user's profile from the API.

    Returns:
        A JSON response containing the user profile.
    """
    if "access_token" not in session:
        return redirect("/login")

    if datetime.datetime.now().timestamp() > session["expires_at"]:
        return redirect("/refresh-token")
    headers = {
        "Authorization": "Bearer " + session["access_token"]
    }
    response = requests.get(ApiUrl, headers=headers)
    if response.status_code == 403:
        return redirect("/forbidden")
    if response.status_code != 200:
        return redirect("/error")
    data = response.json()
    user_info = {
        "username": data["display_name"],
        "followers": data["followers"]["total"],
        "profile_pic": data["images"][1]["url"] if data["images"]
        else "../static/images/profile.png",
        "market": data["country"],
    }

    return render_template("profile.html", user=user_info), user_info["market"]


@reccomendations_blueprint.route("/recommendations")
def get_recommendations():
    """
    Retrieves the user's recommendations from the API.

    Returns:
        A JSON response containing the user's recommendations.
    """
    if "access_token" not in session:
        return redirect("/login")

    if datetime.datetime.now().timestamp() > session["expires_at"]:
        return redirect("/refresh-token")
    headers = {
        "Authorization": "Bearer " + session["access_token"]
    }

    r, tracks_id, artists_id = get_tracks()
    r, user_market = get_profile()
    r, genres = get_artists()
    response = requests.get(
        ApiUrl[:-2] +
        f"recommendations?limit=10&market={user_market}&seed_artists={'%2c'.join(artists_id[:2])}&seed_genres={genres[0]}&seed_tracks={'%2c'.join(tracks_id[:2])}",
        headers=headers)
    print(response.url)
    if response.status_code != 200:
        return redirect("/error")
    data = response.json()
    recommendations = []
    for item in data["tracks"]:
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
        recommendations.append(track_info)

    return recommendations
