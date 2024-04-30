from flask import Flask, redirect, request, session, url_for
import tweepy
import os

# Read environment variables
from dotenv import load_dotenv
load_dotenv('.env')

# Twitter API keys
consumer_key = os.getenv('API_KEY')
consumer_secret = os.getenv('API_SECRET')
callback_url = os.getenv("REDIRECT_URI")  # Update this URL with your callback URL

# Flask configuration
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Redirect users to Twitter for authorization
@app.route('/')
def home():
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, callback_url)
    try:
        redirect_url = auth.get_authorization_url()
        session['request_token'] = auth.request_token
        return redirect(redirect_url)
    except tweepy.TweepError as e:
        print(e)

# Callback route after authorization
@app.route('/callback')
def callback():
    verifier = request.args.get('oauth_verifier')
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    request_token = session['request_token']
    del session['request_token']

    auth.request_token = request_token

    try:
        auth.get_access_token(verifier)
        session['access_token'] = auth.access_token
        session['access_token_secret'] = auth.access_token_secret
        return redirect(url_for('profile'))
    except tweepy.TweepError as e:
        print(e)

# Profile route to display user info
@app.route('/profile')
def profile():
    access_token = session['access_token']
    access_token_secret = session['access_token_secret']

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # Authenticate as the user
    client = tweepy.Client(
        consumer_key=auth.consumer_key, 
        consumer_secret=auth.consumer_secret,
        access_token=auth.access_token,
        access_token_secret=auth.access_token_secret
    )

if __name__ == '__main__':
    app.run(debug=True)