import os
from flask import Flask, render_template, request, url_for
import oauth2 as oauth
import urllib.request
from urllib import parse
import urllib.error
import json
import tweepy
from flask import session

app = Flask(__name__)

app.debug = False

app.config.from_pyfile('config.cfg', silent=True)

# Load the environment variables
from dotenv import load_dotenv
load_dotenv(".env")

oauth2_user_handler = tweepy.OAuth2UserHandler(
    client_id = os.getenv('CLIENT_ID'),
    redirect_uri = os.getenv('REDIRECT_URI'),
    scope = ["tweet.read", "users.read", "list.read"],
    # Client Secret is only necessary if using a confidential client
    client_secret = os.getenv('CLIENT_SECRET'))

authorize_url = (oauth2_user_handler.get_authorization_url())

state = parse.parse_qs(parse.urlparse(authorize_url).query)['state'][0]

# Create a decorator to check if the user is logged in, if not redirect to the login page
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_token' not in session and os.getenv('TEST_USER_TOKEN') is None:
            return render_template('login.html', authorize_url=authorize_url)
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
@login_required
def index():
    access_token = session.get('user_token', os.getenv('TEST_USER_TOKEN'))
    client = tweepy.Client(access_token)
    user = client.get_me(user_auth=False, user_fields=['public_metrics'], tweet_fields=['author_id'])
    # Return user's name and handle as json
    return json.dumps({'name': user.data['name'], 'handle': user.data['username']})

@app.route('/callback')
def callback():
    # Accept the callback params, get the token and call the API to
    # display the logged-in user's name and handle
    received_state = request.args.get('state')
    code = request.args.get('code')
    access_denied = request.args.get('error')

    # if the OAuth request was denied, delete our local token
    # and show an error message
    if access_denied:
        return render_template('error.html', error_message="the OAuth request was denied by this user")
      
    if received_state != state:
      return render_template('error.html', error_message="There was a problem authenticating this user")
    
    redirect_uri = os.getenv('REDIRECT_URI')
    response_url_from_app = '{}?state={}&code={}'.format(redirect_uri, state, code)
    access_token = oauth2_user_handler.fetch_token(response_url_from_app)['access_token']
    print(access_token)
    client = tweepy.Client(access_token)
    user = client.get_me(user_auth=False, user_fields=['public_metrics'], tweet_fields=['author_id'])
    
    return "Logged in!"

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error_message='uncaught exception'), 500

  
if __name__ == '__main__':
    app.run()
