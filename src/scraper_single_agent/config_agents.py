from agents import (
    Agent, 
    Runner,
    AsyncOpenAI,
    set_tracing_disabled, OpenAIChatCompletionsModel)
from agents.run import RunConfig
from dotenv import load_dotenv
import os

load_dotenv()

base_url = os.getenv("BASE_URL") or ""
api_key = os.getenv("API_KEY") or "your_api_key"
model_name= os.getenv("MODEL_NAME") or ""

set_tracing_disabled(True)

external_client= AsyncOpenAI(
    base_url=base_url,
    api_key=api_key,
)

model = OpenAIChatCompletionsModel(
    model=model_name,
    openai_client=external_client,
)

config= RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True,
)

agent: Agent= Agent(
    name="Assistant",
    instructions="You are a helpful assistant.",
)

async def run_agent():
    result= await Runner.run(
        agent,
        input="who are you?",
        run_config=config,
    )
    print(result)



if __name__ == "__main__":
    import asyncio
    asyncio.run(run_agent())