"""
Chinchilla Detail Page Scraper
Visits each listing detail page to get full-resolution images
"""
import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin
from PIL import Image
from io import BytesIO
import re


class DetailPageScraper:
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
        except:
            return None
    
    def download_image(self, img_url, save_path):
        try:
            response = self.get_page(img_url)
            if response:
                img = Image.open(BytesIO(response.content))
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                width, height = img.size
                file_size = len(response.content)
                
                # Accept images 150x150 or larger, 10KB+
                if width >= 150 and height >= 150 and file_size >= 10000:
                    img.save(save_path, 'JPEG', quality=95)
                    print(f"    ✓ {width}x{height}, {file_size//1024}KB")
                    return True
                else:
                    print(f"    ✗ Too small: {width}x{height}, {file_size//1024}KB")
                    return False
        except:
            return False
    
    def get_detail_page_urls(self, search_results_url):
        """Extract all listing detail URLs from search results"""
        response = self.get_page(search_results_url)
        if not response:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        detail_urls = []
        
        # Find links to detail pages
        for link in soup.find_all('a', href=True):
            href = link['href']
            if '/listings/details/index.cfm?itemnum=' in href:
                full_url = urljoin('https://www.chinchillas.com', href)
                detail_urls.append(full_url)
        
        return detail_urls
    
    def extract_images_from_detail_page(self, detail_url, image_counter):
        """Visit detail page and extract all full-size images"""
        response = self.get_page(detail_url)
        if not response:
            return 0
        
        soup = BeautifulSoup(response.content, 'html.parser')
        images_downloaded = 0
        
        # Extract item number from URL
        match = re.search(r'itemnum=(\d+)', detail_url)
        if not match:
            return 0
        
        item_num = match.group(1)
        
        # Try multiple patterns to find full images
        img_patterns = [
            f'/images/{item_num}',      # /images/1431974008.jpg
            f'/photos/{item_num}',      # /photos/1431974008_1.jpg
            f'/uploads/{item_num}',     # /uploads/1431974008.jpg
            f'/pics/{item_num}',        # /pics/1431974008.jpg
            item_num                    # Any path with this ID
        ]
        
        for img_tag in soup.find_all('img', src=True):
            img_src = img_tag['src']
            
            # Check if this image matches our item
            is_match = any(pattern in img_src for pattern in img_patterns)
            
            # Skip thumbnails
            if '/thumbs/' in img_src:
                is_match = False
            
            if is_match and img_src not in self.downloaded_ids:
                self.downloaded_ids.add(img_src)
                
                full_url = urljoin('https://www.chinchillas.com', img_src)
                filename = f"{self.label_prefix}_{image_counter + images_downloaded:04d}.jpg"
                save_path = os.path.join(self.output_dir, filename)
                
                print(f"  [{image_counter + images_downloaded:04d}] {filename}")
                print(f"    URL: {full_url}")
                
                if self.download_image(full_url, save_path):
                    images_downloaded += 1
                
                time.sleep(0.5)
        
        return images_downloaded
    
    def scrape_all_pages(self, max_pages=None):
        current_url = self.base_url
        page_count = 0
        total_images = 0
        
        print(f"\nDetail Page Scraper: {self.label_prefix}")
        print("="*60)
        print("Visiting each listing page for full images")
        print("="*60)
        
        while current_url and (max_pages is None or page_count < max_pages):
            page_count += 1
            print(f"\n>>> Search Results Page {page_count}")
            
            # Get all detail page URLs from this search results page
            detail_urls = self.get_detail_page_urls(current_url)
            print(f"Found {len(detail_urls)} listings on this page")
            
            # Visit each detail page
            for i, detail_url in enumerate(detail_urls, 1):
                print(f"\n  Listing {i}/{len(detail_urls)}")
                count = self.extract_images_from_detail_page(detail_url, total_images + 1)
                total_images += count
                
                if count == 0:
                    print("    No full images found")
                
                time.sleep(1)  # Be nice to the server
            
            # Find next search results page
            response = self.get_page(current_url)
            if not response:
                break
            
            soup = BeautifulSoup(response.content, 'html.parser')
            next_url = None
            for link in soup.find_all('a', href=True):
                if 'next' in link.get_text(strip=True).lower():
                    next_url = urljoin(current_url, link['href'])
                    break
            
            if not next_url:
                print("\nNo more search result pages")
                break
            
            current_url = next_url
            time.sleep(2)
        
        print(f"\n{'='*60}")
        print(f"Complete: {total_images} full images")
        print(f"From {page_count} search pages")
        print(f"Location: {self.output_dir}")
        print(f"{'='*60}\n")
        return total_images


if __name__ == "__main__":
    print("="*60)
    print(" Chinchilla Detail Page Scraper")
    print("="*60)
    
    url = input("Search results URL: ").strip()
    label = input("Label: ").strip() or "chinchilla"
    max_pages = input("Max search pages (Enter for all): ").strip()
    max_pages = int(max_pages) if max_pages.isdigit() else None
    
    scraper = DetailPageScraper(url, f"data/{label}", label)
    scraper.scrape_all_pages(max_pages)
