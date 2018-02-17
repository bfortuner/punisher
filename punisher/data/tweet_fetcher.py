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
from punisher.clients import s3_client
from punisher.clients import twitter_client
from punisher.utils.dates import str_to_date
from punisher.utils.encoders import JSONEncoder
import punisher.utils.logger as logger_utils


parser = argparse.ArgumentParser(description='Historical Tweet Fetcher')
parser.add_argument('-q', '--query', help='Query in the format https://twitter.com/search-advanced', type=str)
parser.add_argument('-s', '--start', help='start time yyyy-mm-dd', default=None, type=str)
parser.add_argument('-e', '--end', help='end time yyyy-mm-dd', default=None, type=str)
parser.add_argument('-m', '--max', help='Max tweets to pull each day', default=1000, type=int)
parser.add_argument('-w', '--workers', help='number of workers in pool', default=1, type=int)
parser.add_argument('-r', '--retries', help='max number of retries', default=15, type=int)
parser.add_argument('--filter', help='Include only tweets w at least one like or retweet', action='store_true')
parser.add_argument('--top', help='Include only tweets from Twitters "top tweets" list', action='store_true')
parser.add_argument('--action', help='"fetch" from twitter, "download" from s3, or "list" files in S3',
                    choices=['fetch','download', 'list'], required=True)
parser.add_argument('--upload', help='upload to s3 after fetching from exchange', action='store_true')
parser.add_argument('--cleanup', help='remove local copy of files after s3 upload', action='store_true')
parser.add_argument('-o', '--outdir', help='output directory to save files', default=cfg.DATA_DIR, type=str)
parser.add_argument('-l', '--lang', type=str, default='en',
                    help="Set this flag if you want to query tweets in \na specific language. You can choose from:\n"
                         "en (English)\nar (Arabic)\nbn (Bengali)\n"
                         "cs (Czech)\nda (Danish)\nde (German)\nel (Greek)\nes (Spanish)\n"
                         "fa (Persian)\nfi (Finnish)\nfil (Filipino)\nfr (French)\n"
                         "he (Hebrew)\nhi (Hindi)\nhu (Hungarian)\n"
                         "id (Indonesian)\nit (Italian)\nja (Japanese)\n"
                         "ko (Korean)\nmsa (Malay)\nnl (Dutch)\n"
                         "no (Norwegian)\npl (Polish)\npt (Portuguese)\n"
                         "ro (Romanian)\nru (Russian)\nsv (Swedish)\n"
                         "th (Thai)\ntr (Turkish)\nuk (Ukranian)\n"
                         "ur (Urdu)\nvi (Vietnamese)\n"
                         "zh-cn (Chinese Simplified)\n"
                         "zh-tw (Chinese Traditional)"
                         )
# python -m punisher.data.tweet_fetcher --query "bitcoin OR btc" --start 2016-01-01
# --end 2016-01-02 --lang en --max 10 --upload --top --filter --action fetch --cleanup

args = parser.parse_args()
TWITTER = 'twitter'
TWITTER_DIR = Path(args.outdir, TWITTER)
TWITTER_DIR.mkdir(exist_ok=True)
MAX_RETRIES = args.retries

def get_s3_path(query, lang, date):
    fname = twitter_client.get_tweet_query_fname(query, lang, date)
    query = query.replace(' ', '_')
    return TWITTER + '/' + query + '/' + fname

def upload_to_s3(query, lang, date):
    fpath = twitter_client.get_tweet_query_fpath(query, lang, date, TWITTER_DIR)
    s3_path = get_s3_path(query, lang, date)
    print('Uploading to s3:', s3_path)
    s3_client.upload_file(str(fpath), s3_path)

@backoff.on_exception(backoff.expo,
                      Exception, #TODO: include twitter exceptions only
                      on_backoff=logger_utils.retry_hdlr,
                      on_giveup=logger_utils.giveup_hdlr,
                      max_tries=MAX_RETRIES)
def fetch_tweets(query, start, end, max_tweets, lang,
                 filter_tweets, top_tweets, upload, cleanup):
    """
    Downloads historical tweets from twitter in daily increments

    Parameters:
        query = 'bitcoin OR btc'
        start = datetime.datetime(year=2018, month=2, day=4)
        end = datetime.datetime(year=2018, month=2, day=6)
    """
    time_delta = datetime.timedelta(days=1)
    cur_start = start
    while cur_start < end:
        cur_end = cur_start + time_delta
        print("Start", cur_start, "End", cur_end)
        tweets = twitter_client.fetch_tweets(
            query, start, end, max_tweets, lang,
            filter_tweets, top_tweets
        )
        print("Downloaded", len(tweets))
        twitter_client.save_query_tweets(tweets, query, lang, cur_start)
        if upload:
            upload_to_s3(query, lang, cur_start)
        if cleanup:
            fpath = twitter_client.get_tweet_query_fpath(query, lang, cur_start, TWITTER_DIR)
            os.remove(fpath)
        cur_start = cur_end

def download_from_s3(query, start_date):
    """ Download query files for all dates """
    query = query.replace(' ', '_')
    prefix = TWITTER + '/' + query
    keys = s3_client.list_files(prefix=prefix)
    fpaths = []
    for key in keys:
        fpath = Path(TWITTER_DIR, Path(key).name)
        fpaths.append(fpath)
        print("Downloading from s3", fpath)
        s3_client.download_file(str(fpath), key)

def list_files():
    prefix = TWITTER + '/'
    keys = s3_client.list_files(prefix=prefix)
    reg = re.compile('twitter\/([a-z0-9A-Z#\$\_]+)\/([a-z0-9A-Z#\$\_]+)_(20[0-9]+)_([0-9]+)_([0-9]+).json')
    meta = {}
    for key in keys:
        m = re.match(reg, key)
        if m is not None:
            query, fname, year, month, day = m.groups()
            start = datetime.datetime(year=int(year), month=int(month), day=int(day))
            if query not in meta:
                meta[query] = {
                    'start': start,
                    'end': start + datetime.timedelta(days=1)
                }
            else:
                meta[query] = {
                    'start': min(start, meta[query]['start']),
                    'end': max(start+datetime.timedelta(days=1), meta[query]['end'])
                }
    return meta

def fetch_tweets_async(query, start, end, max_tweets, lang, filter_tweets,
                       top_tweets, upload, cleanup, workers):
    days = (end - start).days
    start_dates = [start + datetime.timedelta(days=d) for d in range(days)]
    end_dates = [date + datetime.timedelta(days=1) for date in start_dates]
    with ThreadPoolExecutor(max_workers=workers) as executor:
        _ = executor.map(
            fetch_tweets, itertools.repeat(query), start_dates, end_dates,
            itertools.repeat(max_tweets), itertools.repeat(lang),
            itertools.repeat(filter_tweets), itertools.repeat(top_tweets),
            itertools.repeat(upload), itertools.repeat(cleanup)
        )

if __name__ == "__main__":
    action = args.action
    start = str_to_date(args.start) if args.start is not None else None
    end = str_to_date(args.end) if args.end is not None else None

    if args.cleanup:
        assert args.upload is True
    if action == 'fetch':
        assert start is not None and end is not None

    if action == 'list':
        print('Listing files in S3')
        file_metadata = list_files()
        print(json.dumps(file_metadata, indent=4, cls=JSONEncoder))

    elif action == 'fetch':
        print('Fetching from twitter: ', args.query, 'start:', start, 'end:', end)
        if args.workers > 1:
            fetch_tweets_async(
                args.query, start, end, args.max, args.lang, args.filter,
                args.top, args.upload, args.cleanup, args.workers
            )
        else:
            fetch_tweets(
                args.query, start, end, args.max, args.lang,
                args.filter, args.top, args.upload, args.cleanup
            )

    elif action == 'download':
        print('Downloading from S3: ', args.query)
        download_from_s3(args.query, start)

    else:
        raise Exception("Action {:s} not supported!".format(action))
