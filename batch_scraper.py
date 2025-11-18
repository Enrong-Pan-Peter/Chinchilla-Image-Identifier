"""Batch scraper for multiple chinchilla breeds"""
from scraper import ChinchillaScraper
import time

BREEDS = [
    {
        'name': 'standard',
        'url': 'https://www.chinchillas.com/search/search_results.cfm?search_text=standard&search_type=title_search&search_limit=all&phrase_match=all&sort_order=desc',
        'count': '919'
    },
    {
        'name': 'white',
        'url': 'https://www.chinchillas.com/search/search_results.cfm?search_text=white&search_type=title_search&search_limit=all&phrase_match=all&sort_order=desc',
        'count': '964'
    },
    {
        'name': 'black_velvet',
        'url': 'https://www.chinchillas.com/search/search_results.cfm?search_text=black+velvet&search_type=title_search&search_limit=all&phrase_match=all&sort_order=desc',
        'count': '374'
    },
    {
        'name': 'beige',
        'url': 'https://www.chinchillas.com/search/search_results.cfm?search_text=beige&search_type=title_search&search_limit=all&phrase_match=all&sort_order=desc',
        'count': '477'
    },
    {
        'name': 'pink_white',
        'url': 'https://www.chinchillas.com/search/search_results.cfm?search_type=title_search&search_name=Title%2B&%2BDescription%2BSearch&search_text=pink&phrase_match=any&category=-1&search_span=title&search_limit=all&country_type=in&country=&order_by=title&sort_order=DESC',
        'count': '178'
    }
]

def main():
    print("-"*60)
    print(" Batch Chinchilla Scraper - Full Resolution")
    print("-"*60)
    print(f"\nConfigured breeds: {len(BREEDS)}")
    for i, breed in enumerate(BREEDS, 1):
        print(f"  {i}. {breed['name']} (expected: {breed['expected']} images)")
    
    print("\n" + "-"*60)
    print("Choose mode:")
    print("  1. TEST MODE (2 pages per breed, ~50 images each)")
    print("  2. FULL SCRAPE (all images)")
    print("  3. CUSTOM (specify pages)")
    print("-"*60)
    
    choice = input("\nYour choice (1-3): ").strip()
    
    if choice == '1':
        max_pages = 2
        mode = "TEST"
        print(f"\n✓ TEST MODE: 2 pages per breed")
    elif choice == '2':
        max_pages = None
        mode = "FULL"
        print(f"\n✓ FULL SCRAPE: ALL pages")
    elif choice == '3':
        max_pages_input = input("Max pages per breed: ").strip()
        max_pages = int(max_pages_input) if max_pages_input.isdigit() else None
        mode = f"CUSTOM ({max_pages} pages)"
    else:
        print("Invalid choice!")
        return
    
    confirm = input(f"\nProceed with {mode}? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("Cancelled")
        return
    
    print("\n" + "-"*60)
    print(f" Starting Batch Scrape - {mode}")
    print(" FULL-RESOLUTION IMAGES")
    print("-"*60)
    
    results = {}
    start_time = time.time()
    
    for i, breed in enumerate(BREEDS, 1):
        print(f"\n{'#'*60}")
        print(f"# [{i}/{len(BREEDS)}] Scraping: {breed['name']}")
        print(f"# Expected: ~{breed['expected']} images")
        print(f"{'#'*60}")
        
        scraper = ChinchillaScraper(
            base_url=breed['url'],
            output_dir=f"data/{breed['name']}",
            label_prefix=breed['name']
        )
        
        try:
            total = scraper.scrape_all_pages(max_pages=max_pages)
            results[breed['name']] = total
        except KeyboardInterrupt:
            print("\n\n⚠ Interrupted!")
            results[breed['name']] = 0
            break
        except Exception as e:
            print(f"\n Error: {e}")
            results[breed['name']] = 0
        
        if i < len(BREEDS):
            print("\n⏸ Waiting 5 seconds...")
            time.sleep(5)
    
    elapsed = time.time() - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    
    print("\n\n" + "="*60)
    print(f" Complete - {mode}")
    print("-"*60)
    print(f"Time: {minutes}m {seconds}s\n")
    print("Results:")
    print(f"{'Breed':<20} {'Images':<10}")
    print("-"*60)
    
    total_all = 0
    for breed in BREEDS:
        name = breed['name']
        count = results.get(name, 0)
        total_all += count
        status = "✓" if count > 0 else "✗"
        print(f"{status} {name:<18} {count:>5}")
    
    print("-"*60)
    print(f"{'TOTAL':<20} {total_all:>5}")
    print("\n Location: ./data/")
    print("-"*60)

if __name__ == "__main__":
    main()