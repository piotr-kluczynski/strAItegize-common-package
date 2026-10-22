import os
import uuid

from rich.console import Console, Group
from rich.rule import Rule
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.table import Table

from typing import Optional
from langchain_core.messages import BaseMessage, AIMessage

def prompt_recursive(console: Console, schema: dict, defs: dict = None) -> dict:
    """
    Function for recursively prompting user each of the arguments required by the schema.

    Args:
    - console: Console - object from rich library used for managing the console screen content,
    - schema: dict - schematic containing all data required from the user,
    - defs: dict - dictionary containing all complex object schematics, referenced in the original schema.

    Returns:
    filled_schema: dict - dictionary containing keys from the provided schema, and values given by the user.
    """
    schema_properties = schema["properties"]
    args = {}

    # Storing definitions of nested objects (pydantic flattens the nested definitions)
    if defs is None:
        defs = schema.get("$defs", {})

    for key, details in schema_properties.items():
        # Handling Optional values (None by default)
        is_optional = "default" in details or any(t.get("type") == "null" for t in details.get("anyOf", []))

        if "anyOf" in details:
            types = [t.get("type") for t in details["anyOf"] if t.get("type") != "null"]
            excepted_type = types[0] if types else "string"
        else:
            excepted_type = details.get("type", "string")

        ref_str = details.get("$ref")
        if not ref_str and "allOf" in details:
            ref_str = details["allOf"][0].get("$ref")

        if ref_str:
            console.print(f"[bold cyan]--- Entering nested object: {key} ---[/bold cyan]")

            # Retrieving the proper object properties from $defs
            nested_obj_name = ref_str.split("/")[-1]
            nested_obj_schema = defs[nested_obj_name]
    
            args[key] = prompt_recursive(console, nested_obj_schema, defs=defs)
            
            console.print(f"[bold cyan]--- Exiting nested object: {key} ---[/bold cyan]")
        elif excepted_type == "integer":
            prompt_label = f"{key} (integer, optional)" if is_optional else f"{key} (integer)"

            user_input = Prompt.ask(prompt_label)
            if is_optional and user_input == "":
                args[key] = None
            else:
                args[key] = int(user_input)
        elif excepted_type == "boolean":
            prompt_label = f"{key} (boolean, optional)" if is_optional else f"{key} (boolean)"

            user_input = Prompt.ask(prompt_label)
            if is_optional and user_input == "":
                args[key] = None
            else:
                args[key] = user_input.lower() in ["true", "t", "yes", "y", "1"]
        elif excepted_type == "array":
            prompt_label = f"{key} (comma-separated list, optional)" if is_optional else f"{key} (comma-separated list)"

            user_input = Prompt.ask(prompt_label)
            if is_optional and user_input == "":
                args[key] = None
            else:
                args[key] = [x.strip() for x in user_input.split(",") if x.strip()]
        else:
            prompt_label = f"{key} (string, optional)" if is_optional else f"{key} (string)"

            user_input = Prompt.ask(prompt_label)
            if is_optional and user_input == "":
                args[key] = None
            else:
                args[key] = user_input

    return args 

def make_tool_call(console: Console, tool) -> dict:
    """
    Function starting the tool call creation process, allowing user to fill in necessary arguments 
    via interface provided by prompt_recursive.

    Args:
    - console: Console - object from rich library used for managing the console screen content,
    - tool: tool object that needs to be called by the user.

    Returns:
    filled_schema: dict - dictionary containing keys from the tool arguments schema, and values given by the user.
    """
    args = {}

    # Prompting user for all tool args
    if tool.args:
        schema = getattr(tool, "tool_call_schema", tool.get_input_schema()).model_json_schema()
        args = prompt_recursive(console, schema)

    return {
        "name": tool.name,
        "args": args,
        "id": f"call_{uuid.uuid4().hex[:8]}"
    }

def create_message_panel(message: BaseMessage, title="Message") -> Panel:
    """
    Function for creating standard message panel, changing its characteristics 
    (e.g.: frame colour, box title) depending on the message type.

    Args:
    - message: BaseMessage - message object from which data will be displayed in the message panel,
    - title: str - text displayed on top of the message box.

    Returns:
    message_panel: Panel - object from rich library that can be displayed on the console screen.
    """
    messgage_content = Markdown(message.content)
    panel_colour = "magenta" if message.type == "ai" else ("green" if message.type == "tool" else ("cyan" if message.type == "system" else "rosy_brown"))
    
    # Displaying tool calls if there are any
    if message.type == "ai":
        if len(message.tool_calls) > 0:
            tool_calls_table = Table()
        
            tool_calls_table.add_column("Id", justify="right", style="magenta")
            tool_calls_table.add_column("Name", justify="center", style="green")
            tool_calls_table.add_column("Arguments", justify="center", style="rosy_brown")
        
            for tool_call in message.tool_calls:
                tool_calls_table.add_row(tool_call["id"], tool_call["name"], str(tool_call["args"]))
        
        
            message_group = Group(
                messgage_content,
                "",
                tool_calls_table
            )
        else:
            message_group = Group(
                messgage_content
            )
    else:
        message_group = Group(
            messgage_content
        )

    return Panel(
        message_group,
        title=title,
        border_style=panel_colour
    )

def respond(console: Console, agent_name, response_msg_content="", response_msg_tool_calls=[], tools=[]) -> Optional[AIMessage]:
    """
    Function used to construct the AIMessage to add the user's response to the list of agent messages, 
    as if they were an AI agent participating in the simulation.

    Args:
    - console: Console - object from rich library used for managing the console screen content,
    - agent_name: str - the agent identifier, used to distinguish it from other agents within the MAS, 
    - response_msg_content: str - already existing content of the message (in case of editing the response),
    - response_msg_tool_call: list - already existing list of tool calls (in case of editing the response),
    - tools: list - tools available to be used by this agent.

    Returns:
    ai_message: AIMessage - message object created by the user.
    """
    content = response_msg_content
    tool_calls = response_msg_tool_calls

    tools_by_names = {tool.name: tool for tool in tools}

    while True:
        os.system("cls")

        # Header
        header = Rule(title=agent_name, style="bold red")
        console.print(header)

        # List of available tools
        tools_table = Table()

        tools_table.add_column("Name", justify="right", style="green", no_wrap=True)
        tools_table.add_column("Description", justify="center", style="magenta")
        tools_table.add_column("Arguments", justify="right", style="rosy_brown")

        for tool in tools:
            tools_table.add_row(tool.name, tool.description, str(tool.args))

        tools_panel = Panel(
            tools_table,
            title="Available Tools",
            border_style="hot_pink"
        )

        console.print(tools_panel)

        # Current state of the response
        tool_calls_table = Table()

        tool_calls_table.add_column("Id", justify="right", style="magenta")
        tool_calls_table.add_column("Name", justify="center", style="green")
        tool_calls_table.add_column("Arguments", justify="center", style="rosy_brown")

        for tool_call in tool_calls:
            tool_calls_table.add_row(tool_call["id"], tool_call["name"], str(tool_call["args"]))

        response_content = Group(
            Rule(title="Content", align="left"),
            Markdown(content),
            "",
            Rule(title="Tool Calls", align="left"),
            tool_calls_table
        )
        
        response_panel = Panel(
            response_content,
            title="Message",
            border_style="hot_pink"
        )

        console.print(response_panel)

        # Interface for choosing the tool/to write the message content/cancel
        choices = list(tools_by_names.keys())
        choices.append("Edit Content")

        if len(tool_calls) > 0:
            choices.append("Remove Tool Call")

        choices.append("Confirm")
        choices.append("Cancel")

        decision = Prompt.ask("Choose your option", choices=choices)

        if decision == "Confirm":
            break
        elif decision == "Cancel":
            return None
        elif decision == "Edit Content":
            content = Prompt.ask("Enter the content of the message")
            continue
        elif decision == "Remove Tool Call":
            tool_call_choices = [tool_call["id"] for tool_call in tool_calls]
            tool_call_id = Prompt.ask("Enter tool_call id to remove it", choices=tool_call_choices)

            tool_calls = [tool_call for tool_call in tool_calls if tool_call.get("id") != tool_call_id]
            continue
        else: # Tool Call
            tool_calls.append(make_tool_call(console, tools_by_names[decision]))
            continue

    return AIMessage(
        content=content,
        tool_calls=tool_calls
    )

def human(messages: list[BaseMessage], agent_name: str, tools:list =[], msg_list_length: int=5) -> list[BaseMessage]:
    """
    Function allowing user to emulate the functioning of an LLM, and return appropriate AIMessage objects.
    Displays console user interface, to display previously sent or received messages.
    Used for debugging the Multi-Agent Systems, by supplying this function instead of an agent node.

    Args:
    - messages: list[BaseMessage] - list of message objects already existing on this agent's log,
    - agent_name: str - the agent identifier, used to distinguish it from other agents within the MAS,
    - tools: list - tools available to be used by this agent, 
    - msg_list_length: int - number of messages that can be displayed at the same time on the same console screen.

    Returns:
    message_list: list[BaseMessage] - list containing nlanggraph message objects added by the user.
    """
    console = Console()
    responses = []
    bottom_range=max(0, len(messages) - msg_list_length)
    top_range=len(messages)


    while True:
        os.system('cls')

        # Header
        header = Rule(title=agent_name, style="bold red")
        console.print(header)

        # List of previous messages
        message_panels = []
        for message in messages[bottom_range:top_range]:
            message_panels.append(create_message_panel(
                message=message,
                title=message.type
            ))

        messages_group = Group(*message_panels)

        messages_panel = Panel(
            messages_group,
            title="Message History",
            border_style="hot_pink"
        )
        console.print(messages_panel)

        # List of user responses 
        responses_panels = []
    
        for i in range(len(responses)):
            responses_panels.append(create_message_panel(responses[i], f"Response no. {i}"))


        responses_group = Group(*responses_panels)

        responses_panel = Panel(
            responses_group,
            title="Responses",
            border_style="hot_pink"
        )
        console.print(responses_panel)

        # Calculating how many prev/next messages we can view
        prev_messages_left = min(msg_list_length, bottom_range)
        next_messages_left = min(len(messages)-top_range, msg_list_length)

        choices = []
        if prev_messages_left != 0:
            choices.append("Previous")
        if next_messages_left != 0:
            choices.append(f"Next")

        if len(responses) > 0:
            choices.append("Edit Response")
            choices.append("Remove Response")
            choices.append("Send")

        choices.append("Respond")
        choices.append("Close")

        decision = Prompt.ask("Choose your option", choices=choices)

        if decision == "Previous":
            bottom_range -= prev_messages_left
            top_range -= prev_messages_left
        elif decision == "Next":
            top_range += next_messages_left
            bottom_range += next_messages_left
        elif decision == "Edit Response":
            response_choices = [str(i) for i in range(len(responses))]
            response_id = Prompt.ask("Enter response id to edit it", choices=response_choices)

            edited_response = respond(console=console, agent_name=agent_name, tools=tools, response_msg_content=responses[int(response_id)].content, response_msg_tool_calls=responses[int(response_id)].tool_calls)

            responses[int(response_id)] = edited_response if edited_response is not None else responses[int(response_id)]
            continue
        elif decision == "Remove Response":
            response_choices = [str(i) for i in range(len(responses))]
            response_id = Prompt.ask("Enter response id to remove it", choices=response_choices)

            del responses[int(response_id)]
            continue
        elif decision == "Respond":
            response = respond(console=console, agent_name=agent_name, tools=tools, response_msg_content="", response_msg_tool_calls=[])
            if response is not None:
                responses.append(response)
            continue
        elif decision == "Send":
            break
        elif decision == "Close":
            responses = [AIMessage(content="", tool_calls=[])]
            break

    return responses
