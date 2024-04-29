import streamlit as st
import requests
import base64
import json

CLIENT_ID = ''
CLIENT_SECRET = ''

TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_URL = 'https://api.spotify.com/v1'

PLAYLISTS_URL = API_URL + '/playlists'
FEATURES_URL = API_URL + '/audio-features'
st.write(PLAYLISTS_URL)

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

def show_playlist_info(playlist):
    st.caption(LABELS['playlist_name'])
    st.text(playlist['name'])
    st.caption(LABELS['playlist_owner'])
    st.text(playlist['owner']['display_name'])
    st.caption(LABELS['playlist_lenght'])
    st.text(len(playlist['tracks']['items']))

pl_id = st.text_input("Input playlist id", value=playlist_id)

access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)

if access_token:
    playlist = get_playlist(access_token, pl_id)
    if playlist:
        # songs = get_songs_from_playlist(playlist)
        show_playlist_info(playlist)
        songs_ids = get_ids_from_playlist(playlist)
        audio_features = get_audio_features(access_token, songs_ids)
        st.write(audio_features)

        # st.write(songs)
    else:
        print("No playlists found.")

# if __name__ == "__main__":
