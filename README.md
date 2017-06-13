#spoti-flask

This is a small flask application creating an API for controlling Spotify on a
computer. It’s built to work with the spot.coffee script in [Minton’s Spot repo.](https://github.com/minton/spot) (All functionality not necessarily supported
though.) It uses Python 3.

## Setup

Clone the repo to the machine that is running Spotify and cd to its directory.

Recommended: create a virtualenv

`virtualenv -p python3 venv`

and activate it

`source venv/bin/activate`

Install requirements:

`pip install -r requirements.txt`

Note: searching requires Spotify API access. Be sure to have environment variables
on the machine running Spotify for your client ID and secret. Might want to
add to the `.bash_profile`

`export SPOTIPY_CLIENT_ID='<your id>'`
`SPOTIPY_CLIENT_SECRET='<your secret>'`

## Running

`python app.py`
