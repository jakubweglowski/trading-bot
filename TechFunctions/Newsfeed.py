import requests
import json

API_KEY = '148c5df99e2d4830bbd3aa5d0dfdff3f'

commodities = ['gold', 'silver', 'copper', 'aluminium']

url = 'https://newsapi.org/v2/everything'

def fetch_news(commodity):
    params = {
        'q': commodity,
        'apiKey': API_KEY,
        'pageSize': 5, 
        'sortBy': 'publishedAt', 
        'language': 'en'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        articles = response.json().get('articles', [])
        return articles
    else:
        print(f"Failed to fetch news for {commodity}: {response.status_code}")
        return []

news_data = {}
for commodity in commodities:
    articles = fetch_news(commodity)
    news_data[commodity.capitalize()] = [
        {"title": article['title'], "link": article['url']}
        for article in articles
    ]

with open('App/data/news_data.json', 'w') as file:
    json.dump(news_data, file, indent=4)
