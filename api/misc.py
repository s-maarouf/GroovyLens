""" This module contains the misc blueprint. """

from flask import Blueprint, render_template

misc_blueprint = Blueprint('misc', __name__)


@misc_blueprint.route("/error")
def error():
    """
    Renders the error.html template.

    Returns:
        The rendered error.html template.
    """
    return render_template("error.html")


@misc_blueprint.route("/forbidden")
def forbidden():
    """
    Renders the forbidden.html template.

    Returns:
        The rendered forbidden.html template.
    """
    return render_template("forbidden.html")
