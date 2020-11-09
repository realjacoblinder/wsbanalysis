import json
import os
from tqdm import tqdm
import pandas as pd

def convert_to_est(gmt_timestamp):
	return int(gmt_timestamp)-(60*60*5)
	


i = 0

for file in tqdm(os.scandir('post_data')):
    with open(file.path, 'r') as f:
        if i == 0:
            data = json.load(f)
        else:
            data = data + json.load(f)
    i += 1
export = pd.DataFrame(data)
export['created_utc'] = export['created_utc'].apply(convert_to_est)
to_keep = ['author', 'created_utc', 'title', 'link_flair_text','selftext']
export = export[to_keep]
export.to_csv('all_good_posts.csv')