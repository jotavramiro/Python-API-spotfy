
import os
import spotipy

from flask import Flask, render_template, redirect, session, url_for
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, render_template, redirect, session, url_for, request
from datetime import datetime


load_dotenv()

# Cria a aplicação Flask
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Lê as credenciais do Spotify
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
SCOPE = "user-top-read user-read-recently-played"

def criar_spotify_oauth():
    return SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE
    )

def obter_spotify():
    token_info = session.get("token_info")

    if not token_info:
        return None

    return spotipy.Spotify(auth=token_info["access_token"])

@app.route("/login")
def login():
    print("A rota LOGIN foi acessada!")
    sp_oauth = criar_spotify_oauth()

    auth_url = sp_oauth.get_authorize_url()

    

    return redirect(auth_url)

@app.route("/callback")
def callback():
    sp_oauth = criar_spotify_oauth()

    code = request.args.get("code")

    token_info = sp_oauth.get_access_token(code)

    session["token_info"] = token_info


    return redirect(url_for("inicio"))

print("Credenciais do Spotify carregadas!")

@app.route("/logout")
def logout():
    session.clear()

    return redirect(url_for("inicio"))


@app.route("/")
def inicio():
    sp = obter_spotify()

    if not sp:
        return render_template("index.html")

    perfil = sp.current_user()

    artistas = sp.current_user_top_artists(limit=5)
    musicas = sp.current_user_top_tracks(limit=5)
    recentes = sp.current_user_recently_played(limit=5)
    for item in recentes["items"]:
        data = datetime.fromisoformat( item["played_at"].replace("Z", "+00:00"))

        item["data_formatada"] = data.astimezone().strftime("%d/%m/%Y às %H:%M")

    

    return render_template(
    "index.html",
    perfil=perfil,
    artistas=artistas["items"],
    musicas=musicas["items"],
    recentes=recentes["items"]
)

if __name__ == "__main__":

    if not CLIENT_ID or not CLIENT_SECRET or not REDIRECT_URI:
        raise RuntimeError("Verifique as credenciais no arquivo .env")


    app.run(debug=True)

