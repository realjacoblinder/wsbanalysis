import requests
import json
import datetime
import time
from os import path
from os import scandir
import sys
# same as post-collection file, slightly modified to get ALL posts, and not drop based on flair. 
# all info stored the same way in a new dir, so data can be constructed and manipulated with the same scripts
after_time = datetime.datetime(2019, 10, 1, 0, 0).timestamp()
after_time = int(after_time)
stop_time = int(time.time())

max_time = 0
iteration = 0 # for some reason two pulls sometimes had the same timestamped filename, used this to make sure no overwrites
empty_quit = 0

if path.exists('all_maxTime.txt'):
    with open('all_maxTime.txt', 'r') as f:
        max_time = int(f.read())
        after_time = after_time + (max_time - after_time)
    for file in scandir('all_post_data'):
        iteration += 1

while after_time <= stop_time:
    all_posts = requests.get('https://api.pushshift.io/reddit/submission/search/?after={}&sort_type=created_utc&sort=asc&subreddit=wallstreetbets&size=150'.format(after_time))
    try:
        data = all_posts.json()
    except:
        print('JSON Error, try again.')
        time.sleep(2)
        continue
    for post_dict in data['data']:
        if post_dict['created_utc'] > max_time: # keeping track of the time
            max_time = post_dict['created_utc']
    
    if not data['data']:
        empty_quit += 1
        print('Data empty, quit on 5. Current: ' + str(empty_quit))
        if empty_quit == 5: # just quit on 5 empty returns, to try again later
            sys.exit()
        time.sleep(2)
        continue

    after_time = after_time + (max_time - after_time)

    time.sleep(2)  # not including this got us shutdown by the API

    filename = str(iteration) + '.json'
    with open('all_post_data/'+filename, 'w') as f:
        json.dump(data['data'], f)
    with open('all_maxTime.txt', 'w') as timefile:
        timefile.write(str(max_time))
    print(str(iteration) + ' ' + str(datetime.datetime.fromtimestamp(max_time)) + ', stop_time is ' + str(datetime.datetime.fromtimestamp(stop_time)))
    empty_quit = 0 # reset the quit count per pull
    iteration += 1