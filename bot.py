import os
import tweepy
import requests
import xml.etree.ElementTree as ET
import asyncio
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_KEY_SECRET = os.getenv("API_KEY_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

TARGET_ACCOUNTS = ["CallofDuty", "Treyarch", "CallofDutyCM"]
REPLY_MESSAGE = "Bring DEMOLITION to HARDCORE in BO7 PLEASE!!!! We're still stuck playing Cold War to enjoy HC Demo - there's DOZENS OF US!!!! PLzzzZzzZ <3"

last_seen_tweets = {account: None for account in TARGET_ACCOUNTS}

def reply_to_tweet(tweet_id):
    try:
        client = tweepy.Client(
            consumer_key=API_KEY, consumer_secret=API_KEY_SECRET,
            access_token=ACCESS_TOKEN, access_token_secret=ACCESS_TOKEN_SECRET
        )
        response = client.create_tweet(text=REPLY_MESSAGE, in_reply_to_tweet_id=tweet_id)
        print(f" Successfully replied to tweet {tweet_id}!")
    except Exception as e:
        print(f"❌ Failed to send reply: {e}")

async def check_for_new_tweets():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    for account in TARGET_ACCOUNTS:
        try:
            # TwisRss uses an open data stream layer specifically optimized for server feeds
            url = f"https://twisrss.org/user={account}"
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                # Parse the pure XML structure safely
                root = ET.fromstring(response.content)
                item = root.find('.//item')
                
                if item is not None:
                    link = item.find('link').text
                    # Extract the unique tweet numeric ID string from the URL
                    tweet_id = link.split('/')[-1].strip()
                    
                    if last_seen_tweets[account] is None:
                        last_seen_tweets[account] = tweet_id
                        print(f"Bookmarked latest tweet for @{account}: {tweet_id}")
                        continue
                        
                    if int(tweet_id) > int(last_seen_tweets[account]):
                        print(f"🚨 NEW TWEET DETECTED from @{account}!")
                        last_seen_tweets[account] = tweet_id
                        reply_to_tweet(tweet_id)
            else:
                print(f"⚠️ Feed platform returned status code: {response.status_code} for @{account}")
                
        except Exception as e:
            print(f"Error reading feed for @{account}: {e}")

async def main():
    print("🤖 Campaign Bot Active. Continuous Cloud Monitoring Live...")
    while True:
        await check_for_new_tweets()
        print("Waiting 60 seconds before next sync loop...\n")
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
