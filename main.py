import os
from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from oai_stream import EventHandler
from enum import Enum

load_dotenv()
ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")

client = OpenAI()
thread = client.beta.threads.create()
console = Console()

class SweAssistInputModes(Enum):
  SINGLE_LINE = 's'
  MULTI_LINE = 'm'

class SweAssist():
  def __init__(self, client, thread, console) -> None:
    self.stream_handler = EventHandler()
    self.client = client
    self.thread = thread
    self.user_input = ''
    self.input_mode = SweAssistInputModes.SINGLE_LINE.value
    self.console = console

  def prompt_user(self, on_new_line = True):
    maybe_new_line = "\n" if on_new_line else ""
    console.print(f"{maybe_new_line}Prompt \[{self.input_mode}] >>>  ", style="dark_green", end='')
    return self


  def _get_user_input_single_line(self):
    self.user_input = input()
    return self


  # TODO: can this be done without needing to press enter with an empty line?
  def _get_user_input_multi_line(self):
    input_lines = []
    while True:
      user_input = input()
      if user_input.strip() == '':
        break
      input_lines.append(user_input)
    self.user_input = '\n'.join(input_lines)
    return self


  def get_user_input(self):
    if self.input_mode == SweAssistInputModes.SINGLE_LINE.value:
      return self._get_user_input_single_line()
    else:
      return self._get_user_input_multi_line()

  
  def handle_user_input(self):
    if self.user_input.strip() == "im":
      if self.input_mode == SweAssistInputModes.SINGLE_LINE.value:
        self.input_mode = SweAssistInputModes.MULTI_LINE.value
      else:
        self.input_mode = SweAssistInputModes.SINGLE_LINE.value
      self.user_input = ""
    
    if self.user_input.strip() != "":
      console.print("...thinking")
      return self._query()
    
    return self


  def _query(self):
    self.client.beta.threads.messages.create(
      thread_id=self.thread.id,
      role="user",
      content=self.user_input
    )
    with self.client.beta.threads.runs.create_and_stream(
      thread_id=self.thread.id,
      assistant_id=ASSISTANT_ID,
      instructions="Please refer to the user as Tom. Please format all responses in markdown.",
      event_handler=self.stream_handler,
    ) as stream:
      stream.until_done()
    return self


  # TODO: print partial stream periodically
  def print_response(self):
    if self.stream_handler.buffer != '':
      console.print(
          Panel(
            Markdown(self.stream_handler.buffer), title="", padding=1
          )
        )
      self.stream_handler = EventHandler()
    return self


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