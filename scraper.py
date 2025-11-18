"""
Chinchilla Image Scraper
"""
import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin
from PIL import Image
from io import BytesIO
import re

class ChinchillaScraper:
    def __init__(self, base_url, output_dir, label_prefix):
        self.base_url = base_url
        self.output_dir = output_dir
        self.label_prefix = label_prefix
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0'})
        os.makedirs(output_dir, exist_ok=True)
        self.downloaded_ids = set()
    
    def get_page(self, url):
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return response
        except Exception as e:
            return None
    
    def download_image(self, img_url, save_path):
        try:
            response = self.get_page(img_url)
            if response:
                img = Image.open(BytesIO(response.content))
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                width, height = img.size
                # Accept any image over 100x100
                if width < 100 or height < 100:
                    return False
                
                img.save(save_path, 'JPEG', quality=95)
                return True
        except:
            return False
    
    def try_multiple_urls(self, img_id, save_path):
        """Try different URL patterns to find the best image"""
        url_patterns = [
            f'https://www.chinchillas.com/images/{img_id}.jpg',  # Try images folder
            f'https://www.chinchillas.com/uploads/{img_id}.jpg',  # Try uploads
            f'https://www.chinchillas.com/thumbs/{img_id}.jpg',   # Fallback to thumbs
        ]
        
        for url in url_patterns:
            if self.download_image(url, save_path):
                return True
        
        return False
    
    def extract_images_from_page(self, page_url, start_number):
        response = self.get_page(page_url)
        if not response:
            return 0, None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        images_downloaded = 0
        
        for img_tag in soup.find_all('img', src=True):
            img_src = img_tag.get('src', '')
            
            if '/thumbs/' in img_src and '.jpg' in img_src:
                match = re.search(r'/thumbs/(\d+)\.jpg', img_src)
                if match:
                    img_id = match.group(1)
                    
                    if img_id not in self.downloaded_ids:
                        self.downloaded_ids.add(img_id)
                        
                        image_num = start_number + images_downloaded
                        filename = f"{self.label_prefix}_{image_num:04d}.jpg"
                        save_path = os.path.join(self.output_dir, filename)
                        
                        print(f"  [{image_num:04d}] Trying {filename}...", end=' ')
                        
                        if self.try_multiple_urls(img_id, save_path):
                            images_downloaded += 1
                            print("✓")
                        else:
                            print("✗")
                        
                        time.sleep(0.5)
        
        next_url = None
        for link in soup.find_all('a', href=True):
            if 'next' in link.get_text(strip=True).lower():
                next_url = urljoin(page_url, link['href'])
                break
        
        return images_downloaded, next_url
    
    def scrape_all_pages(self, max_pages=None):
        current_url = self.base_url
        page_count = 0
        total_images = 0
        
        print(f"\nScraping: {self.label_prefix}")
        print("-"*60)
        
        while current_url and (max_pages is None or page_count < max_pages):
            page_count += 1
            print(f"\nPage {page_count}")
            
            count, next_url = self.extract_images_from_page(current_url, total_images + 1)
            total_images += count
            
            if count == 0 or not next_url:
                break
            
            current_url = next_url
            time.sleep(2)
        
        print(f"\n{'-'*60}")
        print(f"Complete: {total_images} images")
        print(f"Location: {self.output_dir}")
        print(f"{'-'*60}\n")
        return total_images


if __name__ == "__main__":
    print("Chinchilla Scraper")
    url = input("URL: ").strip()
    label = input("Label: ").strip() or "chinchilla"
    max_pages = input("Max pages: ").strip()
    max_pages = int(max_pages) if max_pages.isdigit() else None
    
    scraper = ChinchillaScraper(url, f"data/{label}", label)
    scraper.scrape_all_pages(max_pages)