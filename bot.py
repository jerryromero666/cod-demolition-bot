import os
import re
import tweepy
from datetime import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY", "").strip()
API_KEY_SECRET = os.getenv("API_KEY_SECRET", "").strip()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "").strip()
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET", "").strip()

BASE_MESSAGE = "Bring DEMOLITION to HARDCORE in BO7 PLEASE!!!! We're still stuck playing Cold War to enjoy HC Demo - there's DOZENS OF US!!!! PLzzzZzzZ <3"

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
        
        current_time = datetime.now().strftime("%m/%d %I:%M %p")
        
        # Build payload conditionally based on whether we successfully parsed a target tweet ID
        if tweet_id:
            public_message = f"{BASE_MESSAGE}\n\nContext: {original_url}\n📌 Sent at: {current_time}"
            # reply_category parameter links it directly as a comment thread
            response = client.create_tweet(text=public_message, in_reply_to_tweet_id=tweet_id)
        else:
            # Safe standalone fallback tweet if IFTTT sent mangled text
            public_message = f"{BASE_MESSAGE}\n\n📌 Broadcast Time: {current_time}"
            response = client.create_tweet(text=public_message)
            
        print("✅ Tweet dispatched smoothly!")
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
    # Capture whatever raw text payload IFTTT sends, even if it isn't perfect JSON
    data = request.json or {}
    tweet_url = str(data.get('LinkToTweet', data.get('tweet_url', ''))).strip()
    
    print(f"📥 Received payload string from IFTTT: '{tweet_url}'")
    
    # Use a regular expression to pull out any 15-20 digit Tweet ID number anywhere in the string
    found_ids = re.findall(r'\d{15,20}', tweet_url)
    tweet_id = found_ids[0] if found_ids else None

    # We always execute a post now—no more 400 rejection crashes to IFTTT!
    success, diagnostic_info = reply_to_tweet(tweet_id, tweet_url)
    
    if success:
        return jsonify({"status": "success", "processed_id": tweet_id}), 200
    else:
        # We return a 202 accepted so IFTTT doesn't freak out and turn off the applet again
        return jsonify({"status": "accepted_with_api_warning", "details": diagnostic_info}), 202

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
