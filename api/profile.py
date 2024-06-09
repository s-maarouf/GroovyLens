""" This module contains the profile blueprint."""

from flask import Blueprint, session, redirect, render_template
import datetime
import requests
from config import ApiUrl

profile_blueprint = Blueprint('profile', __name__)


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
        "profile_pic": data["images"][1]["url"] if data["images"] else "../static/images/profile.png"
    }

    return render_template("profile.html", user=user_info)
