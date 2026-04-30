"""
title: Mistral Chat Completions Thinking Exposure
description: Filter exposes Mistral Chat Completions API reasoning in the response stream by wrapping thinking output in <think> tags. It can also append a configurable reminder to user messages at a chosen interval, helping reinforce system instructions during longer conversations.
author: Kylapaallikko
author_url: https://github.com/Kylapaallikko
version: 1.1
license: MIT
"""

from pydantic import BaseModel, Field
from typing import Optional

class Filter:
    class Valves(BaseModel):
        priority: int = Field(
            default=0, description="Priority level for the filter operations."
        )
        debug: bool = Field(False, description="Print debug messages into the logs.")
        reminder : bool = Field(False, description="Use the reminder message")
        reminder_text: str = Field("", description="Remind LLM every x message")
        reminder_frequency: int = Field(2, description="Append reminder every x message")

    def __init__(self):
        # Indicates custom file handling logic. This flag helps disengage default routines in favor of custom
        # implementations, informing the WebUI to defer file-related operations to designated methods within this class.
        # Alternatively, you can remove the files directly from the body in from the inlet hook
        self.valves = self.Valves()
        self.ids = [] # Thinking event_id(s)


    async def inlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        # Modify the request body or validate it before processing by the chat completion API.
        # This function is the pre-processor for the API where various checks on the input can be performed.
        # It can also modify the request before sending it to the API.
        
        # Remind the reasoner every x messages.
        if self.valves.reminder and (len(body["messages"]) + 1) % self.valves.reminder_frequency == 0:
            last_message = body["messages"][-1]["content"]
            
            # Attached file in the message
            if isinstance(last_message, list):
                for item in last_message:
                    item_type = item.get("type", None)
                    if item_type == "text":
                        item["text"] += f"\n\n{self.valves.reminder_text}"
            else:
                body["messages"][-1]["content"] = f'{last_message}\n\n{self.valves.reminder_text}'
            # DEBUG
            if self.valves.debug:
                print(f'REMINDER ({len(body["messages"])}): {self.valves.reminder_text}')

        return body

    async def stream(self, event: dict) -> dict:
        event_id = event.get("id")
        
        # Debug
        if self.valves.debug:
            print(event)  # Print each incoming chunk for inspection
        
        for choice in event.get("choices", []):
            delta = choice.get("delta", {})
            
            # Stops thinking on tool call
            if choice.get("finish_reason", None) == "tool_calls":
                if event_id in self.ids:
                    delta["content"] = "</think>\n"
                    self.ids.remove(event_id)

            # If no content present. Skip.
            if not delta.get("content", ""):
                continue
            
            output_text = []
        
            if isinstance(delta["content"], list):
                for item in delta["content"]:
                    if item["type"] == "thinking":
                        if not event_id in self.ids:
                            self.ids.append(event_id)
                            output_text.append(f'<think>\n')
                        output_text.append(item["thinking"][0]["text"])
                    else:
                        output_text.append(item)
            else:
                # "normal" response begin. Reset thinking status.
                if event_id in self.ids:
                    output_text.append(f'</think>\n{delta["content"]}')
                    self.ids.remove(event_id)
            
            if output_text:
                delta["content"] = "".join(output_text)
                    
        return event
    
    async def outlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        # Modify or analyze the response body after processing by the API.
        # This function is the post-processor for the API, which can be used to modify the response
        # or perform additional checks and analytics.
        self.ids = [] # Reset id(s)
        return body
