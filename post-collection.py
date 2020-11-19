import requests
import json
import datetime
import time
from os import path
from os import scandir

after_time = datetime.datetime(2019, 10, 1, 0, 0).timestamp()
after_time = int(after_time)
stop_time = int(time.time())

good_flairs = ['DD', 'Options', 'Stocks', 'Fundamentals', 'Technicals', 'YOLO', 'Discussion']

iteration = 0
max_time = 0

if path.exists('maxTime.txt'):
    with open('maxTime.txt', 'r') as f:
        max_time = int(f.read())
        after_time = after_time + (max_time - after_time)
    for file in scandir('post_data'):
        iteration += 1

while after_time <= stop_time:
    all_posts = requests.get('https://api.pushshift.io/reddit/submission/search/?after={}&sort_type=created_utc&sort=asc&subreddit=wallstreetbets&size=150'.format(after_time))
    try:
        data = all_posts.json()
    except:
        print('JSON Error, try again.')
        time.sleep(2)
        continue
    good_posts = []
    for post_dict in data['data']:
        try:
            post_dict['link_flair_text']
        except KeyError:
            continue
        if post_dict['link_flair_text'] in good_flairs:
            good_posts.append(post_dict)
            if post_dict['created_utc'] > max_time:
                max_time = post_dict['created_utc']
    if good_posts:
        # recalculate new time to get next 100 posts
        after_time = after_time + (max_time - after_time)

        filename = str(iteration) + '.json'
        with open('post_data/'+filename, 'w') as f:
            json.dump(good_posts, f)
        with open('maxTime.txt', 'w') as timefile:
            timefile.write(str(max_time))
        print(str(iteration) + ' ' + str(datetime.datetime.fromtimestamp(max_time)) + ', stop_time is ' + str(datetime.datetime.fromtimestamp(stop_time)))
        iteration += 1
        time.sleep(2)  # not including this got us shutdown by the API
    else:
        max_time += 30
        with open('maxTime.txt', 'w') as timefile:
            timefile.write(str(max_time))
        # recalculate because got no posts
        after_time = after_time + (max_time - after_time)
        print("No posts, adding thirty seconds.... max_time is " + str(datetime.datetime.fromtimestamp(max_time)) + ', stop_time is ' + str(datetime.datetime.fromtimestamp(stop_time)))
        time.sleep(1)  # not including this got us shutdown by the API
