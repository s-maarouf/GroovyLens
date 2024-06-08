""" This module contains the token blueprint. """

import datetime
import requests
from config import ClientId, ClientSecret, TokenUrl
from flask import Blueprint, session, redirect

token_blueprint = Blueprint('token', __name__)


@token_blueprint.route("/refresh-token")
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
