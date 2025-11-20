"""
Main scraper for chinchilla images
Downloads and splits images from detail pages
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
        except:
            return None
    
    def split_stacked_image(self, img, tile_height=600):
        """Split vertically stacked images"""
        width, height = img.size
        
        if height % tile_height != 0:
            return [img]
        
        num_tiles = height // tile_height
        if num_tiles == 1:
            return [img]
        
        print(f"    Splitting {width}x{height} into {num_tiles} images")
        
        tiles = []
        for i in range(num_tiles):
            top = i * tile_height
            bottom = top + tile_height
            tile = img.crop((0, top, width, bottom))
            tiles.append(tile)
        
        return tiles
    
    def download_and_split(self, img_url, image_counter):
        """Download and split images"""
        try:
            response = self.get_page(img_url)
            if not response:
                return 0
            
            img = Image.open(BytesIO(response.content))
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            width, height = img.size
            file_size = len(response.content)
            
            print(f"    Downloaded: {width}x{height}, {file_size//1024}KB")
            
            tiles = self.split_stacked_image(img)
            
            images_saved = 0
            for tile in tiles:
                tile_width, tile_height = tile.size
                
                if tile_width >= 400 and tile_height >= 400:
                    filename = f"{self.label_prefix}_{image_counter + images_saved:04d}.jpg"
                    save_path = os.path.join(self.output_dir, filename)
                    
                    tile.save(save_path, 'JPEG', quality=95)
                    print(f"    Saved: {filename} ({tile_width}x{tile_height})")
                    images_saved += 1
            
            return images_saved
            
        except Exception as e:
            print(f"    Error: {e}")
            return 0
    
    def get_detail_urls(self, search_url):
        """Get all listing URLs from search results"""
        response = self.get_page(search_url)
        if not response:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        detail_urls = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            if '/listings/details/index.cfm?itemnum=' in href:
                full_url = urljoin('https://www.chinchillas.com', href)
                if full_url not in detail_urls:
                    detail_urls.append(full_url)
        
        return detail_urls
    
    def scrape_detail_page(self, detail_url, image_counter):
        """Get images from a single detail page"""
        response = self.get_page(detail_url)
        if not response:
            return 0
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        match = re.search(r'itemnum=(\d+)', detail_url)
        if not match:
            return 0
        
        item_num = match.group(1)
        
        img_patterns = [
            f'/images/{item_num}',
            f'/photos/{item_num}',
            f'/uploads/{item_num}',
            f'/pics/{item_num}',
            item_num
        ]
        
        images_downloaded = 0
        
        for img_tag in soup.find_all('img', src=True):
            img_src = img_tag['src']
            
            is_match = any(pattern in img_src for pattern in img_patterns)
            
            if '/thumbs/' in img_src:
                is_match = False
            
            if is_match and img_src not in self.downloaded_ids:
                self.downloaded_ids.add(img_src)
                
                full_url = urljoin('https://www.chinchillas.com', img_src)
                
                print(f"  Processing: {full_url}")
                
                count = self.download_and_split(
                    full_url, 
                    image_counter + images_downloaded
                )
                images_downloaded += count
                
                time.sleep(0.5)
        
        return images_downloaded
    
    def scrape_all(self, max_pages=None):
        """Scrape all pages"""
        current_url = self.base_url
        page_count = 0
        total_images = 0
        
        print(f"\nScraping: {self.label_prefix}")
        print("-" * 60)
        
        while current_url and (max_pages is None or page_count < max_pages):
            page_count += 1
            print(f"\nSearch page {page_count}")
            
            detail_urls = self.get_detail_urls(current_url)
            print(f"Found {len(detail_urls)} listings")
            
            for i, detail_url in enumerate(detail_urls, 1):
                print(f"\nListing {i}/{len(detail_urls)}")
                count = self.scrape_detail_page(detail_url, total_images + 1)
                total_images += count
                
                if count == 0:
                    print("  No images found")
                
                time.sleep(1)
            
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
                break
            
            current_url = next_url
            time.sleep(2)
        
        print(f"\n{'-' * 60}")
        print(f"Complete: {total_images} images")
        print(f"Search pages: {page_count}")
        print(f"Location: {self.output_dir}")
        print(f"{'-' * 60}\n")
        return total_images


if __name__ == "__main__":
    url = input("Search URL: ").strip()
    label = input("Label: ").strip() or "chinchilla"
    max_pages = input("Max pages (Enter for all): ").strip()
    max_pages = int(max_pages) if max_pages.isdigit() else None
    
    scraper = ChinchillaScraper(url, f"data/{label}", label)
    scraper.scrape_all(max_pages)
