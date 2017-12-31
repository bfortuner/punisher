import tweepy
from config import *
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

tweets = api.user_timeline('officialmcafee')

for tweet in tweets:
    print("Msg", tweet.text)
    #print("Keys")


