import os
import re
import random
import tweepy
from datetime import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY", "").strip()
API_KEY_SECRET = os.getenv("API_KEY_SECRET", "").strip()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "").strip()
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET", "").strip()

app = Flask(__name__)

def reply_to_tweet(tweet_id, original_url):
    try:
        if not all([API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET]):
            raise ValueError("Missing X API environment keys in Render settings.")

        client = tweepy.Client(
            consumer_key=API_KEY,
            consumer_secret=API_KEY_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_TOKEN_SECRET
        )
        
        # A pool of subtle variations to bypass the identical/duplicate tweet filter cleanly
        variations = [
            " <3", " <3!", " <3 !!", " <3 :)", 
            " plzzzz.", " PLZ!", "!!! <3", " <3 ...",
            " plzzz! <3", " pleaseee <3"
        ]
        chosen_suffix = random.choice(variations)
        
        # Clean base text with absolutely no timestamps or URL link components
        clean_base = "Bring DEMOLITION to HARDCORE in BO7 PLEASE!!!! We're still stuck playing Cold War to enjoy HC Demo - there's DOZENS OF US!!!!"
        public_message = f"{clean_base}{chosen_suffix}"
        
        # Directly dispatch a normal timeline post (removes the quote-tweet look)
        response = client.create_tweet(text=public_message)
            
        print("✅ Clean text-only tweet broadcasted successfully!")
        return True, "Success"
            
    except Exception as e:
        error_msg = f"X API rejection details: {str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg

@app.route('/')
def home():
    return "Bot platform is live and monitoring traffic.", 200
    
@app.route('/trigger-reply', methods=['POST'])
def trigger_reply():
    data = request.json or {}
    tweet_url = str(data.get('LinkToTweet', data.get('tweet_url', ''))).strip()
    
    print(f"📥 Received payload string from IFTTT: '{tweet_url}'")
    
    found_ids = re.findall(r'\d{15,20}', tweet_url)
    tweet_id = found_ids[0] if found_ids else None

    success, diagnostic_info = reply_to_tweet(tweet_id, tweet_url)
    
    if success:
        return jsonify({"status": "success", "processed_id": tweet_id}), 200
    else:
        return jsonify({"status": "accepted_with_api_warning", "details": diagnostic_info}), 202

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
