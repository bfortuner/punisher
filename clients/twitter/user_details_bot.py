import tweepy
import config as cfg

auth = tweepy.OAuthHandler(cfg.TWITTER_CONSUMER_KEY, cfg.TWITTER_CONSUMER_SECRET)
auth.set_access_token(cfg.TWITTER_ACCESS_TOKEN, cfg.TWITTER_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

def get_user_details(username):
    user = api.get_user(username)

    print("Name:", user.name)
    print("User id: ", user.id_str)
    print("Description: ", user.description)
    print("Location:",user.location)
    print("Time zone: ", user.time_zone)
    print("Number of Following:",user.friends_count)
    print("Number of Followers:",user.followers_count)
    print("Number of tweets: ", str(user.statuses_count))

if __name__ == "__main__":
    get_user_details('officialmcafee')
