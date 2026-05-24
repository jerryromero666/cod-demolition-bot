import tweepy
from ntscraper import Nitter
import time

# Your working credentials
API_KEY = "Qm3sjlEJd9IjmoN56t4TpQMFE"
API_KEY_SECRET = "uMwnMNsn8SIJGJTUKR9nnguCJ4Czy7cz2gRj0Q75oRV6LVvN40"
ACCESS_TOKEN = "2050297362124615680-wMz2bipzheN5Co6lhppO7vlWiQjxRE"
ACCESS_TOKEN_SECRET = "0GqiX0Qd5Cp73LDaOOdJXdILn4Kd55Mos3RdBr5IIFzWX"

# The target accounts to watch
TARGET_ACCOUNTS = ["CallofDuty", "Treyarch", "CallofDutyCM"]

# Your custom campaign message
REPLY_MESSAGE = "Bring DEMOLITION to HARDCORE in BO7 PLEASE!!!! We're still stuck playing Cold War to enjoy HC Demo - there's DOZENS OF US!!!! PLzzzZzzZ <3"

# Dictionary to keep track of the last tweet ID we saw for each user
# This prevents the bot from replying to the same tweet over and over
last_seen_tweets = {account: None for account in TARGET_ACCOUNTS}

def create_client():
    return tweepy.Client(
        consumer_key=API_KEY,
        consumer_secret=API_KEY_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET
    )

def reply_to_tweet(tweet_id):
    """Sends your specific reply to a target tweet ID."""
    try:
        client = create_client()
        # in_reply_to_tweet_id attaches it as a comment under their tweet
        response = client.create_tweet(text=REPLY_MESSAGE, in_reply_to_tweet_id=tweet_id)
        print(f" Successfully replied to tweet {tweet_id}!")
    except Exception as e:
        print(f"❌ Failed to send reply: {e}")

def check_for_new_tweets():
    """Scrapes the targets for new posts without using the paid API."""
    scraper = Nitter()
    
    for account in TARGET_ACCOUNTS:
        try:
            print(f"Checking @{account} for new tweets...")
            # Fetch the single newest tweet from their profile (excluding retweets)
            tweets = scraper.get_profile_info(account)
            # Get their latest numeric tweet ID
            latest_tweets = scraper.get_tweets(account, mode='user', number=1)
            
            if latest_tweets and 'tweets' in latest_tweets and len(latest_tweets['tweets']) > 0:
                current_tweet = latest_tweets['tweets'][0]
                tweet_id = current_tweet['tweet_id']
                
                # If this is the first run, just bookmark their latest tweet so we don't spam old posts
                if last_seen_tweets[account] is None:
                    last_seen_tweets[account] = tweet_id
                    print(f"Bookmarked latest tweet for @{account}: {tweet_id}")
                    continue
                
                # If the ID has changed, they posted something new!
                if tweet_id != last_seen_tweets[account]:
                    print(f"🚨 NEW TWEET DETECTED from @{account}!")
                    last_seen_tweets[account] = tweet_id
                    reply_to_tweet(tweet_id)
                    
        except Exception as e:
            print(f"Error checking @{account}: {e}")

if __name__ == "__main__":
    print("🤖 Bot started. Standing by for Call of Duty updates...")
    
    # Run forever
    while True:
        check_for_new_tweets()
        # Wait 30 seconds before checking again to avoid getting blocked
        print("Waiting 30 seconds before next check...\n")
        time.sleep(30)