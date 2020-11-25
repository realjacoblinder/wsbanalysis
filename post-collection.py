import requests
import json
import datetime
import time
from os import path
from os import scandir

# should we want to go further back than 10/1/2019, we move the current after_time to stop time, and create a new after_time
# to define the new date range. Keeping track of ranges is a manual task, unless dropping duplicates later is ok (seems silly though)

# I admit, going forward in time is a little confusing, but I think it leaves the script more flexible down the line. 

after_time = datetime.datetime(2019, 10, 1, 0, 0).timestamp()
after_time = int(after_time)
stop_time = int(time.time())

# flairs we decided to actually use, the rest are just dropped
good_flairs = ['DD', 'Options', 'Stocks', 'Fundamentals', 'Technicals', 'YOLO', 'Discussion']

iteration = 0 # file name initialization
max_time = 0 # part of date tracking and iterating

if path.exists('maxTime.txt'): # if this exists, its not the scripts first rodeo, so we gather up its last stop point
    with open('maxTime.txt', 'r') as f:
        max_time = int(f.read())
        after_time = after_time + (max_time - after_time) # no need to pull posts we've already pulled on restart, brings after_time to date
    for file in scandir('post_data'): # brings our current file name up to speed
        iteration += 1

while after_time <= stop_time: # decided to pick a time and move forward from there, easy enough to defined a new time range to get older
    all_posts = requests.get('https://api.pushshift.io/reddit/submission/search/?after={}&sort_type=created_utc&sort=asc&subreddit=wallstreetbets&size=150'.format(after_time))
    try:
        data = all_posts.json()
    except: # ocassional errors on read, nothing to do with us (I think). Just try again in this case. 
        print('JSON Error, try again.')
        time.sleep(2)
        continue
    good_posts = [] # these are the posts we'll keep
    for post_dict in data['data']:
        try:
            post_dict['link_flair_text'] # a crude way of checking for the key before I realized there are better ways
        except KeyError:
            continue
        if post_dict['link_flair_text'] in good_flairs:
            good_posts.append(post_dict)
            if post_dict['created_utc'] > max_time:
                max_time = post_dict['created_utc']
    if good_posts: # if we have worthwhile posts
        # recalculate new time to get next 100 posts
        after_time = after_time + (max_time - after_time)

        filename = str(iteration) + '.json'
        with open('post_data/'+filename, 'w') as f:
            json.dump(good_posts, f)
        with open('maxTime.txt', 'w') as timefile: # only write time if succesful write of data
            timefile.write(str(max_time))
        # the prints were just to make sure things were going well while it ran
        print(str(iteration) + ' ' + str(datetime.datetime.fromtimestamp(max_time)) + ', stop_time is ' + str(datetime.datetime.fromtimestamp(stop_time)))
        iteration += 1
        time.sleep(2)  # not including this got us shutdown by the API
    else: # if there were no good posts 
        max_time += 30
        with open('maxTime.txt', 'w') as timefile:
            timefile.write(str(max_time))
        # recalculate because got no posts
        after_time = after_time + (max_time - after_time)
        print("No posts, adding thirty seconds.... max_time is " + str(datetime.datetime.fromtimestamp(max_time)) + ', stop_time is ' + str(datetime.datetime.fromtimestamp(stop_time)))
        time.sleep(1)  # not including this got us shutdown by the API
