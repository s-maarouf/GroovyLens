""" Configuration file for the Spotify API. """

import os

ClientId = os.getenv("ClientId")
ClientSecret = os.getenv("ClientSecret")
RedirectUri = "http://smaarouf.tech/callback"
AuthUrl = "https://accounts.spotify.com/authorize"
TokenUrl = "https://accounts.spotify.com/api/token"
ApiUrl = "https://api.spotify.com/v1/me"
