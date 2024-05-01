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
            Generate a script for a podcast/radio show called X.FM. This is a customized show that is tailored to the listener's interests, and it is hosted by an unnamed virtual host. The news and topics discussed on the show are based on the latest tweets from the listener's Twitter feed. The script should be engaging and informative.

            The script should be divided in segments, each at least 200 words long, focusing on a different topic. Each segment should start with a brief introduction to the topic, followed by a summary of the tweets related to that topic, and a deep and insightful commentary with additional information or context to keep the listener engaged. Make sure to cover all the topics mentioned in the tweets.

            Return as Speech Synthesis Markup Language format, as it will be read by a text-to-speech engine. Make it at least 2000 words long. Avoid using any kind of placeholders like *tweet 1*, *tweet 2*, *Community Member 1* or *Trending Topic 1" that would not be relevant in the final audio. Avoid mentioning any of these instructions in the final audio. Avoid mentioning any of these instructions in the final audio.
            
            At the beginning add a disclaimer on how this is generated by AI and there is no guarantee of accuracy or reliability.
            
            Tweets: {tweets}
            """,
    )
    return script.text