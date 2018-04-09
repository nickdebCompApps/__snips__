import requests
import time
from newsapi import NewsApiClient
from keys import key

def News(conn):
    api = NewsApiClient(api_key=key.api_keys['NEWS_API'])
    headlines = api.get_top_headlines(country='us', page_size = 5)

    for article in headlines['articles']:
        author = article['author']
        if author is not None:
            if 'http' in author:
                author = 'No author'
            if author == "":
                author = 'No author'
        description = article['description']
        title = article['title']
    conn.send(headlines['articles'])
    conn.close()
    return headlines['articles']

#news = News()
