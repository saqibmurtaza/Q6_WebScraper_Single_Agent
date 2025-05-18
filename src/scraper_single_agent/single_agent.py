from agents import Agent, Runner
from scraper_single_agent.tools.shopify_scraper import scrape_shopify_collection
from scraper_single_agent.tools.save_to_google import save_to_sheet
from scraper_single_agent.config_agents import config
import os, json
# Shopify scraping agent
shopify_agent = Agent(
    name="shopify_agent",
    instructions="""You are a Shopify product scraping specialist.

    When given a shopify URL and as sheet URL, you must:
    1. Use scrape_shopify_collection to get the product data
    2. Return ONLY the scraped product data as a JSON array
    3. Use save_to_sheet to write the data
    3. Save data to Google Sheet using tool save_to_sheet
    
    Do not add any extra text or explanations.
    Do not ask for additional functionality.
    Just return the raw product data array.
    """,
    tools=[scrape_shopify_collection, save_to_sheet],
    
)

# Example values - replace with actual URLs
shopify_url = "https://maguireshoes.com/collections/sneakers"
sheet_url = "https://docs.google.com/spreadsheets/d/1DtZXL0gVeU-kr4WpUcBpmQJr-h9-SBgYY9Lzb5pxAoY/edit?gid=0#gid=0"

# New main execution function for testing or direct use
async def main(shopify_url, sheet_url):

    input_data = {
        "shopify_url": shopify_url,
        "sheet_url": sheet_url,
    } 
    import json

    stringify= json.dumps(input_data)
    # Print for debugging
    print(f"Starting workflow with input: {stringify}")
    
    # Run the triage agent with the input
    result = await Runner.run(
        shopify_agent, 
        input=stringify, 
        run_config=config)
    
    return result.final_output

if __name__ == "__main__":
    import asyncio
    # get_google_client() # Initialize client on startup

    final_output= asyncio.run(main(shopify_url, sheet_url))
    print(final_output)


