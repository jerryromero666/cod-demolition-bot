import os
import tweepy
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

# Aggressively strip any hidden newline/space strings that break OAuth validation
API_KEY = os.getenv("API_KEY", "").strip()
API_KEY_SECRET = os.getenv("API_KEY_SECRET", "").strip()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "").strip()
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET", "").strip()

REPLY_MESSAGE = "Bring DEMOLITION to HARDCORE in BO7 PLEASE!!!! We're still stuck playing Cold War to enjoy HC Demo - there's DOZENS OF US!!!! PLzzzZzzZ <3"

app = Flask(__name__)

def reply_to_tweet(tweet_id, original_url):
    try:
        # Diagnostic validation to check if key strings are empty or malformed
        if not all([API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET]):
            raise ValueError("One or more X API environment keys are missing or empty in Render.")

        client = tweepy.Client(
            consumer_key=API_KEY,
            consumer_secret=API_KEY_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_TOKEN_SECRET
        )
        
        public_message = f"{REPLY_MESSAGE}\n\nContext: {original_url}"
        
        response = client.create_tweet(text=public_message)
        print(f" Successfully posted public broadcast for tweet ID: {tweet_id}!")
        return True, "Success"
            
    except Exception as e:
        error_msg = f"X API Authentication or Payload Error: {str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg

@app.route('/')
def home():
    return "Bot is awake and tracking!", 200
    
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
        
        success, diagnostic_info = reply_to_tweet(tweet_id, tweet_url)
        if success:
            return jsonify({"status": "success"}), 200
        
        # Free diagnostic feedback: Bubble up the raw error directly to IFTTT's dashboard!
        return jsonify({"status": "failed", "reason": diagnostic_info}), 400
        
    return jsonify({"status": "error", "message": "Invalid or missing tweet_url"}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
