# DSCI 511 r/wallstreetbets adventure

## The Scraper(s)

<p>This project is broken into two main branches at the beginning, the 'good posts' and 'all posts'. Good posts are posts the are flaired with what we considered to be a good flair, likely to have a worthwhile position inside. We also wrote functionally identical scrapers and preprocessors for all the data, not filtered by flair, in order to eventually compare our taste in flair's performance to the subreddit at large. </p>

<p> The scrapers function by moving forward in time from a defined 'after' date to a defined 'stop' date. The stop date was set at each run to be the current time, in order to move forward across posts. The after date was hard-coded into the scraper, but would record the current 'max time' of each post as it went in a file, so the next run of the script could start from that point forward. </p>

<p> The scraper saved each set of posts (maximum of 100 per the api) to a json file named with the current iteration of the scraper across all runs. All of these small files are compiled using the appropriate compiler script ('good' or 'all') and saved both as a JSON and a CSV, though the JSON is suggested to be used for further processing.</p>

## Preprocessing
### Regular Expressions
<p> Once the data was saved in an easily readable format, the preprocessing scripts could take over. The goal here was to pick out the options positions from the titles and/or bodies of the posts we scraped. We used a variety (always growing) list of regular expressions to try and match as many different possible ways a position could be written (within reason). We run each title / body combination through the regular expression, making sure the output matches are re-ordered to be saved in a standard ticker-strike-call/put-expiry format. Additionally, tickers are not required for a match to be found in the regular expressions. This allows to try and match lists of positions with only one leading ticker, populating the ticker down the list of possible positions. If a ticker is otherwise not found, this also allows for other attempts at matching a ticker, which we attempt later. Each post's positions are returned as nested lists, with the outer list containing smaller lists of single positions, broken into their component parts. </p>
### Dates and Expiry
<p> A tricky part of the data was that older posts were not always posted with a year, since at the time the year might have been apparent to the readers. This was

## Assumptions
## Challenges and Ideas
<p> After the scrapers were written and running, we thought that it might be smarter to work backwards in time to collect the posts. We discovered that while this method is easier to get started, its no simpler to get new posts as they come up, still needing the dates of posts to be recorded separately. </p>
<p> Another issue we discovered later was that the datetime objects written to the JSON file in python were not read in again as JSON files. We opted to handle that issue rather than refactor the scripts to output the data correctly, but this is something we need to change before moving forward in a meaningful way. An idea has been to simply save the dates as sets of integers, and use datetime to read them in again in further processing later. </p>




