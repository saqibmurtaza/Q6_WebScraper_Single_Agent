from agents import Agent, Runner
from scraper_multi_agent.config_agents import config
from scraper_multi_agent.tools.save_to_google import save_to_sheet
from scraper_multi_agent.tools.shopify_scraper import scrape_shopify_collection
import json


# Shopify scraping agent
# shopify_agent = Agent(
#     name="shopify_agent",
#     instructions="""You are a Shopify product scraping specialist.

#     When given a shopify URL, you must:
#     1. Use scrape_shopify_collection to get the product data
#     2. Return the data in the format required by the data_writer_agent
#     """,
#     tools=[scrape_shopify_collection],
#     handoff_description="Extract product data from shopify_url using the scrape_shopify_collection tool."
    
# )

shopify_agent = Agent(
    name="shopify_agent",
    instructions="""
You are a Shopify scraping agent.

When given a Shopify collection URL, follow these rules exactly:

1. Call the tool `scrape_shopify_collection` using the URL.
2. Do not interpret or process the tool output.
3. Do not add or remove any keys (e.g., no `image`, `url`, or lowercase keys).
4. Do not add any markdown (no triple backticks).
5. DO NOT guess — return the result from the tool exactly as-is.

Example format to return (from tool):
{
  "products": [
    {
      "Title": "Simone White Trainer",
      "Price": "240.00",
      "Description": "Handmade in Houjie, China ..."
    },
    ...
  ]
}
Return the above structure **exactly** as returned by the tool.
""",
    tools=[scrape_shopify_collection],
    handoff_description="Scrapes Shopify collection and returns cleanly structured product data."
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

triage_agent = Agent(
    name="triage_agent",
    instructions="""
    You must follow these steps exactly:

    1. Parse input to get shopify_url and sheet_url.

    2. Call the `scrape_shopify_collection` tool using only the shopify_url.
    - This tool returns: { "products": [...] }

    3. Take the returned products list and construct a new JSON object:
    {
        "sheet_url": "<sheet_url>",
        "products": [...]
    }

    4. Call the `save_to_sheet` tool with this new JSON object.
    IMPORTANT: Convert it to a valid JSON string if necessary.

    5. Return only the result from `save_to_sheet`. Do not add any extra formatting or explanation.
    """,
    tools=[
            shopify_agent.as_tool(
                tool_name="scrape_shopify_collection",
                tool_description="Scrapes product data from a Shopify URL"
            ),
            data_writer_agent.as_tool(
                tool_name="save_to_sheet",
                tool_description="Saves product data to Google Sheets"
            ),
        ],
    )

# URL's INPUT
shopify_url = "https://maguireshoes.com/collections/heels"
sheet_url = "https://docs.google.com/spreadsheets/d/1DtZXL0gVeU-kr4WpUcBpmQJr-h9-SBgYY9Lzb5pxAoY/edit?gid=0#gid=0"
# products = []
# Main execution function
async def main(shopify_url, sheet_url):
    print("Step 1: Calling shopify_agent...")
   
    input_data = {
        "shopify_url": shopify_url,
        "sheet_url": sheet_url,
        
    } 

    stringify= json.dumps(input_data)
    # Print for debugging
    print(f"Running triage_agent with shopify_url={shopify_url} and sheet_url={sheet_url}")

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



#triage_agent

# triage_agent = Agent(
#    name="triage_agent",
#    instructions="""
#    1. Extract shopify_url & sheet_url.
#    2. Call scrape_shopify_collection → returns a dict {products: […]}.
#    3. Merge in sheet_url: {"sheet_url": X, "products": […]}.
#    4. Hand off to data_writer_agent.
#    """,
#    handoffs=[shopify_agent, data_writer_agent],
# )


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
