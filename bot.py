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

app = Flask(__name__)

def reply_to_tweet(tweet_id, original_url):
    try:
        client = tweepy.Client(
            consumer_key=API_KEY,
            consumer_secret=API_KEY_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_TOKEN_SECRET
        )
        
        # Free Tier Workaround: Post a standalone tweet with the link attached
        # This bypasses the blocked 'in_reply_to_tweet_id' feature while keeping the context tied together!
        public_message = f"{REPLY_MESSAGE}\n\nContext: {original_url}"
        
        response = client.create_tweet(text=public_message)
        print(f" Successfully posted public broadcast for tweet ID: {tweet_id}!")
        return True
            
    except Exception as e:
        print(f"❌ Failed to send reply: {e}")
        return False

@app.route('/')
def home():
    return "Bot is awake!", 200
    
@app.route('/trigger-reply', methods=['POST'])
def trigger_reply():
    data = request.json or {}
    
    # Extract the LinkToTweet payload from IFTTT
    tweet_url = data.get('LinkToTweet', data.get('tweet_url', ''))
    
    try:
        tweet_id = tweet_url.split('/status/')[-1].split('?')[0]
    except Exception:
        tweet_id = None

    if tweet_id and tweet_id.isdigit():
        print(f"🚨 IFTTT ALERT! Processing message context for Tweet ID: {tweet_id}")
        
        # Pass both the ID and the raw URL down to the tweet handler
        success = reply_to_tweet(tweet_id, tweet_url)
        if success:
            return jsonify({"status": "success"}), 200
        return jsonify({"status": "failed"}), 500
        
    return jsonify({"status": "error", "message": "Invalid or missing tweet_url"}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
