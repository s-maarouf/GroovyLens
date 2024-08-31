""" This module contains the authentication endpoints for the Flask app. """

import requests
import datetime
from flask import Blueprint, redirect, request, session, jsonify, render_template
from urllib import parse
from config import ClientId, ClientSecret, RedirectUri, AuthUrl, TokenUrl

auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route("/login")
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


@auth_blueprint.route("/callback")
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
        return render_template("error.html")
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


@auth_blueprint.route("/logout")
def logout():
    """
    Logs out the user by clearing the session.

    Returns:
        A redirect to the "/login" endpoint.
    """
    session.clear()
    return redirect("/")
