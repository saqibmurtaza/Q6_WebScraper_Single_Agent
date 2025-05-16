from agents import Agent, Runner
from scraper_multi_agent.config_agents import config
from scraper_multi_agent.tools.save_to_google import save_to_sheet
from scraper_multi_agent.tools.shopify_scraper import scrape_shopify_collection
import json


# Shopify scraping agent
shopify_agent = Agent(
    name="shopify_agent",
    instructions="""You are a Shopify product scraping specialist.

    When given a shopify URL, you must:
    1. Use scrape_shopify_collection to get the product data
    2. Return ONLY the scraped product data as a JSON array
    
    Do not add any extra text or explanations.
    Do not ask for additional functionality.
    Just return the raw product data array.
    """,
    tools=[scrape_shopify_collection],
    handoff_description="Extract product data from shopify_url using the scrape_shopify_collection tool."
    
)

# data_writer_agent 
data_writer_agent = Agent(
    name="data_writer_agent",
    instructions="""You are a Google Sheets data writing specialist.

    When given product data and a sheet URL, you must:
    1. Use save_to_sheet to write the data
    2. Return ONLY the success/failure message
    
    Do not add any extra text or explanations.
    Do not modify the input data.
    Just save and return the status message.
    """,
    tools=[save_to_sheet],
    handoff_description="Saves product data to Google Sheets using tool save_to_sheet."
)


#triage_agent
triage_agent = Agent(
    name="Triage Agent",
    instructions="""You coordinate scraping and saving Shopify product data.

    Follow these steps exactly:
    1. Parse the input JSON to get shopify_url and sheet_url
    2. Hand off to shopify_agent with ONLY the shopify_url
    3. Take the product data array returned by shopify_agent
    4. Prepare the input for the data_writer_agent in the format:
       {"sheet_url": "<sheet_url_value>", "products": <product_data_array>}
       Make sure <sheet_url_value> is the sheet_url parsed in step 1.
       Make sure <product_data_array> is the data returned in step 3.
    5. Hand off to data_writer_agent with the prepared input from step 4.
    6. Return the final save status message from data_writer_agent.

    IMPORTANT: Do not add extra explanations or text.
    Just coordinate the data flow between agents and return the final result of the save operation.
    """,
    handoffs=[shopify_agent, data_writer_agent]
)


# URL's INPUT
shopify_url = "https://maguireshoes.com/collections/heels"
sheet_url = "https://docs.google.com/spreadsheets/d/1DtZXL0gVeU-kr4WpUcBpmQJr-h9-SBgYY9Lzb5pxAoY/edit?gid=0#gid=0"
# products = []
# Main execution function
async def main(shopify_url, sheet_url):
   
    input_data = {
        "shopify_url": shopify_url,
        # "products": products,
        "sheet_url": sheet_url,
        
    } 

    stringify= json.dumps(input_data)
    # Print for debugging
    print(f"Starting workflow with input: {stringify}")
    
    # Run the triage agent with the input
    result = await Runner.run(
        triage_agent, 
        input=stringify,
        run_config=config,
        )
    
    return result


if __name__ == "__main__":
    import asyncio
    final_output= asyncio.run(main(shopify_url, sheet_url))
    print(final_output)


# orchestrator_agent = Agent(
#     name="orchestrator_agent",
#     instructions=(
#         "You are a router agent responsible for orchestrating data scraping and saving operations."
#         "Execute the given tools in sequence: first, scrape data using the shopify_agent, then save the extracted data using the data_writer_agent."
#         "Ensure that you strictly return the final save status message from data_writer_agent without adding any explanations, commentary, or unnecessary text."
#         "Process results exactly as received, avoiding hallucinations, modifications, or extra wording."
#     ),
#     tools=[
#         shopify_agent.as_tool(
#             tool_name="scrape_shopify_collection",
#             tool_description="Extract product data from the given Shopify collection URL.",
#         ),
#         data_writer_agent.as_tool(
#             tool_name="save_to_sheet",
#             tool_description="Store the extracted product data in Google Sheets.",
#         ),
#     ],
# )
