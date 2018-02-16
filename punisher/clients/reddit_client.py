import codecs
import heapq
import json
from pathlib import Path

import praw

import punisher.config as cfg
import punisher.constants as c
from punisher.utils.dates import utc_to_epoch, epoch_to_utc
from punisher.utils.encoders import JSONEncoder


# Docs
# http://praw.readthedocs.io/en/latest/tutorials/comments.html
REDDIT = 'reddit'
REDDIT_DIR = Path(cfg.DATA_DIR, REDDIT)
REDDIT_DIR.mkdir(exist_ok=True)

def get_subreddit_fname(subreddit, date):
    fname = '{:s}_{:d}_{:d}_{:d}.json'.format(
        subreddit.lower(), date.year, date.month, date.day
    )
    return fname

def get_subreddit_fpath(subreddit, date, dirname=REDDIT_DIR):
    fname = get_subreddit_fname(subreddit, date)
    subreddit_dir = Path(dirname, subreddit.lower())
    subreddit_dir.mkdir(exist_ok=True)
    return Path(subreddit_dir, fname)

def save_submissions(submissions, subreddit, date):
    fpath = get_subreddit_fpath(subreddit, date)
    f = open(fpath, 'w')
    json.dump(submissions, f, cls=JSONEncoder)
    f.close()

def load_submissions(subreddit, date):
    fpath = get_subreddit_fpath(subreddit, date)
    with codecs.open(fpath, 'r', 'utf-8') as f:
        tweets = json.load(f, encoding='utf-8')
    return tweets

def get_client():
    return praw.Reddit(
        client_id=cfg.REDDIT_CLIENT_ID,
        client_secret=cfg.REDDIT_SECRET_KEY,
        user_agent=cfg.REDDIT_USER_AGENT
    )

def get_subreddit(name):
    return get_client().subreddit(name)

def get_submission(sub_id, sort_by='top'):
    submission = get_client().submission(id=sub_id)
    submission.comment_sort = sort_by
    submission.comments.replace_more(limit=0)
    return submission

def get_submissions(subreddit_name, start, end, top_n_comments):
    submissions = []
    subreddit = get_subreddit(subreddit_name)
    subs = subreddit.submissions(
        start=utc_to_epoch(start),
        end=utc_to_epoch(end)
    )
    for sub in subs:
        comments = get_top_n_comments(sub, top_n_comments)
        submissions.append({
            'id': sub.id,
            'subreddit': sub.subreddit.display_name.lower(),
            'author': '' if sub.author is None else sub.author.name,
            'created_utc': sub.created_utc,
            'external_url': sub.url,
            'title': sub.title,
            'n_comments': sub.num_comments,
            'body': sub.selftext,
            'score': sub.score,
            'ups': sub.ups,
            'downs': sub.downs,
            'view_count': sub.view_count,
            'comments': comments,
        })
    return submissions

def get_top_n_comments(submission, n):
    comments = []
    submission.comment_sort = 'top' # unnecessary
    submission.comments.replace_more(limit=0)
    for comment in submission.comments.list():
        comments.append({
            'id': comment.id,
            'subreddit': comment.subreddit.display_name.lower(),
            'submission_id': comment.submission.id,
            'body': comment.body,
            'author': '' if comment.author is None else comment.author.name,
            'created_utc': comment.created_utc,
            'score': comment.score,
            'ups': comment.ups,
            'downs': comment.downs,
        })
    return heapq.nlargest(n, comments, key=lambda s: s['score'])

def filter_comments(comments):
    pass

def filter_submissions(submissions):
    pass

# Streaming
# http://praw.readthedocs.io/en/latest/code_overview/other/subredditstream.html?highlight=historical
