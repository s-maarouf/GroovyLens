"""SpotiLytics app that returns data from spotify endpoint API"""

import os
import datetime
import requests
from uuid import uuid4
from urllib import parse
from flask import Flask, jsonify, request, render_template, redirect, session

app = Flask(__name__)
app.secret_key = str(uuid4())

ClientId = os.environ.get("ClientId")
ClientSecret = os.environ.get("ClientSecret")
RedirectUri = "https://smaarouf.tech/callback"
AuthUrl = "https://accounts.spotify.com/authorize"
TokenUrl = "https://accounts.spotify.com/api/token"
ApiUrl = "https://api.spotify.com/v1/me"


print(ClientId, ClientSecret)


@app.route("/")
def index():
    """
    This function returns a welcome message with a link to login with Spotify.

    Returns:
        str: The welcome message with the login link.
    """

    return render_template("index.html")


@app.route("/login")
def login():
    """
    Redirects the user to the Spotify authorization page for login.

    Returns:
        A redirect response to the Spotify authorization page.
    """

    scope = "user-read-private user-read-email \
            playlist-read-private user-top-read"
    params = {
        "client_id": ClientId,
        "response_type": "code",
        "scope": scope,
        "redirect_uri": RedirectUri,
        "show_dialog": True
    }

    auth_url = f"{AuthUrl}?{parse.urlencode(params)}"
    return redirect(auth_url)


@app.route("/callback")
def callback():
    """
    Callback function for handling the response from the authorization server.

    Returns:
        A redirect to the "/playlists" endpoint if the authorization code
            is present in the request arguments.
        Otherwise, returns a JSON response with an error message if
            the "error" parameter is present in the request arguments.
    """

    if "error" in request.args:
        return jsonify({"error": request.args["error"]})

    if "code" in request.args:
        body = {
            "code": request.args["code"],
            "grant_type": "authorization_code",
            "redirect_uri": RedirectUri,
            "client_id": ClientId,
            "client_secret": ClientSecret
        }

        response = requests.post(TokenUrl, data=body)
        token = response.json()
        session["access_token"] = token["access_token"]
        session["refresh_token"] = token["refresh_token"]
        session["expires_at"] = datetime.datetime.now().timestamp() + \
            token["expires_in"]

        return redirect("/profile")


@app.route("/profile")
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
    if response.status_code != 200:
        return redirect("/error")
    data = response.json()
    user_info = {
        "username": data["display_name"],
        "followers": data["followers"]["total"],
        "profile_pic": data["images"][1]["url"] if data["images"] else None
    }

    return render_template("profile.html", user=user_info)


@app.route("/playlists")
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
    if response.status_code != 200:
        return redirect("/error")
    data = response.json()
    playlists = []

    for playlist in data["items"]:
        playlist_info = {
            "Playlist name": playlist["name"],
            "Owner": playlist["owner"]["display_name"],
            "Total tracks": playlist["tracks"]["total"],
            "Playlist link": playlist["external_urls"]["spotify"],
            "image": playlist["images"][0]["url"] if playlist["images"] else None
        }
        playlists.append(playlist_info)

    total_playlists = len(playlists)

    return render_template("playlists.html",
                           playlists=playlists,
                           total_playlists=total_playlists)


@app.route("/top-artists")
def get_artists():
    if "access_token" not in session:
        return redirect("/login")

    if datetime.datetime.now().timestamp() > session["expires_at"]:
        return redirect("/refresh-token")
    headers = {
        "Authorization": "Bearer " + session["access_token"]
    }
    response = requests.get(
        ApiUrl + "/top/artists?time_range=medium_term&limit=10&offset=0",
        headers=headers)
    if response.status_code != 200:
        return redirect("/error")
    data = response.json()
    artists = []
    for item in data["items"]:
        artist_info = {
            "Name": item["name"],
            "Followers": item["followers"]["total"],
        }
        artists.append(artist_info)

    return jsonify(artists)


@app.route("/top-tracks")
def get_tracks():
    if "access_token" not in session:
        return redirect("/login")

    if datetime.datetime.now().timestamp() > session["expires_at"]:
        return redirect("/refresh-token")
    headers = {
        "Authorization": "Bearer " + session["access_token"]
    }
    response = requests.get(
        ApiUrl + "/top/tracks?time_range=long_term&limit=10&offset=0",
        headers=headers)
    if response.status_code != 200:
        return redirect("/error")
    data = response.json()
    tracks = []
    for item in data["items"]:
        track_info = {
            "Track name": item["name"],
            "Track link": item["external_urls"]["spotify"],
            "Track image": item["album"]["images"][1]["url"],
            "Album name": item["album"]["name"],
            "Artists": item["artists"],
            "Preview link": item["preview_url"]
        }

        tracks.append(track_info)

    return jsonify(tracks)


@app.route("/refresh-token")
def refresh_token():
    """
    Refreshes the access token if it has expired.

    Returns:
        A redirect to the "/playlists" endpoint if the access token
            has been successfully refreshed.
        Otherwise, returns a redirect to the "/login" endpoint.
    """

    if "refresh_token" not in session:
        return redirect("/login")

    if datetime.datetime.now().timestamp() > session["expires_at"]:
        body = {
            "grant_type": "refresh_token",
            "refresh_token": session["refresh_token"],
            "client_id": ClientId,
            "client_secret": ClientSecret
        }
        response = requests.post(TokenUrl, data=body)
        new_token = response.json()

        session["access_token"] = new_token["access_token"]
        session["expires_at"] = datetime.datetime.now().timestamp() + \
            new_token["expires_in"]
        return redirect("/")


@app.route("/logout")
def logout():
    """
    Logs out the user by clearing the session.

    Returns:
        A redirect to the "/login" endpoint.
    """
    session.clear()
    return redirect("/")


@app.route("/error")
def error():
    """
    Renders the error.html template.

    Returns:
        The rendered error.html template.
    """
    return render_template("error.html")


@app.errorhandler(404)
def not_found(error):
    """
    Renders the 404.html template and returns a 404 status code.

    Args:
        error: The error object or message.

    Returns:
        A tuple containing the rendered template and the 404 status code.
    """
    return render_template("notfound.html"), 404


if __name__ == "__main__":

    """ Main Function """
    app.run(host="0.0.0.0", port=10000, debug=True)
