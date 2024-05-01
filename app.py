import io
from flask import Flask, Response, request, redirect, session
from flask_caching import Cache
import tweepy
import os
from gtts import gTTS
from dotenv import load_dotenv
from functools import wraps

from gemini_interface import generate_script

# Load environment variables from .env file
load_dotenv('.env')

# Flask app
app = Flask(__name__)
app.secret_key = "a1b2c3d4e5f6g7h8i9j0"
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

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

# Decorator to cache response based on session access token
def cache_response(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Generate cache key based on session user token
        cache_key = f"{session.get('user_token')}-{request.path}"
        # Check if response is cached
        cached_response = cache.get(cache_key)
        if cached_response:
            return cached_response
        # If response is not cached, call the view function and cache the response
        response = f(*args, **kwargs)
        cache.set(cache_key, response, timeout=60*5)  # Cache for 60 seconds
        return response
    return decorated_function

@app.route('/')
@require_authentication
@cache_response
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
    tweets_raw = client.get_home_timeline()
    tweets = [tweet.data for tweet in tweets_raw.data]
    # Generate script
    script = generate_script(tweets)
    print(script)
    # Generate the audio
    tts = gTTS(text=script, lang='en')
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
        
    # Set headers for audio streaming
    headers = {
        'Content-Type': 'audio/mpeg',
        'Content-Disposition': 'inline; filename=output.mp3'
    }
    
    return Response(mp3_fp, headers=headers, status=200)


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

if __name__ == '__main__':
    app.run(debug=True)