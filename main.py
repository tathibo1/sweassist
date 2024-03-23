from openai import OpenAI
from rich.console import Console
from swe_assist import SweAssist

client = OpenAI()
thread = client.beta.threads.create()
console = Console()


def main_loop(client, thread, console):
    sa = SweAssist(client, thread, console)
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