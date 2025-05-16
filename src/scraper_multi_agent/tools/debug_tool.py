from scraper_multi_agent.tools.shopify_scraper import scrape_shopify_collection

def debug_scraper():
    result = scrape_shopify_collection("https://maguireshoes.com/collections/sneakers")
    print("Raw result from tool:", result)

if __name__ == "__main__":
    debug_scraper()
