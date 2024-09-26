""" This module contains the profile blueprint."""

from flask import Blueprint, session, redirect, render_template
import datetime
import requests
from config import ApiUrl
from api.misc import get_error
from api.top_items import get_tracks, get_artists
from api.playlists import get_playlists

home_blueprint = Blueprint('home', __name__)


@home_blueprint.route("/home")
def home():
    """
    Renders the home.html template.

    Returns:
        The rendered home.html template.
    """
    user = get_profile()
    total_playlists = get_playlists()
    liked = get_liked()
    artists = get_artists()[1]
    tracks = get_tracks()[1]
    recommendations = get_recommendations()

    return render_template("newprofile.html", user=user, total_playlists=total_playlists, liked=liked, artists=artists, tracks=tracks, recommendations=recommendations)


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
    get_error(response)
    data = response.json()
    user_info = {
        "username": data["display_name"],
        "followers": data["followers"]["total"],
        "profile_pic": data["images"][1]["url"] if data["images"]
        else "../static/images/profile.png",
        "market": data["country"],
    }

    return user_info


def get_recommendations():
    """
    Retrieves the user's recommendations from the API.

    Returns:
        A rendered template with the user's recommendations.
    """
    if "access_token" not in session:
        return redirect("/login")

    if datetime.datetime.now().timestamp() > session["expires_at"]:
        return redirect("/refresh-token")
    headers = {
        "Authorization": "Bearer " + session["access_token"]
    }

    seeds = get_tracks()
    seed_artists = '%2C'.join(seeds[3][:2])
    seed_tracks = '%2C'.join(seeds[2][:2])
    user_market = get_profile()["market"]
    genres = get_artists()[2][0]
    response = requests.get(
        ApiUrl[:-2] +
        f"recommendations?limit=5&market={user_market}&seed_artists={seed_artists}&seed_genres={genres}&seed_tracks={seed_tracks}",
        headers=headers)
    get_error(response)
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


def get_liked():
    """
    Retrieves the user's liked songs from the API.

    Returns:
        A JSON response containing the user's liked songs.
    """
    if "access_token" not in session:
        return redirect("/login")

    if datetime.datetime.now().timestamp() > session["expires_at"]:
        return redirect("/refresh-token")
    headers = {
        "Authorization": "Bearer " + session["access_token"]
    }
    response = requests.get("https://api.spotify.com/v1/me/tracks?limit=50&offset=0",
                            headers=headers)
    get_error(response)
    data = response.json()

    return data["total"]
