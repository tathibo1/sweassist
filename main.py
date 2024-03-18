import os
from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from oai_stream import EventHandler

load_dotenv()
ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")

client = OpenAI()
thread = client.beta.threads.create()
console = Console()

try:
  while True:
    event_handler = EventHandler()
    console.print(f"\nPrompt >>> ", style="dark_green", end='')
    user_input = input()
    

    if user_input.strip() != "":
      message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input
      )

      # Streaming Response TODO: show partial results using Markdown
      with client.beta.threads.runs.create_and_stream(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID,
        instructions="Please refer to the user as Tom. Please format all responses in markdown.",
        event_handler=event_handler,
      ) as stream:
        stream.until_done()

      console.print(
        Panel(
          Markdown(event_handler.buffer), title="", padding=1
        )
      )
except KeyboardInterrupt:
  console.print("\nGoodbye!")