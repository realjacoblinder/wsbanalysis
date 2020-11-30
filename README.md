# DSCI 511 r/wallstreetbets adventure

## The Scraper(s)

This project is broken into two main branches at the beginning: the 'good posts' and 'all posts'. Good posts are posts flaired with what is considered to be a good flair, likely to have a worthwhile position inside. Functionally identical scrapers and preprocessors were written for all posts, not filtered by flair, in order to eventually compare 'good' flair performance to the subreddit at large.

The scrapers function by moving forward in time from a defined 'after' date to a defined 'stop' date. The stop date was set at each run to be the current time, in order to move forward across posts. The after date was hard-coded into the scraper, but would record the current 'max time' of each post as it went in a file, so the next run of the script could start from that point forward.

The scraper saved each set of posts (maximum of 100 per the API) to a JSON file named with the current iteration of the scraper across all runs. All of these small files are compiled using the appropriate compiler script ('good' or 'all') and saved both as a JSON and a CSV, though the JSON is suggested to be used for further processing.

## Preprocessing
### Regular Expressions
Once the data was saved in an easily readable format, the preprocessing scripts could take over. The aim of this section is to pick out the options positions from the titles and/or bodies of the scraped posts. A varied (always growing) list of regular expressions were used to try and match as many different possible ways a position could be written (within reason). Each title / body combination is run through the regular expression, making sure the output matches are re-ordered to be saved in a standard ticker-strike-call/put-expiry format. Additionally, tickers are not required for a match to be found in the regular expressions. This allows it to try and match lists of positions with only one leading ticker, populating the ticker down the list of possible positions. If a ticker is otherwise not found, this also allows for other attempts at matching a ticker, which are attempted later. Each post's positions are returned as nested lists, with the outer list containing smaller lists of single positions, broken into their component parts.
### Dates and Expiry
A tricky part of the data was that older posts were not always posted with a year, since at the time of posting, the year might have been apparent to the readers. This was solved by first assigning all posts with no year already the current year (2020). Then a loop was run checking the posting date of the post to the expiration date listed. If the expiration month was larger than the post month, then it was assumed that the correct year is the posting year, since at that time a person would have had to specify and years later than that, to avoid confusion over the months. If the expiration month was less than the post month, then it must be for the next year since that specificity would not have been required and these are never backward looking.
### Finding empty tickers
Because it was allowed to find positions with no tickers, the list can end up having positions without tickers. Previous preprocessing steps dropped positions if they were unsalvageable but made it possible to have positions missing only a ticker. This stage would look at positions with no ticker, clean the posts of stop words, and then tokenize the remaining words. Then, those tokens are compared one by one to a list of all tickers on the NASDAQ and the NYSE. Each time a token registered a hit it would be saved in a counter object, and ultimately only the three most common tickers would be returned to the data. From there, only the most common one would be used as the missing ticker, assuming that a post about one company would a) be able to imply the ticker in the position listing, and b) the most mentioned ticker would be the correct one. The three most common tickers are returned during the iteration to allow spot checking in review, and for completeness should further analysis ever happen.
### Match Stock Data
Open and close data for the post date and expiration, respectively, were pulled from the previously handled positions and fed into a Yahoo Finance API (Yahoo_fin) to get historical prices. 
### Generate returns
Using the open and close quotes from Yahoo Finance, one can see how often the community as a whole wins or loses their bets, and to what magnitude it occurs. open_price and close_price in the yahoo_fin file are the quotes generated previously. price_delta is the change in price from start to finish of the option contract. sentiment is 'Correct' or 'Not Correct', designated based on the direction of price movement relative to the type of position (call (c) or put (p)); if the position is a call and the price_delta is positive, then the sentiment is 'Correct' because it went in the intended direction. If the same position is taken with a negative price_price delta, the sentiment would be 'Not Correct.' The inverse is true for puts. Moneyness is the gap between strike price of the option and the close_price. Negative values are out of the money (loss) and positive values are in the money (gain).

## Data
The data was too large to host on github, so they are for now hosted at [my server](https://static.jacoblinder.net/dsci511). The data can also reproduced by (patiently) running the scraper, the compiler, and then the Phase 3 Dataset build, in that order. Doing that should result in a complete dataset, with data up to the date the scraper was started. 

## Assumptions
- Posts never refer to positions in the past
- Ticker mentioned the most will be the company the post is talking about

## Challenges and Ideas
After the scrapers were written and running, we thought that it might be smarter to work backwards in time to collect the posts. We discovered that while this method is easier to get started, its no simpler to get new posts as they come up, still needing the dates of posts to be recorded separately.
Using regex to parse position information is imperfect when trying to find a variable pattern with several patterns. While the patterns are mostly thorough, they can't fully handle all edge cases for several position formats and could rarely generate duplicate information from applying new patterns to a post.
Another issue discovered later was that the datetime objects written to the JSON file in python were not read in again as datetime objects. We opted to handle that issue rather than refactor the scripts to output the data correctly, but this is something that needs to change before moving forward in a meaningful way. An idea has been to simply save the dates as sets of integers, and use datetime to read them in again in further processing later.



