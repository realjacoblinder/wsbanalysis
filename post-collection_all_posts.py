import requests
import json
import datetime
import time
from os import path

after_time = datetime.datetime(2019, 10, 1, 0, 0).timestamp()
after_time = int(after_time)
stop_time = int(datetime.datetime(2020, 10, 26, 0, 0).timestamp())

good_posts = []

max_time = 0

if path.exists('maxTime.txt'):
    with open('maxTime.txt', 'r') as f:
        max_time = int(f.read())
        after_time = after_time + (max_time - after_time)
iteration = 0.000 # for some reason two pulls sometimes had the same timestamped filename, used this to make sure no overwrites
while after_time <= stop_time:
    all_posts = requests.get('https://api.pushshift.io/reddit/submission/search/?after={}&sort_type=created_utc&sort=asc&subreddit=wallstreetbets&size=150'.format(after_time))
    data = all_posts.json()
    for post_dict in data['data']:
        good_posts.append(post_dict)
        if post_dict['created_utc'] > max_time:
            max_time = post_dict['created_utc']
        if good_posts:
            # recalculate new time to get next 100 posts
            after_time = after_time + (max_time - after_time)

            time.sleep(2)  # not including this got us shutdown by the API

            filename = str(iteration) + '.json'
            with open('all_post_data/'+filename, 'w') as f:
                json.dump(good_posts, f)
            with open('all_maxTime.txt', 'w') as timefile:
                timefile.write(str(max_time))
            print(str(iteration) + ' ' + str(datetime.datetime.fromtimestamp(max_time)))
            good_posts = []
        else:
            max_time += 30
            # recalculate because got no posts
            after_time = after_time + (max_time - after_time)
            print("No posts, adding thirty seconds...")
            time.sleep(2)  # not including this got us shutdown by the API
        iteration = round(iteration + 0.001,3)

