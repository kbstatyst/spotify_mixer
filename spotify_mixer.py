import streamlit as st
import requests
import base64
import json
import pandas
import statistics
import pandas as pd

CLIENT_ID = ''
CLIENT_SECRET = ''

TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_URL = 'https://api.spotify.com/v1'

PLAYLISTS_URL = API_URL + '/playlists'
FEATURES_URL = API_URL + '/audio-features'

if 'playlist_id' not in st.session_state:
    st.session_state['playlist_id'] = ''

def get_access_token(client_id, client_secret):
    client_credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded_client_credentials = base64.b64encode(client_credentials.encode()).decode()

    headers = {
        'Authorization': f'Basic {encoded_client_credentials}',
    }
    data = {
        'grant_type': 'client_credentials',
    }

    response = requests.post(TOKEN_URL, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        print("Failed to retrieve access token.")
        return None

def get_playlist(access_token, playlist_id):
    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    response = requests.get(f"{PLAYLISTS_URL}/{playlist_id}" , headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to retrieve playlists.")
        return None

def get_audio_features(access_token, songs_ids):
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.get(f"{FEATURES_URL}/?ids={songs_ids}" , headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to retrieve audio features.")
        return None

def get_ids_from_playlist(playlist):
    ids = []
    for track in playlist['tracks']['items']:
        ids.append(track['track']['id'])
    return '%2C'.join(ids)

def show_audio_features_info(audio_features):
    feature_names = {'taneczność': 'danceability',
                     'energiczność': 'energy',
                     'akustyczność': 'acousticness',
                     'instrumentalność': 'instrumentalness',
                     'żywość': 'liveness',
                     'szczęśliwość': 'valence'}

    expander = st.expander('Statystyki')

    with expander:
        keys = list(feature_names.keys())
        row1 = keys[0:3]
        row2 = keys[3:6]

        columns1 = st.columns(3)
        columns2 = st.columns(3)

        def mean(name):
            return statistics.mean(map((lambda t: t[feature_names[name]]), audio_features['audio_features']))

        for (name, column) in zip(row1, columns1):
            column.metric(name, mean(name))

        for (name, column) in zip(row2, columns2):
            column.metric(name, mean(name))

def songs_to_dataframe(songs):
    # df = pd.DataFrame(np.random.randn(10, 5), columns=("col %d" % i for i in range(5)))
    songs_info = []
    for s in songs:
        songs_info.append({'Artysta': s['track']['artists'][0]['name'], 'Tytuł': s['track']['name']})

    df = pd.DataFrame(songs_info)

    expander = st.expander('Lista piosenek', expanded=True)
    with expander:
        st.table(df)

st.header("Spotify mixer")
st.caption("Playlisty")

col1, col2, col3, col4 = st.columns(4)

with col1:
    pl1 = st.button(":minidisc: Piosenki do płakania", use_container_width=True)

with col2:
    pl2 = st.button(":minidisc: Piosenki do tańczenia", use_container_width=True)

with col3:
    pl3 = st.button(":minidisc: Spokojny jazz", use_container_width=True)

with col4:
    pl4 = st.button(":minidisc: Szybki jogging", use_container_width=True)

if pl1:
    st.session_state['playlist_id'] = '37i9dQZF1EIdChYeHNDfK5'
elif pl2:
    st.session_state['playlist_id'] = '7qZcphQz8AJd7V4CmUI4dA'
elif pl3:
    st.session_state['playlist_id'] = '6c8RcZLx8DGlPdq7XLVr9g'
elif pl4:
    st.session_state['playlist_id'] = '0zFDgi3VsLZUHH9NerfQ8t'

access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)

with st.sidebar:
    st.button(":house: Strona główna", use_container_width=True)
    st.button(":heavy_plus_sign: Nowa playlista", use_container_width=True)

if access_token and st.session_state['playlist_id']:
    playlist = get_playlist(access_token, st.session_state['playlist_id'])
    if playlist:
        songs_ids = get_ids_from_playlist(playlist)
        audio_features = get_audio_features(access_token, songs_ids)
        show_audio_features_info(audio_features)
        songs_to_dataframe(playlist['tracks']['items'])
    else:
        print("No playlists found.")

# if __name__ == "__main__":
