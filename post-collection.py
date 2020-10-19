import requests
import json
import datetime
import time
# import re
# import pandas as pd
# import yfinance as yf

after_time = datetime.datetime(2019, 10, 1, 0, 0).timestamp()
after_time = int(after_time)
stop_time = int(datetime.datetime(2020, 10, 18, 0, 0).timestamp())

all_posts = requests.get(
    'https://api.pushshift.io/reddit/submission/search/?after={}&sort_type=created_utc&sort=asc&subreddit=wallstreetbets&size=150'.format(
        after_time))
data = all_posts.json()

good_flairs = ['DD', 'Options', 'Stocks', 'Fundamentals', 'Technicals', 'YOLO', 'Discussion']
good_posts = []
max_time = 0

while after_time <= stop_time:
    all_posts = requests.get(
        'https://api.pushshift.io/reddit/submission/search/?after={}&sort_type=created_utc&sort=asc&subreddit=wallstreetbets&size=150'.format(
            after_time))
    data = all_posts.json()
    for post_dict in data['data']:
        try:
            post_dict['link_flair_text']
        except KeyError:
            continue
        if post_dict['link_flair_text'] in good_flairs:
            good_posts.append(post_dict)
            if post_dict['created_utc'] > max_time:
                max_time = post_dict['created_utc']
    # recalculate new time to get next 100 posts
    after_time = after_time + (max_time - after_time)
    time.sleep(2)  # not including this got us shutdown by the API

    filename = str(datetime.datetime.fromtimestamp(max_time).month) + '.' + \
               str(datetime.datetime.fromtimestamp(max_time).year) + '.' + \
               str(datetime.datetime.fromtimestamp(max_time).hour) + '.' + \
               str(datetime.datetime.fromtimestamp(max_time).minute)+'.json'
    with open('post_data/'+filename, 'w') as f:
        json.dump(good_posts, f)
    with open('maxTime.txt', 'w') as timefile:
        timefile.write(str(max_time))
    print(filename)
