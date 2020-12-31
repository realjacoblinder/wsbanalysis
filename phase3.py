#!/usr/bin/env python
# coding: utf-8

import json
import os
from tqdm import tqdm
import pandas as pd
import re
import numpy as np
import datetime
import dateutil.parser as dp
from dateutil.relativedelta import relativedelta

from nltk.corpus import stopwords
from nltk import FreqDist
import collections
import string

def ticker_extender(pos_list):
    prev_ticker = "NONE"
    for group in pos_list:
        if not group[0]:
            group[0] = prev_ticker
        else:
            prev_ticker = group[0]
    return pos_list


def regex_pos(post_text):
    if pd.isna(post_text): return 0
    x = []
    p1 = re.compile(r'((?:\$?[A-Z]{1,4})(?:[a-z]{1,3})?)?\s+\$?(?:(\d+(?:\.\d\d?)?)\s*([CcPp])\w{0,4}\s+(\d\d?\/\d\d?(?:\/\d{2,4})?))')
    p2 = re.compile(r'((?:\$?[A-Z]{1,4})(?:[a-z]{1,3})?)?\s+(\d\d?\/\d\d?(?:\/\d{2,4})?)\s+\$?(\d+(?:\.\d\d?)?)\s*([CcPp])\w{0,4}')
    p3 = re.compile(r'(\d\d?\/\d\d?(?:\/\d{2,4})?)\s+((?:\$?[A-Z]{1,4})(?:[a-z]{1,3})?)\s+\$?(\d+(?:\.\d\d?)?)\s*([CcPp])\w{0,4}')
    p4 = re.compile(r'((?:\$?[A-Z]{1,4})(?:[a-z]{1,3})?)?\s+(\d{1,2}\s?[A-Z]{1,3})\s+\$?(\d+(?:\.\d\d?)?)\s*([CcPp])\w{0,4}')
    p5 = re.compile(r'(\d{1,2}\s?[A-Z]{1,3})\s+((?:\$?[A-Z]{1,4})(?:[a-z]{1,3})?)?\s+\$?(\d+(?:\.\d\d?)?)\s*([CcPp])\w{0,4}')
    p6 = re.compile(r'([A-Z]{1,3}\s?\d{1,2})\s+((?:\$?[A-Z]{1,4})(?:[a-z]{1,3})?)?\s+\$?(\d+(?:\.\d\d?)?)\s*([CcPp])\w{0,4}')
    p7 = re.compile(r'((?:\$?[A-Z]{1,4})(?:[a-z]{1,3})?)?\s+([A-Z]{1,3}\s?\d{1,2})\s+\$?(\d+(?:\.\d\d?)?)\s*([CcPp])\w{0,4}')
    
    # original ticker: (\$?[A-Z]{1,4})
    # alt ticker: ((?:\$?[A-Z]{1,4})(?:[a-z]{1,3})?)
    
    x1 = re.findall(p1, post_text)
    x2 = re.findall(p2, post_text)
    x3 = re.findall(p3, post_text)
    x4 = re.findall(p4, post_text) # diving into alpha-numeric dates like 20 NOV
    x5 = re.findall(p5, post_text) #alpha 20 nov, date first
    x6 = re.findall(p6, post_text) #alpha nov 20, date first
    x7 = re.findall(p7, post_text) #alpha nov 20, ticker first
    
    #dictating ticker-strike-c/p-date as standard. x1 stays, the rest must be edited 
    if x1:
        x1_e = []
        for match in x1:
            ordered = [match[0].upper(), match[1], match[2], match[3]]
            x1_e.append(ordered)
        x.extend(x1_e)
    if x2: #ticker-date-strike-c/p
        x2_e = []
        for match in x2:
            ordered = [match[0].upper(),match[2],match[3],match[1]]
            x2_e.append(ordered)
        x.extend(x2_e)
    if x3: #date-ticker-strike-c/p
        x3_e = []
        for match in x3:
            ordered = [match[1].upper(),match[2],match[3],match[0]]
            x3_e.append(ordered)
        x.extend(x3_e)
    if x4: # ticker-date(alphanumeric)-stike-c/p
        x4_e = []
        for match in x4:
            ordered = [match[0].upper(),match[2],match[3],match[1]]
            x4_e.append(ordered)
        x.extend(x4_e)
    if x5: #date(alpha)-ticker-strike-cp
        x5_e = []
        for match in x5:
            ordered = [match[1].upper(),match[2],match[3],match[0]]
            x5_e.append(ordered)
        x.extend(x5_e)
    if x6: #same as above, diff alpha
        x6_e = []
        for match in x6:
            ordered = [match[1].upper(),match[2],match[3],match[0]]
            x6_e.append(ordered)
        x.extend(x6_e)
    if x7:
        x7_e = []
        for match in x7:
            ordered = [match[0].upper(),match[2],match[3],match[1]]
            x7_e.append(ordered)
        x.extend(x7_e)

    if x:
        x = ticker_extender(x) # see above
        return x 
    else:
        return 0


# adds -1 to unproccessed dates, these are worth dropping
def date_proccessor(pos_list):
    if pos_list == 0: return pos_list
    new_list = pos_list
    for position in new_list:
        date = position[-1]
        try:
            p_date = dp.parse(date)
        except:
            try:
                date_e = date.split('/')
                if len(date_e) == 2:
                    date_e = '/'.join(i for i in date_e[::-1])
                elif len(date_e) == 3:
                    tmp = date_e[0]
                    date_e[0] = date_e[1]
                    date_e[1] = tmp
                    date_e = '/'.join(i for i in date_e[::-1])
                p_date = dp.parse(date_e)                
            except:
                #print("date parse error, probably worth dropping")
                #print(date)
                p_date = -1
        position[-1] = p_date
    return new_list
# hanndled the -1 entries for dates. if no positions left, drops the entire entry
def date_proccessor_corrector(pos_list):
    if pos_list == 0: return pos_list
    new_list = []
    for position in pos_list:
        if position[-1] != -1:
            new_list.append(position)
    if new_list:
        return new_list
    else:
        return 0


# get the created year, compare to expiry
# make adjustments as needed
# return
#initial comparison made to current because all posts with no year originally have current year added to them
#   as part of pre-processing
def expiry_year_corrector(row):
    post_date = int(row['created_utc'])
    post_date = datetime.datetime.fromtimestamp(post_date)
    combined = row['regexed_combined']
    if combined == 0: return combined
    current_year = datetime.datetime.now().year
    for position in combined:
        expiry = position[3]
        expiry_year = expiry.year
        expiry_month = expiry.month
        post_year = post_date.year
        post_month = post_date.month
        
        if expiry_year > current_year: 
            expiry = expiry.timestamp()
            continue # continue to other positions in post
            #return combined # no changes needed
        
        if expiry_month >= post_month: # expiry month is greater than month, is POST year
            expiry = datetime.datetime(post_year,expiry.month,expiry.day)
        elif expiry_month < post_month: # expiry month is less than post month, is POST year + 1
            expiry = datetime.datetime(post_year+1,expiry.month,expiry.day)
        position[3] = expiry
    #print(combined)
    return combined


def ticker_finder(row):
    if row['regexed_combined'] == 0:
        return 0
    if type(row['selftext']) == float:
        return 0 
    if row['regexed_combined'][0][0] != 'NONE':
        return 1
    lookup_string = row['title'] + ' ' + row['selftext']
    tickers = check_tickers(clean_post(lookup_string))
    the_goods = tickers.most_common(1)
    if the_goods:
        return the_goods
    else:
        return -1

def clean_post(post_text):
    translator = str.maketrans('', '', string.punctuation) # for removing punctuation
    post_text = post_text.translate(translator)
    token_text = [t for t in post_text.replace('\n',' ').split()]
    
    sr = stopwords.words('english')
    sr.extend(['gay', 'bear', 'girlfriend', 'bull'])
    cleanTokens = [i for i in token_text if i not in sr]
    
    return cleanTokens

def check_tickers(tokens):
    nasdaq = pd.read_csv('tickers/nasdaq.csv')
    nyse = pd.read_csv('tickers/nyse.csv')
    ticker_counter = collections.Counter()
    for token in tokens:
        if any(nasdaq['Symbol'].isin([token])): 
            ticker_counter[token] += 1
            #print(token)
        if any(nyse['Symbol'].isin([token])): 
            ticker_counter[token] += 1
            #print(token)
    return ticker_counter


def add_missing_tickers(row):
    # rows with no regex
    if row['regexed_combined'] == 0: return row['regexed_combined']
    # if there are no missing tickers
    if row['regexed_combined'][0][0] != "NONE": return row['regexed_combined']
    # if there are missing tickers
    for position in row['regexed_combined']:
        if position[0] == "NONE" and not (type(row['ticker_locator']) == int):
            position[0] = row['ticker_locator'][0][0] # adds in ticker of most common ticker mentioned - best guess
    return row['regexed_combined']