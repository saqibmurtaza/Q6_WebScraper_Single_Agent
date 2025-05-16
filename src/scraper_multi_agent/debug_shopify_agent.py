from agents import Agent, Runner
from scraper_multi_agent.config_agents import config
from scraper_multi_agent.multi_agents import shopify_agent

shopify_url = "https://maguireshoes.com/collections/heels"

async def debug_shopify_agent():
    input_data = shopify_url  # just the URL as string
    print(f"Sending input to shopify_agent: {input_data}")
    
    result = await Runner.run(
        shopify_agent,
        input=input_data,
        run_config=config
    )

    print("Raw result from shopify_agent:", result)

# Run the debug function instead of the triage agent
if __name__ == "__main__":
    import asyncio
    asyncio.run(debug_shopify_agent())
