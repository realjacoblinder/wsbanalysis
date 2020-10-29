import requests
import json
import time
import datetime
from os import path


def get_comment_ids(author, before, sort='desc', sort_type='created_utc', size=100):
    if before:
        r_params = 'author={}&before={}&sort={}&sort_type={}&size={}'.format(author, before, sort, sort_type, size)
    else:
        r_params = 'author={}&sort={}&sort_type={}&size={}'.format(author, sort, sort_type, size)
    print(r_params)
    r = requests.get("https://api.pushshift.io/reddit/comment/search/?" + r_params)
    data = r.json()
    return data['data']


def get_comments_by_id(id_batch):
    r_params = ','.join(id for id in id_batch)
    r = requests.get('https://api.pushshift.io/reddit/comment/search?ids={}'.format(r_params))
    data = r.json()
    return data['data']


def get_comments_from_reddit_api(comment_ids,author):
    headers = {'User-agent':'Comment Collector for /u/{}'.format(author)}
    params = {}
    params['id'] = ','.join(["t1_" + id for id in comment_ids])
    r = requests.get("https://api.reddit.com/api/info",params=params,headers=headers)
    data = r.json()
    return data['data']['children']


before = None
if path.exists('before_time.txt'):
    with open('before_time.txt', 'r') as f:
        before = int(f.read())

### IMPORTANT ######################
# Set this variable to your username
author = "pickbot"
####################################
iteration = 0
while True:
    comments = get_comment_ids(author=author, size=100, before=before, sort='desc', sort_type='created_utc')
    if not comments:
        print('Empty comments returned, last BEFORE is {}'.format(filename))
        break

    # This will get the comment ids from Pushshift in batches of 100 -- Reddit's API only allows 100 at a time
    comment_ids = []
    for comment in comments:
        if before is None or before > comment['created_utc']:
            before = comment['created_utc']  # This will keep track of your position for the next call in the while loop
        comment_ids.append(comment['id'])

    time.sleep(2)

    # comments = get_comments_by_id(comment_ids)
    results = []
    comments = get_comments_from_reddit_api(comment_ids, author)
    for comment in comments:
        comment = comment['data']
        results.append(comment)
    filename = str(iteration) + '.json'
    with open('{}_comments/{}'.format(author, filename), 'w') as f:
        json.dump(results, f)
    with open('before_time.txt', 'w') as f:
        f.write(str(before))
    print(str(iteration) + '\t' + filename)
    iteration += 1
