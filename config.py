""" Configuration file for the Spotify API. """

import os

ClientId = os.getenv("ClientId")
ClientSecret = os.getenv("ClientSecret")
RedirectUri = "https://127.0.0.1/callback"
AuthUrl = "https://accounts.spotify.com/authorize"
TokenUrl = "https://accounts.spotify.com/api/token"
ApiUrl = "https://api.spotify.com/v1/me"
