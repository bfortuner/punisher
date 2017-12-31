import tweepy
import config as cfg

auth = tweepy.OAuthHandler(cfg.TWITTER_CONSUMER_KEY, cfg.TWITTER_CONSUMER_SECRET)
auth.set_access_token(cfg.TWITTER_ACCESS_TOKEN, cfg.TWITTER_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

def get_user_tweets(username):
    tweets = api.user_timeline(username)
    for tweet in tweets:
        print("Msg", tweet.text)

if __name__ == "__main__":
    get_user_tweets('officialmcafee')


