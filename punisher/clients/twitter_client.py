import codecs
import sys
import datetime
import json
import os
import re
import time
import traceback
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import itertools

import backoff
import pandas as pd

import punisher.constants as c
import punisher.config as cfg
from punisher.utils.dates import str_to_date, local_to_utc
from punisher.utils.encoders import JSONEncoder
import punisher.utils.logger as logger_utils

from . import s3_client
from . import got3


TWITTER = 'twitter'
TWITTER_DIR = Path(cfg.DATA_DIR, TWITTER)
TWITTER_DIR.mkdir(exist_ok=True)

def get_tweet_query_fname(query, lang, date):
    query = query.replace(' ', '_')
    fname = '{:s}_{:s}_{:d}_{:d}_{:d}.json'.format(
        query, lang, date.year, date.month, date.day
    )
    return fname

def get_tweet_query_fpath(query, lang, date, dirname=TWITTER_DIR):
    fname = get_tweet_query_fname(query, lang, date)
    query = query.replace(' ', '_')
    query_dir = Path(dirname, query)
    query_dir.mkdir(exist_ok=True)
    return Path(query_dir, fname)

def save_query_tweets(tweets, query, lang, date):
    fpath = get_tweet_query_fpath(query, lang, date)
    f = open(fpath, 'w')
    json.dump(tweets, f, cls=JSONEncoder)
    f.close()

def load_query_tweets(query, lang, date):
    fpath = get_tweet_query_fpath(query, lang, date)
    with codecs.open(fpath, 'r', 'utf-8') as f:
        tweets = json.load(f, encoding='utf-8')
    return tweets

def filter_query_tweets(tweets):
    filtered_tweets = []
    for tweet in tweets:
        if tweet.favorites > 0 or tweet.retweets > 0:
            filtered_tweets.append(tweet)
    return filtered_tweets

def cleanup_tweets(tweets):
    for tweet in tweets:
        utc_time = local_to_utc(tweet.date)
        tweet.date = utc_time
        tweet.formatted_date = utc_time
    return tweets

def fetch_tweets(query, start, end, max_tweets, lang,
                 filter_tweets, top_tweets):
    """
    Fetches historical tweets from twitter

    Parameters:
        query = 'bitcoin OR btc'
        start = datetime() in UTC
        end = datetime() in UTC

    Returns:
        Tweet objects (dates in UTC)
    """
    start_str = start.isoformat().split('T')[0]
    end_str = end.isoformat().split('T')[0]
    tweetCriteria = got3.manager.TweetCriteria().setQuerySearch(
        query).setSince(start_str).setUntil(end_str).setMaxTweets(
        max_tweets).setLang(lang).setTopTweets(top_tweets)
    tweets = got3.manager.TweetManager.getTweets(tweetCriteria)
    if filter_tweets:
        tweets = filter_query_tweets(tweets)
    tweets = cleanup_tweets(tweets)
    return tweets
