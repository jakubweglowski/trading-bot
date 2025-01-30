import requests

# Replace with your NewsAPI key
API_KEY = '148c5df99e2d4830bbd3aa5d0dfdff3f'

# Define the commodities
commodities = ['gold', 'silver', 'copper', 'aluminium']

# Base URL for NewsAPI
url = 'https://newsapi.org/v2/everything'

# Function to fetch news
def fetch_news(commodity):
    params = {
        'q': commodity,
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
        print(f"Failed to fetch news for {commodity}: {response.status_code}")
        return []


for commodity in commodities:
    print(f"\nLatest news for {commodity.capitalize()}:")
    articles = fetch_news(commodity)
    for idx, article in enumerate(articles, start=1):
        print(f"{idx}. {article['title']}")
        print(f"   Link: {article['url']}\n")