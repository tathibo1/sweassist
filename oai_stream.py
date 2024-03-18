from openai import AssistantEventHandler
from typing_extensions import override

class EventHandler(AssistantEventHandler):
  def __init__(self):
    super().__init__()
    self.buffer = ""

  @override
  def on_text_created(self, text) -> None:
    pass
        
  @override
  def on_text_delta(self, delta, snapshot):
    self.buffer += delta.value
      
  def on_tool_call_created(self, tool_call):
    self.buffer += tool_call.type
  
  def on_tool_call_delta(self, delta, snapshot):
    if delta.type == 'code_interpreter':
      if delta.code_interpreter.input:
        self.buffer += delta.code_interpreter.input
      if delta.code_interpreter.outputs:
        self.buffer += "\n\noutput >"
        for output in delta.code_interpreter.outputs:
          if output.type == "logs":
            self.buffer += f"\n{output.logs}"