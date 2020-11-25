# DSCI 511 r/wallstreetbets adventure

## The Scraper(s)

<p>This project is broken into two main branches at the beginning, the 'good posts' and 'all posts'. Good posts are posts the are flaired with what we considered to be a good flair, likely to have a worthwhile position inside. We also wrote functionally identical scrapers and preprocessors for all the data, not filtered by flair, in order to eventually compare our taste in flair's performance to the subreddit at large. </p>

<p> The scrapers function by moving forward in time from a defined 'after' date to a defined 'stop' date. The stop date was set at each run to be the current time, in order to move forward across posts. The after date was hardcoded into the scraper, but would record the current 'max time' of each post as it went in a file, so the next run of the script could start from that point forward. </p>

<p> The scraper saved each set of posts (maximum of 100 per the api) to a json file named with the current iteration of the scraper across all runs. These files can be compiled into one CSV using the compiler script (one for 'good', one for 'all') included in the files. These files can be proccessed using the same scripts past this point. </p>

### Challenges and Ideas
<p> After the scrapers were written and running, we thought that it might be smarter to work backwards in time to collect the posts. We discovered that while this method is easier to get started, its no simpler to get new posts as they come up, still needing the dates of posts to be recorded separetely. </p>



