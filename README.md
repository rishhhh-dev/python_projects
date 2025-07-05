Create a virtualenv using Python shell
Activate the virtualenv and install the required packages from requirements.txt

```pip install -r requirements.txt```

**Projects**
-> _web_scraping/scrape_load.py_ : This is a Python script which scrapes books data from this site https://books.toscrape.com/ using htmlib5 and BeatuifulSoup. 
Next, it cleans the scraped data and stores (or) loads the cleaned data into PostgreSQL database. It also creates a csv or json file loaded with the cleaned data.
