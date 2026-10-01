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

def prompt_recursive(console: Console, schema_properties: dict) -> dict:
    args = {}

    for key, details in schema_properties.items():
        excepted_type = details.get("type", "string")

        if excepted_type == "object" and "properties" in details:
            console.print(f"[bold cyan]--- Entering nested object: {key} ---[/bold cyan]")
            args[key] = prompt_recursive(details["properties"])
            console.print(f"[bold cyan]--- Exiting nested object: {key} ---[/bold cyan]")
        elif excepted_type == "integer":
            user_input = Prompt.ask(f"{key} (integer)")
            args[key] = int(user_input)
        elif excepted_type == "boolean":
            user_input = Prompt.ask(f"{key} (boolean)")
            args[key] = user_input.lower() in ["true", "t", "yes", "y", "1"]
        elif excepted_type == "array":
            user_input = Prompt.ask(f"{key} (comma-separated list)")
            args[key] = [x.strip() for x in user_input.split(",") if x.strip()]
        else:
            args[key] = Prompt.ask(f"{key} (string)")

    return args 

def make_tool_call(console: Console, tool) -> dict:
    args = {}

    # Prompting user for all tool args
    if tool.args is not None:
        args = prompt_recursive(console, tool.args)

    return {
        "name": tool.name,
        "args": args,
        "id": f"call_{uuid.uuid4().hex[:8]}"
    }

def create_message_panel(message: BaseMessage, title="Message") -> Panel:
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
            responses = []
            break

    return responses

# DEVELOPMENT
'''
from langchain_core.tools import tool
@tool
def think_tool(reflection: str) -> str:
    """Tool for strategic reflection on the simulation state and decision-making.

    Use this tool after each interaction with environment, other players or agents within your system and plan next steps systematically.
    This creates a deliberate pause in the planning process for quality decision-making.

    When to use:
    - After receiving the information from the environment: How does new information influences my plans?
    - Before making the final decision: Can I make well informed decision?
    
    Reflection should address:
    1. Analysis of the currently gathered information - What do I know about the problem at hand?
    2. Missing information assessment - What more information can I gather about the problem?
    3. Predicted consequences - What will be the result of considered possiblities?
    4. Strategic decision - Should I continue observing the environment or make the decision now?

    Args:
        reflection: Your detailed reflection on the problem at hand, findings, and next steps

    Returns:
        Confirmation that reflection was recorded for decision-making
    """

    return f"Reflection recorded: {reflection}"


from langchain_core.messages import SystemMessage, ToolMessage, AIMessage, HumanMessage
messages = [
    SystemMessage(content="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quisque consectetur varius lectus, et mollis mi viverra sed. Ut eu ante non tellus egestas tincidunt. Quisque ac dui sit amet est varius molestie. Maecenas quis tincidunt felis. Pellentesque vel aliquet ante, dapibus lobortis mi. Nulla ut ultricies tortor. Etiam vel molestie purus. Cras pulvinar, tellus eu scelerisque placerat, arcu purus sagittis nibh, eget faucibus ex nisi a dolor. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas."),
    HumanMessage(content="Vestibulum in quam nec dolor fringilla auctor. Maecenas tristique luctus odio, et semper ex congue ut. Nulla vehicula mollis ex, eu elementum tortor pharetra id. Etiam leo nibh, eleifend in elit sit amet, mattis interdum arcu. Praesent bibendum, diam sed varius hendrerit, tortor nulla lobortis mi, eget consequat risus enim eget dui. Interdum et malesuada fames ac ante ipsum primis in faucibus. Nullam et tincidunt neque. Vivamus in dui id lorem vestibulum maximus a ac mauris."),
    AIMessage(content="Sed pretium placerat tellus. Nunc neque turpis, dictum vel congue in, viverra ac ex. Curabitur ullamcorper orci ac laoreet cursus. Curabitur a malesuada purus, et ornare mi. Nullam faucibus sapien eget nisi iaculis ultricies. Fusce non laoreet urna, at tempor elit. Fusce in lectus arcu. Etiam laoreet massa quis metus scelerisque, a mollis libero porttitor. Vivamus sed quam nisl. Etiam egestas ultricies libero ut efficitur. In interdum vulputate magna nec feugiat. Cras tristique eu ante id congue. Suspendisse nec consectetur turpis. Morbi ligula nunc, auctor ornare nisl ut, volutpat sagittis mi. Sed sed nulla eleifend, euismod erat a, blandit sapien."),
    ToolMessage(tool_call_id="call_Jja7J89XsjrOLA5r!MEOW!SL", content="In orci ligula, porta euismod magna in, sollicitudin porttitor mi. In tincidunt felis commodo, vestibulum velit vel, varius justo. Sed nulla orci, blandit quis convallis a, scelerisque eget nunc. Nulla facilisis metus sed turpis luctus rhoncus. Etiam at nibh fermentum metus tincidunt tincidunt. Nunc vitae purus euismod, congue massa molestie, vehicula erat. Suspendisse facilisis pulvinar facilisis. Mauris mollis quis lacus ut mattis. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Duis odio felis, auctor sit amet tortor sed, fringilla imperdiet massa. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Fusce congue, risus ut euismod tempus, massa massa molestie justo, congue fermentum arcu magna quis orci. Duis faucibus mi leo, in tincidunt arcu fringilla ac. Praesent sed tortor sed ante egestas malesuada vel a enim. Vivamus id velit vestibulum, faucibus enim eget, ullamcorper massa."),
    ToolMessage(tool_call_id="call_Jja7J89XsjrOLA5r!MEOW!SL", content="Fusce non fermentum quam. Nulla facilisi. Aenean tempor tempus metus quis efficitur. Maecenas commodo congue diam sed viverra. Aenean et ante at ante feugiat suscipit. Nulla at dolor pharetra, sodales erat eu, gravida lorem. In aliquam ac ipsum sed posuere. Sed in ex porta, vehicula sem id, tempor ex. Maecenas efficitur velit fringilla dignissim sodales. Sed egestas erat id est auctor, vel finibus mi tincidunt. Cras mi ante, fringilla ut maximus in, mollis id purus. Cras faucibus iaculis pharetra. Maecenas efficitur urna sit amet sapien luctus, at suscipit tortor mattis."),
    AIMessage(additional_kwargs={"tool_calls": [{"id": "12345", "name": "super_tool", "args": {}}]}, content="Cras sed purus commodo, dignissim enim scelerisque, accumsan quam. Donec et quam vel magna tincidunt placerat. In eu neque dui. Etiam at faucibus velit. Phasellus mattis luctus vestibulum. Duis nisl massa, imperdiet quis pharetra ut, fermentum ut lacus. Cras convallis convallis condimentum. Praesent ultrices maximus felis in malesuada. Proin mollis quis leo et placerat. Proin ut felis laoreet, condimentum dolor et, aliquam quam. Duis euismod mi ac hendrerit rutrum. Fusce sed mi vel arcu suscipit molestie. Etiam feugiat ac tortor sit amet venenatis. Proin maximus sodales rhoncus. Donec luctus, tellus tristique sollicitudin mattis, nisl dui ultrices lectus, vitae vehicula massa felis at mauris. Suspendisse tincidunt dictum pharetra."),
    ToolMessage(tool_call_id="call_Jja7J89XsjrOLA5r!MEOW!SL", content="Nunc sollicitudin tempor urna, ut aliquet risus cursus a. In efficitur id odio quis posuere. Aliquam in nunc at quam molestie pretium. Phasellus a interdum risus, eget pulvinar sapien. Nunc a ex eu leo dictum finibus. Sed molestie nisl suscipit turpis commodo accumsan non eleifend felis. Aenean urna velit, finibus non posuere sed, vestibulum non risus. Sed dui orci, aliquet eu imperdiet lobortis, sodales vitae felis. Integer nulla nisl, volutpat finibus mauris vitae, maximus tempor nisl. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Fusce eu tincidunt est. In aliquam est quis massa laoreet, in dapibus erat convallis. Nullam aliquam, mauris vitae cursus elementum, tortor felis consequat nisl, eget malesuada velit leo non tellus. Praesent accumsan erat ac volutpat tincidunt."),
    ToolMessage(tool_call_id="call_Jja7J89XsjrOLA5r!MEOW!SL", content="Pellentesque eget mauris vel orci sodales sagittis ut nec tellus. Morbi vel felis et nisi aliquet facilisis eu eget odio. Aliquam metus nulla, auctor a sagittis et, porta tristique enim. Vestibulum quis nisi vitae libero porttitor sagittis. In rhoncus felis nulla, non egestas nisi tincidunt et. Mauris imperdiet nibh eget suscipit rhoncus. Cras gravida nibh eget justo efficitur euismod. Aliquam urna mauris, aliquam et erat eu, accumsan vehicula ligula. Mauris sit amet mi neque. Fusce eget turpis vitae turpis lobortis vehicula quis sit amet velit."),
    ToolMessage(tool_call_id="call_Jja7J89XsjrOLA5r!MEOW!SL", content="Curabitur id mi et tortor ultrices posuere sit amet vitae mi. Quisque eu quam sed orci finibus efficitur in et mauris. Vivamus varius, est sit amet scelerisque pharetra, arcu ligula viverra nunc, suscipit pellentesque urna justo vel justo. Pellentesque lobortis fermentum nisi vitae volutpat. Praesent cursus, elit in feugiat facilisis, felis augue ultrices ipsum, in lacinia leo tellus nec augue. Sed vel velit ut risus scelerisque euismod id ut purus. Quisque vulputate interdum mauris non malesuada. Suspendisse non dolor ut erat luctus cursus sed eget nisl. Mauris maximus lorem sit amet mi finibus, tincidunt mollis tellus gravida. Cras scelerisque dolor pulvinar nisl molestie, sit amet congue justo lobortis. Quisque et pulvinar turpis, sit amet luctus sapien. Vestibulum vulputate efficitur mauris, sed fringilla enim dapibus nec. Nam at mi posuere, finibus nulla ut, eleifend ligula."),
    AIMessage(content="Ut in orci scelerisque, consectetur augue quis, blandit lacus. Mauris consequat, lorem eget aliquet viverra, lorem nibh suscipit nunc, at rhoncus purus purus sed eros. Etiam tempor urna et lobortis porta. Curabitur purus velit, consequat sed nisi in, volutpat accumsan velit. Sed luctus mattis consectetur. Aenean eu laoreet erat, vitae eleifend nisi. Nullam maximus porttitor nisl ut efficitur. In ligula risus, fermentum nec elit ac, aliquet dapibus lacus."),
    HumanMessage(content="Quisque vel accumsan est. Curabitur nibh augue, accumsan id neque eget, vestibulum euismod ante. Maecenas malesuada maximus arcu et hendrerit. Sed sollicitudin, tellus ac maximus porta, libero erat aliquet justo, sed volutpat ipsum nisl id justo. Vestibulum eu ipsum et libero efficitur facilisis. Mauris eleifend dictum tempus. Mauris id nisi quam. Donec consectetur finibus pharetra. Phasellus et pulvinar velit. Sed ac blandit leo. Nulla facilisi. Nam sit amet mauris euismod, consequat turpis at, volutpat ex. Sed sit amet libero facilisis, porta leo non, volutpat leo. Proin non pulvinar elit. Fusce sollicitudin ligula ac metus sollicitudin cursus."),
    AIMessage(content="Vestibulum ornare volutpat lectus id bibendum. Proin cursus at nisl id placerat. Aliquam dignissim placerat porttitor. Phasellus eget enim at mauris semper mollis sit amet eu felis. Nulla non mauris id tellus faucibus posuere. Ut orci eros, convallis in orci ut, molestie rutrum est. Sed consectetur, turpis sit amet volutpat placerat, purus magna luctus justo, quis feugiat tellus leo et enim. Curabitur nunc orci, porttitor non suscipit in, iaculis non neque. Nam et libero sapien.")
]
agent_name="Leader Agent"
tools = [think_tool]


human(messages, agent_name, tools=tools)
'''