import streamlit as st
import requests
import base64
import json
import pandas
import statistics

CLIENT_ID = ''
CLIENT_SECRET = ''

TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_URL = 'https://api.spotify.com/v1'

PLAYLISTS_URL = API_URL + '/playlists'
FEATURES_URL = API_URL + '/audio-features'

LABELS = {'playlist_name': 'Nazwa playlisty:',
          'playlist_owner': 'Właściciel playlisty',
          'playlist_lenght': 'Liczba utworów'
         }

playlist_id = ''

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
    st.caption('Średnie danceability')
    st.text(statistics.mean(map((lambda t: t['danceability']), audio_features['audio_features'])))
    st.caption('Średnie energy')
    st.text(statistics.mean(map((lambda t: t['energy']), audio_features['audio_features'])))
    st.caption('Średnie acousticness')
    st.text(statistics.mean(map((lambda t: t['acousticness']), audio_features['audio_features'])))
    st.caption('Średnie instrumentalness')
    st.text(statistics.mean(map((lambda t: t['instrumentalness']), audio_features['audio_features'])))
    st.caption('Średnie liveness')
    st.text(statistics.mean(map((lambda t: t['liveness']), audio_features['audio_features'])))
    st.caption('Średnie valence (szczęśliwość)')
    st.text(statistics.mean(map((lambda t: t['valence']), audio_features['audio_features'])))

def show_playlist_info(playlist):
    st.caption(LABELS['playlist_name'])
    st.text(playlist['name'])
    # st.caption(LABELS['playlist_owner'])
    # st.text(playlist['owner']['display_name'])
    st.caption(LABELS['playlist_lenght'])
    st.text(len(playlist['tracks']['items']))

pl_id = st.text_input("Input playlist id", value=playlist_id)

col1, col2, col3, col4 = st.columns(4)

with col1:
    pl1 = st.button("Playlista wbudowana 1")

with col2:
    pl2 = st.button("Playlista wbudowana 2")

with col3:
    pl3 = st.button("Playlista wbudowana 3")

with col4:
    pl4 = st.button("Playlista wbudowana 3")

if pl1:
    playlist_id = '' # playlista 1
elif pl2:
    playlist_id = '' # playlista 2
elif pl3:
    playlist_id = '' # playlista 3
elif pl4:
    playlist_id = '' # playlista 4

access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)

if access_token:
    playlist = get_playlist(access_token, playlist_id)
    if playlist:
        # songs = get_songs_from_playlist(playlist)
        show_playlist_info(playlist)
        for (n, i) in enumerate(playlist['tracks']['items']):
            st.write(str(n + 1) + '. ' + i['track']['artists'][0]['name'] + ' : ' + i['track']['name'])

        stats = st.button('Statystyki')
        if stats:
            songs_ids = get_ids_from_playlist(playlist)
            audio_features = get_audio_features(access_token, songs_ids)
            show_audio_features_info(audio_features)
        # st.write(audio_features)

        # st.write(songs)
    else:
        print("No playlists found.")

# if __name__ == "__main__":
