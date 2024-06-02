"""
This example module shows various types of documentation available for use
with pydoc.  To generate HTML documentation for this module issue the
command:

        pydoc -w foo

"""

import streamlit as st
import requests
import base64
import json
import pandas
import statistics
import pandas as pd
import uuid
import matplotlib.pyplot as plt

CLIENT_ID = '52b35c378f1f48e691bf39d4b004a5b3'
CLIENT_SECRET = '31993222478349968efa385c178f78e6'

TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_URL = 'https://api.spotify.com/v1'

PLAYLISTS_URL = API_URL + '/playlists'
FEATURES_URL = API_URL + '/audio-features'

# dodanie pustych albo domyślnych wartości do stanu który jest zachowany pomiędzy kliknięciami
if 'playlist_id' not in st.session_state:
    st.session_state['playlist_id'] = ''

if 'page' not in st.session_state:
    st.session_state['page'] = 'mainpage'

if 'custom_playlists' not in st.session_state:
    st.session_state['custom_playlists'] = []

if 'playlist_to_show' not in st.session_state:
    st.session_state['playlist_to_show'] = []

def get_access_token(client_id, client_secret):
    """
    Pobiera token sesji API spotify

    :param client_id: client id aplikacji
    :param client_secret: sekret aplikacji
    """

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
    """
    Pobiera playlisty wg API spotify: link https://developer.spotify.com/documentation/web-api/reference/get-playlist

    :param access_token: token sesji
    :param playlist_id: id playlisty
    """
    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    response = requests.get(f"{PLAYLISTS_URL}/{playlist_id}" , headers=headers)
    responseJson = response.json()
    next = responseJson['tracks']['next']

    while next:

        responseNext = requests.get(next , headers=headers)

        responseJson['tracks']['items'].extend(responseNext.json()['items'])
        next = responseNext.json()['next']

    return responseJson


def get_audio_features(access_token, songs_ids):
    """
    Pobiera własności utworów wg API spotify: https://developer.spotify.com/documentation/web-api/reference/get-several-audio-features

    :param access_token: token sesji
    :param songs_ids: lista id utworów
    :return: lista właściwości utworów
    """
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    features = {'audio_features': []}

    for i in range(0, len(songs_ids), 100):
        chunk = songs_ids[i:i + 100]
        chunk_url = '%2C'.join(chunk)
        response = requests.get(f"{FEATURES_URL}/?ids={chunk_url}" , headers=headers)
        features['audio_features'].extend(response.json()['audio_features'])

    return features


# wyciągnięcie id piosenek z obiektu playlisty
def get_ids_from_playlist(playlist):
    ids = []
    for track in playlist['tracks']['items']:
        ids.append(track['track']['id'])
    return ids

def show_audio_features_info(audio_features):
    """
    Wyświetlenie średnich właściwości utworów na ekranie

    :param audio_features: lista właściwości utworów
    :return: None
    """

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
            plt.pie([mean(name), 1 - mean(name)],  colors=['b','w'], startangle=90)
            column.pyplot(plt, use_container_width=True)
            column.metric(name, round(mean(name), 2))

        for (name, column) in zip(row2, columns2):
            plt.pie([mean(name), 1 - mean(name)],  colors=['b','w'], startangle=90)
            column.pyplot(plt, use_container_width=True)
            column.metric(name, round(mean(name), 2))

# wyświetlenie na ekranie statystyk doczyczących playlisty stworzonej przez użytkownika
def show_audio_features_info_custom(audio_features):
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
            return statistics.mean(map((lambda t: t['features'][feature_names[name]]), audio_features))

        for (name, column) in zip(row1, columns1):
            plt.pie([mean(name), 1 - mean(name)],  colors=['b','w'], startangle=90)
            column.pyplot(plt, use_container_width=True)
            column.metric(name, round(mean(name), 2))

        for (name, column) in zip(row2, columns2):
            plt.pie([mean(name), 1 - mean(name)],  colors=['b','w'], startangle=90)
            column.pyplot(plt, use_container_width=True)
            column.metric(name, round(mean(name), 2))

def songs_to_dataframe(songs):
    """
    Przekształcenie listy piosenek do dataframe'u biblioteki pandas.
    Potrzebne do wyświetlenia listy piosenek na ekranie w estetyczny sposób.

    :param songs: lista piosenek z api spotify
    :return: lista piosenek w dataframe'ie pandas
    """
    songs_info = []
    for s in songs:
        songs_info.append({'Artysta': s['track']['artists'][0]['name']
                         , 'Tytuł': s['track']['name']
                         , 'Odtwórz': '<a href="https://open.spotify.com/track/' + s['track']['id'] + '"><img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQu_b8IVLbSnfcJpRR1_klGnu00kfHCTitebQ&s" style="width: 20px"></img></a>'})

    df = pd.DataFrame(songs_info)

    expander = st.expander('Lista piosenek', expanded=True)
    with expander:
        st.markdown(df.to_html(escape=False), unsafe_allow_html=True)

st.header("Spotify mixer")

# dodanie playlisty stworzonej przez użytkownika do stanu, czyli obiektu który jest zachowywany pomiedzy kliknięciami użytkownika
def show_custom_playlist(songs):
    st.session_state['playlist_to_show'] = songs['playlist']

def new_playlist():
    """
    Wyświeltenie strony tworzenia nowej playlisty
    """
    st.caption("Nowa playlista")

    # utworzenie suwaków wyboru statystyk
    dnc = st.slider('taneczność', min_value=0.0, max_value=1.0, value=(0.0, 1.0))
    eng = st.slider('energiczność', min_value=0.0, max_value=1.0, value=(0.0, 1.0))
    acu = st.slider('akustyczność', min_value=0.0, max_value=1.0, value=(0.0, 1.0))
    ins = st.slider('instrumentalność', min_value=0.0, max_value=1.0, value=(0.0, 1.0))
    liv = st.slider('żywość', min_value=0.0, max_value=1.0, value=(0.0, 1.0))
    val = st.slider('szczęśliwość', min_value=0.0, max_value=1.0, value=(0.0, 1.0))

    big_playlist_id = '4Dg0J0ICj9kKTGDyFu0Cv4'

    btn = st.button(":minidisc: Utwórz", use_container_width=True)

    # zrobienie listy tupli z listy utworów i listy statystyk utworów
    def zip_tracks_features(tracks, features):
        zipped = zip(tracks, features)
        track_with_features = []
        for pair in zipped:
            pair[0]['features'] = pair[1]
            track_with_features.append(pair[0])
        return track_with_features

    # filtrowanie po statystykach wybranych przez użytkownika
    def filter_features(track):
        features = track['features']
        conditions = [ dnc[0] <= features['danceability'] <= dnc[1],
                       eng[0] <= features['energy'] <= eng[1],
                       acu[0] <= features['acousticness'] <= acu[1],
                       ins[0] <= features['instrumentalness'] <= ins[1],
                       liv[0] <= features['liveness'] <= liv[1],
                       val[0] <= features['valence'] <= val[1] ]
        return all(conditions)

    def filter_tracks(tracks):
        fil = filter(filter_features, tracks)
        return list(fil)

    # wyświetlenie liczby wszystkich utworów oraz tych spełniających wybrane przez użytkownika statystyki
    def lengths(all, filtered):
        expander = st.expander('Liczba utworów', expanded=True)
        with expander:
            st.metric('Spełniające warunki', filtered)

    # zapisanie playlisty
    if btn:
        access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)
        if access_token:
            playlist = get_playlist(access_token, big_playlist_id)
            if playlist:
                songs_ids = get_ids_from_playlist(playlist)
                audio_features = get_audio_features(access_token, songs_ids)
                zipped = zip_tracks_features(playlist['tracks']['items'],
                                             audio_features['audio_features'])
                filtered = filter_tracks(zipped)
                lengths(len(zipped), len(filtered))

                songs_to_dataframe(filtered)

                def save_custom_playlist():
                    st.session_state['custom_playlists'].append({'name': st.session_state['new_name'], 'playlist': filtered[:]})
                    st.success('Playlista zapisana')

                name = st.text_input('Nazwa', value='Nowa playlista', key='new_name', on_change=save_custom_playlist)

                # st.button(':arrow_down: Zapisz', on_click=save_custom_playlist, args=(st.session_state['new_name'], filtered), use_container_width=True)

# wybór strony głównej
# miejsce w którym aktualnie znajduje się użytkownik jest trzymane w st.session_state, które jest niezmienne pomiędzy kliknięciami użytkownika
def go_to_mainpage():
    st.session_state['page'] = 'mainpage'

# wybór strony "Nowa playlista"
def go_to_new_playlist():
    st.session_state['page'] = 'new_playlist'

def mainpage():
    """
    Wyświeltenie strony głównej
    """
    st.caption("Playlisty")

    col1, col2, col3, col4 = st.columns(4)

    # kolumny z przyciskami z wbudowanymi playlistami
    with col1:
        col1.image('https://cdn-icons-png.flaticon.com/512/636/636224.png')
        pl1 = st.button('Piosenki do płakania', use_container_width=True)

    with col2:
        col2.image('https://cdn-icons-png.flaticon.com/512/636/636224.png')
        pl2 = st.button("Piosenki do tańczenia", use_container_width=True)

    with col3:
        col3.image('https://cdn-icons-png.flaticon.com/512/636/636224.png')
        pl3 = st.button("Spokojny jazz", use_container_width=True)

    with col4:
        col4.image('https://cdn-icons-png.flaticon.com/512/636/636224.png')
        pl4 = st.button("Szybki jogging", use_container_width=True)

    if pl1:
        st.session_state['playlist_id'] = '37i9dQZF1EIdChYeHNDfK5'
    elif pl2:
        st.session_state['playlist_id'] = '7qZcphQz8AJd7V4CmUI4dA'
    elif pl3:
        st.session_state['playlist_id'] = '6c8RcZLx8DGlPdq7XLVr9g'
    elif pl4:
        st.session_state['playlist_id'] = '0zFDgi3VsLZUHH9NerfQ8t'

    custom_playlists = st.session_state['custom_playlists']

    # wyświetlenie przycisków po 4 w rzędzie
    for i in range(0, len(custom_playlists), 4):
        chunk = custom_playlists[i:i + 4]
        col1, col2, col3, col4 = st.columns(4)
        try:
            col1.image('https://cdn-icons-png.flaticon.com/512/636/636224.png')
            col1.button(chunk[0]['name'], key=uuid.uuid1(), use_container_width=True, on_click=show_custom_playlist, args=(chunk[0],))
            col2.image('https://cdn-icons-png.flaticon.com/512/636/636224.png')
            col2.button(":dvd: " + chunk[1]['name'], key=uuid.uuid1(), use_container_width=True, on_click=show_custom_playlist, args=(chunk[1],))
            col3.button(":dvd: " + chunk[1]['name'], key=uuid.uuid1(), use_container_width=True, on_click=show_custom_playlist, args=(chunk[1],))
            col3.button(":dvd: " + chunk[2]['name'], key=uuid.uuid1(), use_container_width=True, on_click=show_custom_playlist, args=(chunk[2],))
            col3.button(":dvd: " + chunk[2]['name'], key=uuid.uuid1(), use_container_width=True, on_click=show_custom_playlist, args=(chunk[2],))
            col4.button(":dvd: " + chunk[1]['name'], key=uuid.uuid1(), use_container_width=True, on_click=show_custom_playlist, args=(chunk[1],))
            col4.button(":dvd: " + chunk[3]['name'], key=uuid.uuid1(), use_container_width=True, on_click=show_custom_playlist, args=(chunk[3],))
        except IndexError:
            break

    if st.session_state['playlist_id']:
        access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)
        if access_token:
            playlist = get_playlist(access_token, st.session_state['playlist_id'])
            if playlist:
                songs_ids = get_ids_from_playlist(playlist)
                audio_features = get_audio_features(access_token, songs_ids)
                show_audio_features_info(audio_features)
                songs_to_dataframe(playlist['tracks']['items'])
            else:
                print("No playlists found.")
    elif st.session_state['playlist_to_show']:
        show_audio_features_info_custom(st.session_state['playlist_to_show'])
        songs_to_dataframe(st.session_state['playlist_to_show'])

if __name__ == "__main__":

    # pasek boczny
    with st.sidebar:
        st.button(":house: Strona główna", use_container_width=True, on_click=go_to_mainpage)
        st.button(":heavy_plus_sign: Nowa playlista", use_container_width=True, on_click=go_to_new_playlist)

    if st.session_state.page == 'mainpage':
        mainpage()
    elif st.session_state.page == 'new_playlist':
        new_playlist()
