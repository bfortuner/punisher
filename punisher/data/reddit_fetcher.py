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
from punisher.clients import reddit_client
from punisher.utils.dates import str_to_date
from punisher.utils.encoders import JSONEncoder
import punisher.utils.logger as logger_utils


parser = argparse.ArgumentParser(description='Reddit Submission Fetcher')
parser.add_argument('-sr', '--subreddit', help='Subreddit name', type=str)
parser.add_argument('-s', '--start', help='start time yyyy-mm-dd', default=None, type=str)
parser.add_argument('-e', '--end', help='end time yyyy-mm-dd', default=None, type=str)
parser.add_argument('-c', '--n_comments', help='Top N comments to pull for each submission', default=10, type=int)
parser.add_argument('-w', '--workers', help='number of workers in pool', default=1, type=int)
parser.add_argument('-r', '--retries', help='max number of retries', default=15, type=int)
parser.add_argument('--action', help='"fetch" from reddit, "download" from s3, or "list" files in S3',
                    choices=['fetch','download', 'list'], required=True)
parser.add_argument('--upload', help='upload to s3 after fetching from exchange', action='store_true')
parser.add_argument('--cleanup', help='remove local copy of files after s3 upload', action='store_true')
parser.add_argument('-o', '--outdir', help='output directory to save files', default=cfg.DATA_DIR, type=str)

args = parser.parse_args()
REDDIT = 'reddit'
REDDIT_DIR = Path(args.outdir, REDDIT)
REDDIT_DIR.mkdir(exist_ok=True)
MAX_RETRIES = args.retries

def get_s3_path(subreddit, date):
    fname = reddit_client.get_subreddit_fname(subreddit, date)
    return REDDIT + '/' + subreddit + '/' + fname

def upload_to_s3(subreddit, date):
    fpath = reddit_client.get_subreddit_fpath(subreddit, date, REDDIT_DIR)
    s3_path = get_s3_path(subreddit, date)
    print('Uploading to s3:', s3_path)
    s3_client.upload_file(str(fpath), s3_path)

@backoff.on_exception(backoff.expo,
                      Exception, #TODO: include reddit exceptions only
                      on_backoff=logger_utils.retry_hdlr,
                      on_giveup=logger_utils.giveup_hdlr,
                      max_tries=MAX_RETRIES)
def fetch_submissions(subreddit, start, end, n_comments, upload, cleanup):
    """
    Downloads reddit submission and comments

    Parameters:
        subreddit: 'Bitcoin' or 'cryptocurrency'
        start: datetime.datetime(year=2018, month=2, day=4)
        end: datetime.datetime(year=2018, month=2, day=6)
    """
    time_delta = datetime.timedelta(days=1)
    cur_start = start
    while cur_start < end:
        cur_end = cur_start + time_delta
        print("Start", cur_start, "End", cur_end)
        submissions = reddit_client.get_submissions(
            subreddit, start, end, n_comments
        )
        print("Downloaded:", len(submissions))
        reddit_client.save_submissions(submissions, subreddit, cur_start)
        if upload:
            upload_to_s3(subreddit, cur_start)
        if cleanup:
            fpath = reddit_client.get_subreddit_fpath(
                subreddit, cur_start, REDDIT_DIR)
            os.remove(fpath)
        cur_start = cur_end

def download_from_s3(subreddit, start_date):
    """ Download submission files for all dates """
    prefix = REDDIT + '/' + subreddit
    keys = s3_client.list_files(prefix=prefix)
    fpaths = []
    for key in keys:
        fpath = Path(REDDIT_DIR, subreddit, Path(key).name)
        fpaths.append(fpath)
        print("Downloading from s3", fpath)
        s3_client.download_file(str(fpath), key)

def list_files():
    prefix = REDDIT + '/'
    keys = s3_client.list_files(prefix=prefix)
    reg = re.compile('reddit\/([a-z0-9A-Z#\$\_]+)\/([a-z0-9A-Z#\$\_]+)_(20[0-9]+)_([0-9]+)_([0-9]+).json')
    meta = {}
    for key in keys:
        m = re.match(reg, key)
        if m is not None:
            subreddit, fname, year, month, day = m.groups()
            start = datetime.datetime(year=int(year), month=int(month), day=int(day))
            if subreddit not in meta:
                meta[subreddit] = {
                    'start': start,
                    'end': start + datetime.timedelta(days=1)
                }
            else:
                meta[subreddit] = {
                    'start': min(start, meta[subreddit]['start']),
                    'end': max(start+datetime.timedelta(days=1), meta[subreddit]['end'])
                }
    return meta

def fetch_submissions_async(subreddit, start, end, n_comments, upload,
                            cleanup, workers):
    days = (end - start).days
    start_dates = [start + datetime.timedelta(days=d) for d in range(days)]
    end_dates = [date + datetime.timedelta(days=1) for date in start_dates]
    with ThreadPoolExecutor(max_workers=workers) as executor:
        _ = executor.map(
            fetch_submissions, itertools.repeat(subreddit), start_dates, end_dates,
            itertools.repeat(n_comments), itertools.repeat(upload),
            itertools.repeat(cleanup)
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
        print('Fetching from reddit: ', args.subreddit, 'start:', start, 'end:', end)
        if args.workers > 1:
            print(args.subreddit, start, end, args.n_comments, args.upload,
            args.cleanup, args.workers)
            fetch_submissions_async(
                args.subreddit, start, end, args.n_comments, args.upload,
                args.cleanup, args.workers
            )
        else:
            fetch_submissions(
                args.subreddit, start, end, args.n_comments, args.upload,
                args.cleanup
            )

    elif action == 'download':
        print('Downloading from S3: ', args.subreddit)
        download_from_s3(args.subreddit, start)

    else:
        raise Exception("Action {:s} not supported!".format(action))
