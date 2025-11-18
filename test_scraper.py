"""Quick test - tries multiple URL patterns"""
from scraper import ChinchillaScraper

url = 'https://www.chinchillas.com/search/search_results.cfm?search_text=standard&search_type=title_search&search_limit=all&phrase_match=all&sort_order=desc'

scraper = ChinchillaScraper(url, "data/test", "test")
scraper.scrape_all_pages(max_pages=1)