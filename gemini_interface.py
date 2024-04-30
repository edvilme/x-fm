import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('.env')

# Configure generative AI
genai.configure(api_key=os.environ.get('GENAI_API_KEY'))
gemini_model = genai.GenerativeModel('gemini-pro')

# Receive tweet objects to generate script for radio show
def generate_script(tweets):
    # Generate script
    script = gemini_model.generate_content(
            f"""
            Generate a script for a podcast/radio show called X.FM. This is a customized show that is tailored to the listener's interests, and it is hosted by an unnamed virtual host. The news and topics discussed on the show are based on the latest tweets from the listener's Twitter feed.

            The script will be fed into a text-to-speech engine to create an audio version of the show, so avoid using any visual elements or references that would not translate well to an audio format.
            
            The script should be divided into segments, with each segment focusing on a different topic. The host should summarize the tweets and provide commentary on each topic, if necessary, add extra information to keep the listener engaged. The script should be engaging and informative. 

            Format the script in a way that it can be read out loud by Google Text-to-Speech. Make it at least 500 words long.

            Avoid using any kind of placeholders like *tweet 1*, *tweet 2*, *Community Member 1* or *Trending Topic 1", instead use the actual content. Avoid generating any social media handles for X.FM.
            

            Tweets: {tweets}
            """,
    )
    return script.text