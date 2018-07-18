from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import praw
import prawcore
import re
import config as cfg

LOG_MSG = "Checking for new Eden's Zero chapter in /r/{} at " + str(datetime.now())
SERVER_ERROR = "Error with searching for a new Eden's Zero chapter in /r/{}"

GITHUB_LINK = 'https://github.com/abhinavk99/edens-zero-friend-bot'
PM_LINK = 'https://www.reddit.com/message/compose/?to=edenszerofriendbot'
FOOTER = '---\n^^[source]({}) ^^on ^^github, ^^[message]({}) ^^the ^^bot ^^for ^^any ^^questions'.format(GITHUB_LINK, PM_LINK)

reddit = praw.Reddit(client_id=cfg.reddit_id,
                     client_secret=cfg.reddit_secret,
                     password=cfg.reddit_password,
                     user_agent=cfg.reddit_user_agent,
                     username=cfg.reddit_username)

sched = BlockingScheduler()

chapters_info = {}

def read_chapters_file():
    with open('chapters.txt') as f:
        for line in f:
            tokens = line.split()
            chapters_info[int(tokens[0])] = int(tokens[1])

def write_chapters_file():
    with open('chapters.txt', 'w') as f:
        for key in sorted(chapters_info.keys()):
            f.write('{} {}\n'.format(key, chapters_info[key]))


def scan_chapter(link):
    # TODO
    pass

def post_comment(submission):
    # TODO
    pass

def get_chapter_number(title):
    match_obj = re.search(r'chapter (\d+)', title)
    if match_obj is not None:
        chapter_number = int(match_obj.groups()[0])
        print(chapter_number)
        if chapter_number not in chapters_info:
            return chapter_number
    return None

def format_title(title):
    print(title)
    return title.lower()

def is_new_submission(submission):
    return submission not in reddit.user.me().new(limit = 5)

def analyze_submission(submission, title):
    chapter_number = get_chapter_number(title)
    if chapter_number is not None and is_new_submission(submission):
        scan_chapter(submission.url)
        post_comment(submission)
        write_chapters_file()

@sched.scheduled_job('interval', seconds=600)
def search_in_manga():
    print(LOG_MSG.format('manga'))
    try:
        for submission in reddit.subreddit('manga').search("Eden's Zero", sort='new', time_filter='day'):
            title = format_title(submission.title)
            if '[disc]' in title:
                analyze_submission(submission, title)
    except prawcore.exceptions.ServerError:
        print(SERVER_ERROR.format('manga'))

@sched.scheduled_job('interval', seconds=600)
def search_in_edens_zero():
    print(LOG_MSG.format('EdensZero'))
    try:
        for submission in reddit.subreddit('EdensZero').search("Chapter", sort='new', time_filter='day'):
            title = format_title(submission.title)
            if 'links + discussion' in title:
                analyze_submission(submission, title)
    except prawcore.exceptions.ServerError:
        print(SERVER_ERROR.format('EdensZero'))

read_chapters_file()
search_in_manga()
search_in_edens_zero()
sched.start()
