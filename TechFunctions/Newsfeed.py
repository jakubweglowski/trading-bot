import requests
import json

# Replace with your NewsAPI key
API_KEY = '148c5df99e2d4830bbd3aa5d0dfdff3f'

# Define the commodities and their refined queries
commodities = {
    "Gold": "gold AND (commodity OR prices OR market OR bullion OR mining) -person -name -surname",
    "Silver": "silver AND (commodity OR prices OR market OR bullion OR mining) -person -name -surname",
    "Copper": "copper AND (commodity OR prices OR market OR mining) -person -name -surname",
    "Aluminium": "aluminium AND (commodity OR prices OR market OR mining) -person -name -surname"
}

# Base URL for NewsAPI
url = 'https://newsapi.org/v2/everything'

# Function to fetch news
def fetch_news(query):
    params = {
        'q': query,
        'apiKey': API_KEY,
        'pageSize': 5,  # Fetch 5 articles per commodity
        'sortBy': 'publishedAt',  # Sort by latest
        'language': 'en'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        articles = response.json().get('articles', [])
        return articles
    else:
        print(f"Failed to fetch news for query '{query}': {response.status_code}")
        return []

# Fetch news for each commodity and store in a dictionary
news_data = {}
for commodity, query in commodities.items():
    articles = fetch_news(query)
    news_data[commodity] = [
        {"title": article['title'], "link": article['url']}
        for article in articles
    ]

print("News data saved to 'news_data.json'.")
with open('App/data/news_data.json', 'w') as file:
    json.dump(news_data, file, indent=4)
