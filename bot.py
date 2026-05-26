import os
import tweepy
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_KEY_SECRET = os.getenv("API_KEY_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

REPLY_MESSAGE = "Bring DEMOLITION to HARDCORE in BO7 PLEASE!!!! We're still stuck playing Cold War to enjoy HC Demo - there's DOZENS OF US!!!! PLzzzZzzZ <3"

# Turn the bot into a web service
app = Flask(__name__)

def reply_to_tweet(tweet_id):
    try:
        client = tweepy.Client(
            consumer_key=API_KEY, consumer_secret=API_KEY_SECRET,
            access_token=ACCESS_TOKEN, access_token_secret=ACCESS_TOKEN_SECRET
        )
        response = client.create_tweet(text=REPLY_MESSAGE, in_reply_to_tweet_id=tweet_id)
        print(f" Successfully replied to tweet {tweet_id}!")
        return True
    except Exception as e:
        print(f"❌ Failed to send reply: {e}")
        return False

@app.route('/trigger-reply', methods=['POST'])
def trigger_reply():
    data = request.json
    # Expecting the automation service to pass us the tweet ID
    tweet_id = data.get('tweet_id')
    
    if tweet_id:
        print(f"🚨 ALERT received! Attempting to reply to Tweet ID: {tweet_id}")
        success = reply_to_tweet(tweet_id)
        if success:
            return jsonify({"status": "success"}), 200
        return jsonify({"status": "failed", "error": "Tweepy error"}), 500
        
    return jsonify({"status": "error", "message": "No tweet_id provided"}), 400

if __name__ == "__main__":
    # Render assigns a port automatically
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
