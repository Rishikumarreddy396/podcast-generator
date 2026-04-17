# news_fetcher.py

import requests
import config

def fetch_latest_articles():
    """Fetches the latest articles from NewsAPI for all specified categories."""
    print("Checking for new articles across all categories...")
    all_articles = []
    
    for category in config.CATEGORIES:
        print(f"Fetching news for category: {category}...")
        url = (f"https://newsapi.org/v2/top-headlines?"
               f"country={config.NEWS_COUNTRY}&"
               f"category={category}&"
               f"apiKey={config.NEWS_API_KEY}")
        
        try:
            response = requests.get(url)
            response.raise_for_status() 
            news_data = response.json()
            
            articles = news_data.get('articles', [])
            if articles:
                # Add the category to each article object for later use
                for article in articles:
                    article['category'] = category
                all_articles.extend(articles)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching news for category '{category}': {e}")
            continue # Continue to the next category
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            continue

    print(f"Found a total of {len(all_articles)} articles.")
    return all_articles