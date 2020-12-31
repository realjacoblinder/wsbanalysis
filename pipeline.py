import requests
import json
import datetime
import time
from os import path
from os import scandir
from os import getenv
import pandas as pd
import phase3
import phase4

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.types import Integer, Text, String, DateTime, Float

script_start = datetime.datetime.today()

## make sure sql works and is good to go first
load_dotenv()

DB_PASS = getenv("DB_PASS")
DB_USER = getenv("DB_USER")
DB_HOST = getenv("DB_HOST")

engine = create_engine(f"mysql://{DB_USER}:{DB_PASS}@{DB_HOST}/wsb")
conn = engine.connect()

# should we want to go further back than 10/1/2019, we move the current after_time to stop time, and create a new after_time
# to define the new date range. Keeping track of ranges is a manual task, unless dropping duplicates later is ok (seems silly though)

# I admit, going forward in time is a little confusing, but I think it leaves the script more flexible down the line. 

after_time = datetime.datetime(2019, 10, 1, 0, 0).timestamp()
after_time = int(after_time)
stop_time = int(time.time())

# flairs we decided to actually use, the rest are just dropped
good_flairs = ['DD', 'Options', 'Stocks', 'Fundamentals', 'Technicals', 'YOLO', 'Discussion']

max_time = 0 # part of date tracking and iterating

df = pd.DataFrame()

if path.exists('maxTime.txt'): # if this exists, its not the scripts first rodeo, so we gather up its last stop point
    with open('maxTime.txt', 'r') as f:
        max_time = int(f.read())
        after_time = after_time + (max_time - after_time) # no need to pull posts we've already pulled on restart, brings after_time to date

# first step is to scrape for new posts from a certain point in time to the current time. 

while after_time <= stop_time: # decided to pick a time and move forward from there, easy enough to defined a new time range to get older
    all_posts = requests.get('https://api.pushshift.io/reddit/submission/search/?after={}&sort_type=created_utc&sort=asc&subreddit=wallstreetbets&size=150'.format(after_time))
    try:
        data = all_posts.json()
    except: # ocassional errors on read, nothing to do with us (I think). Just try again in this case. 
        time.sleep(2)
        continue
    df = pd.DataFrame(columns=['author', 'created_utc', 'selftext', 'title', 'flair']) # these are the posts we'll keep
    for post_dict in data['data']:
        if not all(i in post_dict for i in ['author', 'created_utc', 'selftext', 'title']):
            continue
        if 'link_flair_text' in post_dict:
            flair = post_dict['link_flair_text']
        else:
            flair = 'NONE'
        new_row = {'author':post_dict['author'], 'created_utc':post_dict['created_utc'], 'selftext':post_dict['selftext'], 'title':post_dict['title'], 'flair':flair}
        df = df.append(new_row, ignore_index=True)
        if post_dict['created_utc'] > max_time:
            max_time = post_dict['created_utc']
    if not df.empty: # if we have worthwhile posts
        # recalculate new time to get next 100 posts
        after_time = after_time + (max_time - after_time)
        time.sleep(1)  # not including this got us shutdown by the API
    else: # if there were no good posts 
        max_time += 30
        with open('maxTime.txt', 'w') as timefile:
            timefile.write(str(max_time))
        # recalculate because got no posts
        after_time = after_time + (max_time - after_time)
        time.sleep(1)  # not including this got us shutdown by the API
        continue

    # Second step is to process the data that comes in. 
    # 2a is to add all the position data using regular expressions, falling back to basic text analysis when needed
    # 2b is breaking out the positions into a new dataframe, dropping all uneeded post info, and adding in equity open and close prices

    df['all text'] = df['title'] + df['selftext']
    df['regexed_combined'] = df['all text'].apply(phase3.regex_pos)
    df['regexed_combined'] = df['regexed_combined'].apply(phase3.date_proccessor)
    df['regexed_combined'] = df['regexed_combined'].apply(phase3.date_proccessor_corrector)
    df['regexed_combined'] = df.apply(phase3.expiry_year_corrector, axis = 1)
    df['ticker_locator'] = 0 # needed to create the col before running the below. I have a lot to learn. 
    df['ticker_locator'] = df.apply(phase3.ticker_finder, axis = 1)
    df.apply(phase3.add_missing_tickers, axis = 1) # should be in place. function directly makes changes to columns
    df = df[df['regexed_combined'] != 0] 
    # in original left this data, but for the pipeline it needs to go ASAP
    
    new_df = pd.DataFrame(columns=['position', 'post_date', 'author', 'flair'])
    for index,row in df.iterrows():
        author = row['author']
        flair = row['flair']
        post_date = row['created_utc']
        post_date = phase4.convert_to_est(post_date)
        for position in row['regexed_combined']:
            new_row = {'position':position, 'post_date': post_date, 'author':author, 'flair':flair}
            new_df = new_df.append(new_row, ignore_index=True)

    new_df['ticka'] = new_df['position'].apply(lambda x: x[0])
    new_df['strike'] = new_df['position'].apply(lambda x: x[1])
    new_df['contract'] = new_df['position'].apply(lambda x: x[2])
    new_df['expiry'] = new_df['position'].apply(lambda x: x[3]) # the timestamps are way too long

    new_df = new_df[new_df['ticka'] != 'NONE']
    new_df['ticka'] = new_df['ticka'].apply(lambda x: x[1:] if x.startswith('$') else x)
    # specific ticker changes where yahoo_fin is dumb
    new_df['ticka'] = new_df['ticka'].apply(lambda x: '^VIX' if x == 'VIX' else x)

    # drop original position lists
    new_df.drop(columns=['position'], inplace=True)
    new_df.drop_duplicates(inplace=True)

    new_df['post_date'] = new_df['post_date'].apply(datetime.datetime.fromtimestamp)

    # fill open price of equity on posting date
    new_df['open_price'] = 0
    new_df['open_price'] = new_df.apply(phase4.fill_open, axis = 1)
    new_df = new_df[new_df['open_price'] != -1]

    # mark close prices to be pulled later, but still make an attempt to fill now.
    new_df['close_price'] = 0
    new_df['close_price'] = new_df.apply(phase4.fill_close, axis = 1)

    # add to sql database
    table_name = 'positions'

    new_df.to_sql(
        table_name,
        conn,
        if_exists='append',
        index=False,
        dtype={
            'ticka':String(10),
            'author':String(20),
            'flair':String(10),
            'strike':Float,
            'contract':Text,
            'expiry':DateTime,
            'post_date':DateTime,
            'open_price':Float,
            'close_price':Float
        }
    )
    print(f"Saved {len(new_df)} posistions to database...")
    with open('maxTime.txt', 'w') as timefile: # only write time if succesful write of data
            timefile.write(str(max_time))

script_end = datetime.datetime.today()

with open('wsb_scraper.log', 'a') as f:
    f.write(f"Script ran from {script_start} to {script_end}\n")