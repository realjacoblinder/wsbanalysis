import json
import os
from tqdm import tqdm
import pandas as pd

def convert_to_est(gmt_timestamp):
	return int(gmt_timestamp)-(60*60*5)
	
# file for compiling all of the json files into one large csv. this crashed my rasp-pi, which was fun. 
# this file is specfic to compiling the "good" posts. maybe one day we'll grduate to command line arguments. 
# i also drop some columns here, just to keep the size down. I don't need ever single col for the final set. 

i = 0

for file in tqdm(os.scandir('post_data')):
    with open(file.path, 'r') as f:
        if i == 0:
            data = json.load(f)
        else:
            data = data + json.load(f)
    i += 1
print('Creating dataframe....')
export = pd.DataFrame(data)
print("Converting times to EST....")
export['created_utc'] = export['created_utc'].apply(convert_to_est)
print('Dropping columns....')
to_keep = ['author', 'created_utc', 'title', 'link_flair_text','selftext', 'id', 'full_link']
export = export[to_keep]
print('Saving csv....')
export.to_csv('all_good_posts.csv')