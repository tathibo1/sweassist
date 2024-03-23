from rich.markdown import Markdown
from rich.panel import Panel
from oai_stream import EventHandler
from enum import Enum
import textwrap
import os
from dotenv import load_dotenv

class SweAssistInputModes(Enum):
    SINGLE_LINE = 's'
    MULTI_LINE = 'm'


class SweAssist():
    def __init__(self, client, thread, console) -> None:
        load_dotenv()
        self.stream_handler = EventHandler()
        self.client = client
        self.thread = thread
        self.user_input = ''
        self.input_mode = SweAssistInputModes.SINGLE_LINE.value
        self.console = console
        self.assistant_id = os.getenv("OPENAI_ASSISTANT_ID")
        self.prompt_prepend = os.getenv("SWEASSIST_PROMPT_PREPEND", default="Prompt")

    def prompt_user(self, on_new_line = True):
        maybe_new_line = "\n" if on_new_line else ""
        self.console.print(f"{maybe_new_line}{self.prompt_prepend} \[{self.input_mode}] >>>  ", style="dark_green", end='')
        return self


    def _get_user_input_single_line(self):
        self.user_input += input()
        return self


    def _get_user_input_multi_line(self):
        input_lines = []
        while True:
            user_input = input()
            if user_input.strip() == '':
                break
            input_lines.append(user_input)
        self.user_input += '\n'.join(input_lines)
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
        
        # TODO: raw_input + tab completion: https://stackoverflow.com/questions/5637124/tab-completion-in-pythons-raw-input
        if self.user_input.lower().startswith("\\r "):
            file_path = self.user_input.split(" ")[1]
            with open(file_path, 'r') as file:
                file_contents = file.read()
                message = textwrap.dedent(f"""
                    Please keep the following file contents in mind during our conversation.
                    They are from file {file_path}
                    Contents of file:
                """) + file_contents
                self.console.print(message)
                self._add_message(message)
            self.user_input = ""

        if self.user_input.strip() != "":
            self.console.print("...")
            return self._query()
    
        return self

    def _add_message(self, message: str):
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=message
        )

    def _query(self):
        self._add_message(self.user_input)
        with self.client.beta.threads.runs.create_and_stream(
            thread_id=self.thread.id,
            assistant_id=self.assistant_id,
            instructions="Please refer to the user as Tom. Please format all responses in markdown.",
            event_handler=self.stream_handler,
        ) as stream:
            stream.until_done()
        return self


    def _flush_buffers(self):
        self.stream_handler = EventHandler()
        self.user_input = ''


  # TODO: print partial stream periodically
    def print_response(self):
        if self.stream_handler.buffer != '':
            self.console.print( Panel(
                Markdown(self.stream_handler.buffer), title="", padding=1
            ))
            self._flush_buffers()
        return self