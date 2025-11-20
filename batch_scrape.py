"""
Batch scraper for multiple chinchilla breeds
"""
from scraper import ChinchillaScraper
import time


# breed urls and expected counts
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
    print("-" * 60)
    print(" Batch Chinchilla Scraper")
    print("-" * 60)
    
    print(f"\nBreeds: {len(BREEDS)}")
    for i, breed in enumerate(BREEDS, 1):
        has_url = "Yes" if breed['url'] else "No"
        print(f"  {i}. {breed['name']:<20} URL: {has_url}")
    
    print("\n" + "-" * 60)
    print("Options:")
    print("  1. TEST MODE (2 pages)")
    print("  2. FULL SCRAPE (all pages)")
    print("  3. CUSTOM")
    print("-" * 60)
    
    choice = input("\nChoice (1-3): ").strip()
    
    if choice == '1':
        max_pages = 2
        mode = "TEST"
    elif choice == '2':
        max_pages = None
        mode = "FULL"
    elif choice == '3':
        max_pages_input = input("Pages per breed: ").strip()
        max_pages = int(max_pages_input) if max_pages_input.isdigit() else None
        mode = "CUSTOM"
    else:
        print("Invalid")
        return
    
    confirm = input(f"\nProceed with {mode}? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("Cancelled")
        return
    
    print(f"\n{'-' * 60}")
    print(f" Starting: {mode}")
    print("-" * 60)
    
    results = {}
    start_time = time.time()
    
    for i, breed in enumerate(BREEDS, 1):
        if not breed['url']:
            print(f"\nSkipping {breed['name']}: No URL")
            continue
        
        print(f"\n{'#' * 60}")
        print(f"# [{i}/{len(BREEDS)}] {breed['name']}")
        print(f"{'#' * 60}")
        
        scraper = ChinchillaScraper(
            base_url=breed['url'],
            output_dir=f"data/{breed['name']}",
            label_prefix=breed['name']
        )
        
        try:
            total = scraper.scrape_all(max_pages=max_pages)
            results[breed['name']] = total
        except KeyboardInterrupt:
            print("\n\nInterrupted")
            results[breed['name']] = 0
            break
        except Exception as e:
            print(f"\nError: {e}")
            results[breed['name']] = 0
        
        if i < len(BREEDS):
            print("\nWaiting 5 seconds...")
            time.sleep(5)
    
    elapsed = time.time() - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    
    print(f"\n\n{'-' * 60}")
    print(f" Complete - {mode}")
    print("-" * 60)
    print(f"Time: {minutes}m {seconds}s\n")
    print(f"{'Breed':<20} {'Images':<10}")
    print("-" * 60)
    
    total_all = 0
    for breed in BREEDS:
        name = breed['name']
        count = results.get(name, 0)
        total_all += count
        status = "OK" if count > 0 else "--"
        print(f"{status:>4} {name:<16} {count:>5}")
    
    print("-" * 60)
    print(f"{'TOTAL':<20} {total_all:>5}")
    print(f"\nLocation: ./data/")
    print("-" * 60)


if __name__ == "__main__":
    main()
