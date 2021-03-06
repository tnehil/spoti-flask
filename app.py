from flask import Flask, request, jsonify
import appscript
import time
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import os

app = Flask(__name__)
spotify = appscript.app("Spotify")
spotify_user = os.environ["SPOTIFLASK_SPOTIFY_USER"]

#Oauth2 for spotify API access
#Be sure you have SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET
#environment variables on this machine
client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

#Separate oauth2 for modifying playlist
scope = "playlist-modify-private"
token = util.prompt_for_user_token(spotify_user, scope)
sp2 = spotipy.Spotify(auth=token)

def spotify_search(query,limit):
    results = sp.search(q=query, limit=limit, market="US")
    tracks = results['tracks']['items']
    return tracks

def serialize_track(track):
    if track == False:
        return {}
    artists = []
    if track['artists']:
        for artist in track['artists']:
            artists.append({'name': artist['name']})
    result = {
                'uri': track['uri'],
                'name': track['name'],
                'popularity': track['popularity'],
                'track_number': track['track_number'],
                'length': track['duration_ms'] / 1000,
                'artists': artists
              }
    if track['album']:
        result['album'] = {
                            'name': track['album']['name'],
                            'uri': track['album']['uri']
                          }
    return result

def current_track_info():
    title = spotify.current_track.name.get()
    artist = spotify.current_track.artist.get()
    album = spotify.current_track.album.get()
    return {"title": title, "artist": artist, "album": album}

def seconds_remaining():
    track_length = float(spotify.current_track.duration.get())/1000
    current_position = float(spotify.player_position.get())
    return int(track_length-current_position)

@app.route("/play", methods=['PUT'])
def play():
    spotify.play()
    info = current_track_info()
    return "Now playing '{}' by {}.".format(info['title'], info['artist'])

@app.route("/pause", methods=['PUT'])
def pause():
    spotify.pause()
    return "Everything is paused."

@app.route("/next", methods=['PUT'])
def next():
    spotify.next_track()
    time.sleep(.1)
    info = current_track_info()
    return "OK, fine. Maybe you'll like {} by {}".format(info['title'], info['artist'])

@app.route("/back", methods=['PUT'])
def back():
    spotify.previous_track()
    time.sleep(.1)
    info = current_track_info()
    return "Play it again, Sam. 'It' being {} by {}".format(info['title'], info['artist'])

@app.route("/playing")
def playing():
    info = current_track_info()
    return "Now playing '{}' by {}.".format(info['title'], info['artist'])

@app.route("/volume", methods=['GET','PUT'])
def volume():
    if request.method == 'GET':
        vol = spotify.sound_volume.get()
        return str(vol)
    if request.method == 'PUT':
        new_vol = request.args.get('volume')
        spotify.sound_volume.set(new_vol)
        return str(new_vol)

@app.route("/bumpup", methods=['PUT'])
def bumpup():
    vol = int(spotify.sound_volume.get())
    new_vol = vol + 6
    spotify.sound_volume.set(new_vol)
    return str(new_vol)

@app.route("/bumpdown", methods=['PUT'])
def bumpdown():
    vol = int(spotify.sound_volume.get())
    new_vol = vol - 4
    spotify.sound_volume.set(new_vol)
    return str(new_vol)

#/play-uri
@app.route("/play-uri", methods=['POST'])
def play_uri():
    track = request.args.get('uri')
    spotify.play_track(track)
    time.sleep(.1)
    return ""

#/album-info (optional)

@app.route("/seconds-left")
def seconds_left():
    return jsonify(seconds_remaining())

@app.route("/how-much-longer")
def how_much_longer():
    seconds_left = seconds_remaining()
    if seconds_left < 60:
        return jsonify("{} seconds left".format(seconds_left))
    return "{}:{:02d} left".format(int(seconds_left/60), seconds_left%60)

@app.route("/single-query")
def single_query():
    query = request.args.get('q')
    return jsonify(serialize_track(spotify_search(query,1)[0]))

#query
@app.route("/query")
def query():
    q = request.args.get('q')
    limit = request.args.get('limit')
    if limit == False:
        limit = 10
    response = []
    results = spotify_search(q, limit)
    for result in results:
        response.append(serialize_track(result))
    return jsonify(response)

@app.route("/add-to-playlist", methods=["POST"])
def add_to_playlist():
    track_uri = request.args.get("track_uri")
    playlist_uri = request.args.get("playlist_uri")
    sp2.user_playlist_add_tracks(spotify_user, playlist_uri, [track_uri])
    return "Added."

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
