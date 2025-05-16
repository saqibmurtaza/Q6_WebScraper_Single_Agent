import chainlit as cl, json
from scraper_multi_agent.single_agent import main


@cl.on_chat_start
async def on_start():
    await cl.Message(
        content=(
            "👋 Welcome! This app scrapes **one type of Shopify store** only.\n\n"
            "🔍 Try multi-page scraping and save results to Google Sheets using this test URL:\n"
            "👉 https://maguireshoes.com\n\n"
            "🧪 To get started, enter your input in this format:\n"
            "```text\n"
            "https://your-shopify-url.com/collections/... | https://docs.google.com/spreadsheets/...\n"
            "```"
        )
    ).send()

@cl.on_message
async def handle_message(message: cl.Message):
    try:
        if "|" not in message.content:
            await cl.Message(
                content=(
                    "❗ Please provide input in the format:\n\n"
                    "`<shopify_url> | <google_sheet_url>`\n\n"
                    "**Example:**\n"
                    "`https://maguireshoes.com/collections/heels | https://docs.google.com/spreadsheets/...`"
                )
            ).send()
            return

        # Split input on '|'
        shopify_url, sheet_url = map(str.strip, message.content.split("|", 1))

        await cl.Message(content="⏳ Scraping products and saving to Google Sheets...").send()

        # Call your agent
        result = await main(shopify_url, sheet_url)

        # Format result
        pretty_result = json.dumps(result, indent=2) if isinstance(result, dict) else result

        await cl.Message(
            content=(
                f"✅ **Scraping completed!**\n\n"
                f"🔗 **Shopify URL:** {shopify_url}\n"
                f"📄 **Google Sheet:** {sheet_url}\n\n"
                f"📝 **Result:**\n{pretty_result}"
            )
        ).send()

    except Exception as e:
        await cl.Message(content=f"❌ Error: {str(e)}").send()


