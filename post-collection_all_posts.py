import requests
import json
import datetime
import time
from os import path

after_time = datetime.datetime(2019, 10, 1, 0, 0).timestamp()
after_time = int(after_time)
stop_time = int(datetime.datetime(2020, 10, 26, 0, 0).timestamp())

max_time = 0

if path.exists('all_maxTime.txt'):
    with open('all_maxTime.txt', 'r') as f:
        max_time = int(f.read())
        after_time = after_time + (max_time - after_time)
iteration = 0 # for some reason two pulls sometimes had the same timestamped filename, used this to make sure no overwrites

while after_time <= stop_time:
    all_posts = requests.get('https://api.pushshift.io/reddit/submission/search/?after={}&sort_type=created_utc&sort=asc&subreddit=wallstreetbets&size=150'.format(after_time))
    try:
        data = all_posts.json()
    except:
        print('JSON Error, try again.')
        time.sleep(2)
        continue
    for post_dict in data['data']:
        if post_dict['created_utc'] > max_time:
            max_time = post_dict['created_utc']
        
    after_time = after_time + (max_time - after_time)

    time.sleep(2)  # not including this got us shutdown by the API

    filename = str(iteration) + '.json'
    with open('all_post_data/'+filename, 'w') as f:
        json.dump(data['data'], f)
    with open('all_maxTime.txt', 'w') as timefile:
        timefile.write(str(max_time))
    print(str(iteration) + ' ' + str(datetime.datetime.fromtimestamp(max_time)))
    
    iteration += 1