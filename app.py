from flask import Flask, Response, render_template, redirect, request, jsonify, session
from flask_cors import CORS
import requests
import random
import os

app = Flask(__name__)

# app.secret_key = 'sua_chave_secreta'  # precisa para sessions

# Spotify API credentials
CLIENT_ID = '2884a91101e24d10ac44b379b7420da6'
CLIENT_SECRET = 'e0c1c8a950ae4ab19ad3bc62afe0a0c4'
REDIRECT_URI = 'https://localhost/oauth2callback'

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1"

SCOPES = 'playlist-modify-private playlist-modify-public user-library-read'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/go')
def go():
    return redirect(
        "https://open.spotify.com/intl-pt/album/0uj28c7dMMgO59Jzx84bSE?si=mdhMx9yVTrGLJfvNpC1EdQ"
    )


@app.after_request
def add_csp(response: Response):
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "frame-src https://www.youtube.com https://www.youtube-nocookie.com; "
        "img-src 'self' data:; "
        "style-src 'self' 'unsafe-inline'; "
        "script-src 'self' 'unsafe-inline';"
    )
    return response


# Endpoint para criar a playlist
@app.route('/create_random_playlist')
def create_random_playlist():
    access_token = session.get('spotify_token')

    if not access_token:
        # Redireciona para login se não estiver autenticado
        auth_query = {
            "response_type": "code",
            "redirect_uri": REDIRECT_URI,
            "scope": SCOPES,
            "client_id": CLIENT_ID
        }
        auth_url = requests.Request('GET', SPOTIFY_AUTH_URL, params=auth_query).prepare().url
        return redirect(auth_url)

    # Já autenticado, continua:
    headers = {'Authorization': f'Bearer {access_token}'}

    # Buscar músicas curtidas
    response = requests.get(f"{SPOTIFY_API_BASE_URL}/me/tracks?limit=50", headers=headers)
    if response.status_code != 200:
        # Se der erro, limpa a session e força novo login
        session.pop('spotify_token', None)
        return redirect('/create_random_playlist')

    tracks_data = response.json()
    tracks = [item['track']['uri'] for item in tracks_data.get('items', [])]

    if len(tracks) < 5:
        return "Poucas músicas curtidas para criar playlist."

    random_tracks = random.sample(tracks, 5)

    # Obter ID do usuário
    user_response = requests.get(f"{SPOTIFY_API_BASE_URL}/me", headers=headers)
    user_id = user_response.json()['id']

    # Criar nova playlist
    playlist_data = {
        'name': 'Minha Playlist Aleatória 🎵',
        'description': 'Criada automaticamente!',
        'public': False
    }
    playlist_response = requests.post(f"{SPOTIFY_API_BASE_URL}/users/{user_id}/playlists", headers=headers, json=playlist_data)
    playlist = playlist_response.json()
    playlist_id = playlist['id']

    # Adicionar faixas
    add_tracks_url = f"{SPOTIFY_API_BASE_URL}/playlists/{playlist_id}/tracks"
    requests.post(add_tracks_url, headers=headers, json={'uris': random_tracks})

    # Redireciona para a playlist
    playlist_url = playlist['external_urls']['spotify']
    return redirect(playlist_url)


@app.route('/callback')
def callback():
    code = request.args.get('code')
    if code is None:
        return "Erro ao logar no Spotify."

    # Trocar código por token
    token_response = requests.post(SPOTIFY_TOKEN_URL, data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    })
    token_info = token_response.json()

    if 'access_token' not in token_info:
        return "Erro ao obter token."

    session['spotify_token'] = token_info['access_token']
    return redirect('/create_random_playlist')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
