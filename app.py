"""
    SpotiLytics API

    This module contains the main Flask application that
    serves as the API for the SpotiLytics web application.
"""


from uuid import uuid4
from flask import Flask, render_template

from api.auth import auth_blueprint
from api.profile import profile_blueprint
from api.playlists import playlists_blueprint
from api.top_items import top_items_blueprint
from api.token import token_blueprint
from api.misc import misc_blueprint
from api.profile import reccomendations_blueprint

app = Flask(__name__)
app.secret_key = str(uuid4())

app.register_blueprint(auth_blueprint)
app.register_blueprint(profile_blueprint)
app.register_blueprint(reccomendations_blueprint)
app.register_blueprint(playlists_blueprint)
app.register_blueprint(top_items_blueprint)
app.register_blueprint(token_blueprint)
app.register_blueprint(misc_blueprint)


@app.route("/")
def index():
    """
    Renders the index.html template.

    Returns:
        The rendered index.html template.
    """
    return render_template("index.html")


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
    app.run(host="0.0.0.0", port=10000, debug=True)
