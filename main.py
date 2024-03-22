import os
from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
from swe_assist import SweAssist

load_dotenv()
assistant_id = os.getenv("OPENAI_ASSISTANT_ID")

client = OpenAI()
thread = client.beta.threads.create()
console = Console()


def main_loop(client, thread, console):
    sa = SweAssist(client, thread, console, assistant_id)
    try:
        while True: (
            sa.prompt_user()
              .get_user_input()
              .handle_user_input()
              .print_response()
        )

    except KeyboardInterrupt:
        console.print("\nGoodbye!")


main_loop(client, thread, console)