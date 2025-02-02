from openai import OpenAI
from browser_use import Agent
import asyncio
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()  

async def main():
    agent = Agent(
        task="Go to Reddit, search for 'browser-use', click on the first post and return the first comment.",
        llm=lambda prompt: client.chat.completions.create(
            model="grok-2-latest",
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": prompt}]
        ).choices[0].message.content 
    )

    result = await agent.run()
    print(result)

asyncio.run(main())
