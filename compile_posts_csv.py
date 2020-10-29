import json
import os
from tqdm import tqdm
import pandas as pd

i = 0

for file in tqdm(os.scandir('post_data')):
    with open(file.path, 'r') as f:
        if i == 0:
            data = json.load(f)
        else:
            data = data + json.load(f)
    i += 1
export = pd.DataFrame(data)
to_keep = ['author', 'created_utc', 'title', 'link_flair_text','selftext']
export = export[to_keep]
export.to_csv('all_good_posts.csv')