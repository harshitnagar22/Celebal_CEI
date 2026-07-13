import requests
from bs4 import BeautifulSoup
import os
import json
from src.core.config import config

class WebScraper:
    def __init__(self, output_dir=None):
        self.output_dir = output_dir or os.path.join(config.DATA_DIR, "raw")
        os.makedirs(self.output_dir, exist_ok=True)
        
    def scrape_wikipedia(self, url, filename):
        """Scrape text content from a Wikipedia page."""
        print(f"Scraping {url}...")
        try:
            headers = {
                'User-Agent': 'MemoryAugmentedChatbot/1.0 (https://github.com/yourusername/MemoryAugmentedChatbot; you@example.com)'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.find('h1', {'id': 'firstHeading'}).text
            
            # Extract all paragraphs in the content body
            content_div = soup.find('div', {'id': 'mw-content-text'})
            paragraphs = content_div.find_all('p')
            
            text_content = [p.text for p in paragraphs if p.text.strip()]
            
            data = {
                "url": url,
                "title": title,
                "content": "\n".join(text_content)
            }
            
            file_path = os.path.join(self.output_dir, f"{filename}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                
            print(f"Successfully saved {title} to {file_path}")
            return data
            
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return None

def run_pipeline():
    """Run the initial scraping pipeline."""
    urls = [
        ("https://en.wikipedia.org/wiki/Artificial_intelligence", "artificial_intelligence"),
        ("https://en.wikipedia.org/wiki/Machine_learning", "machine_learning"),
        ("https://en.wikipedia.org/wiki/Large_language_model", "large_language_model")
    ]
    
    scraper = WebScraper()
    for url, filename in urls:
        scraper.scrape_wikipedia(url, filename)

if __name__ == "__main__":
    run_pipeline()
