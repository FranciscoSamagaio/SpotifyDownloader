import requests
import urllib.parse
import json

from flask import Flask, redirect, request, jsonify, session
from datetime import datetime

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = '192b9bdd22ab9ed4d12e236c78afcb9a3'

CLIENT_ID = '8a32e7538e224beab1b1cfa6f38463b3'
CLIENT_SECRET = 'c496c68c14f14d6096d0d956289f1a95'
REDIRECT_URI = 'http://localhost:5000/callback'

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'


@app.route('/')
def index():
    return "Welcome to my Spotify App <a href='/login'> Login with Spotify</a>"

@app.route('/login')
def login():
    scope = 'user-read-private user-read-email'

    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri' : REDIRECT_URI,
        'scope': scope,
        'show_dialog': True
    }

    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

    return redirect(auth_url)

@app.route('/callback')
def callback():
    if 'error' in request.args:
        return jsonify({"error": request.args['error']})
    
    if 'code' in request.args:
        req_body = {
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'redirect_uri' : REDIRECT_URI,
        }
        response = requests.post(TOKEN_URL, data=req_body)
        token_info = response.json()

        session['access_token'] = token_info['access_token']
        session['refresh_token'] = token_info['refresh_token']
        session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']

        return redirect('/playlist')
    
@app.route('/playlist')
def get_playlist():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    response = requests.get(API_BASE_URL + 'me/playlists/', headers=headers)

    print(response.text)

    playlist= response.json()

    # Extract JSON content using get_json()
    data = response.json()

    # Extract IDs and names from each playlist
    playlist_info = [(playlist['id'], playlist['name']) for playlist in data['items']]

    # Print or use the extracted information
    for playlist_id, playlist_name in playlist_info:
        print(f"Playlist ID: {playlist_id}, Name: {playlist_name}")

    return jsonify(data)

@app.route('/refresh-token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')

    if datetime.now().timestamp() > session['expires_at']:
        req_body = {
            'grant_type': 'refresh_token',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'redirect_uri': REDIRECT_URI,
            'refresh_token': session['refresh_token'],  # Include the refresh_token
        }

        response = requests.post(TOKEN_URL, data=req_body)
        new_token_info = response.json()

        session['access_token'] = new_token_info['access_token']
        session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']

        return redirect('/playlist')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)