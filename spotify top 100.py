import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

spotify_client_id = os.environ.get('SPOTIFY_CLIENT_ID')
print(spotify_client_id)
spotify_client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')
redirect_uri = "http://localhost:8888/callback"
base_url = "https://api.spotify.com"
token_url = "https://accounts.spotify.com/api/token"
user_name = "username"



# web-scrapping billboard
def get_date():
    date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")
    try:
        year, month, day = date.split('-')
        month = int(month)
        day = int(day)
        if month < 1 or month > 12:
            raise ValueError("Invalid month. Must be between 01 and 12.")
        if day < 1 or day > 31:
            raise ValueError("Invalid day. Must be between 01 and 31.")
    except ValueError as e:
        print(f"Invalid input: {e}")
        return None
    return date


date = get_date()
url = f"https://www.billboard.com/charts/hot-100/{date}"
response = requests.get(url)

soup = BeautifulSoup(response.text, 'html.parser')
song_names_spans = soup.select("li ul li h3")
song_names = [song.getText().strip() for song in song_names_spans]

# Headers
headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}

# Data payload for the POST request
data = {
    "grant_type": "client_credentials",
    "client_id": spotify_client_id,
    "client_secret": spotify_client_secret
}

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="playlist-modify-private", redirect_uri=redirect_uri,
                                               client_id=spotify_client_id, client_secret=spotify_client_secret,
                                               show_dialog=True,
                                               cache_path="token.txt",
                                               username=user_name))


def get_user_id():
    user_id = sp.current_user()["id"]
    return user_id


# Check if the request was successful
def get_access_token():
    response = requests.post(token_url, headers=headers, data=data)
    if response.status_code == 200:
        token_info = response.json()
        access_token = token_info.get('access_token')
        # print(f"Access Token: {access_token}")
        return access_token
    else:
        print(f"Failed to obtain token: {response.status_code}")
        print(response.text)


access_token = get_access_token()

# get artist_data
art_url = "https://api.spotify.com/v1/artists/4Z8W4fKeB5YxbusRsdQVPb"
art_headers = {"Authorization": "Bearer " + access_token}
art_response = requests.get(url=art_url, headers=art_headers)

YYYY = date.split("-")[0]
uri_list = []
main_list = []

# search for songs
for name in song_names:
    song_uri = sp.search(q=f"track: {name} year: {YYYY}", type='track')
    try:
        uri = song_uri["tracks"]["items"][0]["uri"]
        uri_list.append(uri)
    except IndexError:
        print(f"{name} doesn't exist in Spotify. Skipped.")

# CREATE SPOTIFY PLAYLIST
playlist = sp.user_playlist_create(user=get_user_id(), name="Python Playlist", public=False, collaborative=False,
                                   description="A playlist for python using spotipy")

print(f"Playlist ID: {playlist['id']}")


def add_playlist():
    sp.user_playlist_add_tracks(user=get_user_id(), playlist_id=playlist["id"],
                                tracks=[uri for uri in uri_list])


add_playlist()
