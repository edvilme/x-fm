from io import BytesIO
import json
from flask import Flask, Response, request, redirect, send_file, session, jsonify
import tweepy
import os
from gtts import gTTS

from gemini_interface import gemini_model, generate_script

app = Flask(__name__)

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv('.env')

# Twitter API credentials
consumer_key = os.environ.get('API_KEY')
consumer_secret = os.environ.get('API_SECRET')

# Flask session secret key
app.secret_key = "a1b2c3d4e5f6g7h8i9j0"

# Tweepy OAuth1UserHandler
oauth1_user_handler = tweepy.OAuth1UserHandler(
    consumer_key=os.environ.get('API_KEY'),
    consumer_secret=os.environ.get('API_SECRET'),
    callback=os.environ.get('REDIRECT_URI')
)

# Decorator to check if user is authenticated
def require_authentication(f):
    def wrapper(*args, **kwargs):
        access_token = session.get('access_token')
        if not access_token:
            return redirect('/login')
        return f(*args, **kwargs)
    return wrapper

@app.route('/')
def index():
    return 'Welcome to the Flask-Tweepy OAuth example!'

@app.route('/login')
def login():
    redirect_url = oauth1_user_handler.get_authorization_url()
    print(redirect_url)
    return redirect(redirect_url)

@app.route('/callback')
def callback():
    oauth_verifier = request.args.get('oauth_verifier')
    oauth1_user_handler.get_access_token(oauth_verifier)
    access_token = oauth1_user_handler.access_token
    access_token_secret = oauth1_user_handler.access_token_secret
    session['access_token'] = (access_token, access_token_secret)
    return redirect('/timeline')

@app.route('/timeline')
@require_authentication
def timeline():
    access_token = session.get('access_token')
    oauth1_user_handler.set_access_token(*access_token)

    client = tweepy.Client(
        consumer_key=os.environ.get('API_KEY'),
        consumer_secret=os.environ.get('API_SECRET'),
        access_token=access_token[0],
        access_token_secret=access_token[1],
        wait_on_rate_limit=True
    )
    # Get tweets
    print("Getting tweets")
    tweets_raw = client.get_home_timeline()
    tweets = [tweet.data for tweet in tweets_raw.data]
    # Generate script
    print("Generating script")
    script = generate_script(tweets)
    # Generate speech
    print("Generating speech")
    speech_bytes = BytesIO() 
    tts = gTTS(text=script, lang='en')
    
    return Response(tts.stream(), mimetype='audio/mpeg')


    


if __name__ == '__main__':
    app.run(debug=True)