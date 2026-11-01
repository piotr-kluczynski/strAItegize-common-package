from typing import Literal
from langchain_core.tools import tool
from strAItegize_common.client.game_rules_store import RULES_CATEGORIES, rules_store

from strAItegize_common.client.communication.communication_context import CommunicationContext
from strAItegize_common.communication.message_types import MessageType

def get_generic_tools(communication: CommunicationContext) -> list:
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

    @tool
    def observe_unit(unit_id: str) -> str:
        """Observe the surroundings around owned unit with given id.

        Args:
            unit_id: Identifier of the unit to observe.

        Returns:
            Textual description of the surroundings within distance of 2 tiles from the unit.
        """

        # Retrieving the description of unit surroundings from the simulation.
        data = communication.request_data(
            request_type = MessageType.ObserveUnit,
            request_args = {"unit_id": unit_id}
        )

        if isinstance(data, dict):
            if data.get("error"):
                return f"An error has occurred during tool execution.\r\nDescription: {data["desc"]}\r\nDetails: {data['details']}"

        # Formatting the tool output to be more readable for the LLM
        if len(data.observations) > 0:
            observation = f"Your unit: {unit_id} observes the following tiles:"
            for tile_coord, tile_data in data.observations.items():
                observation += f"- Tile ({tile_coord}) belongs to the region: {tile_data.region}, owned by player: {tile_data.owner}"

                if tile_data.unit != "Empty":
                    observation += f", is occupied by unit: {tile_data.unit}"
                    
                    if tile_data.unit == unit_id:
                        observation += f" (your unit's tile)"

                if tile_data.is_command_center:
                    observation += ', is the command center of its region'        

                observation += f", and is {tile_data.distance} units away (coords relative to your unit: {tile_data.rel_coord}).\r\n"
        else:
            observation = f"The unit: {unit_id} could not observe its surrounding tiles."

        return observation

    @tool
    def observe_region(region_id: str) -> str:
        """Observe the terrain of the owned region with given id.

        Args:
            unit_id: Identifier of the region to observe.

        Returns:
            Textual description of the entire region.
        """

        # Retrieving the description of region terrain from the simulation.
        data = communication.request_data(
            request_type = MessageType.ObserveRegion,
            request_args = {"region_id": region_id}
        )

        if isinstance(data, dict):
            if data.get("error"):
                return f"An error has occurred during tool execution.\r\nDescription: {data["desc"]}\r\nDetails: {data['details']}"

        # Formatting the tool output to be more readable for the LLM
        if len(data.observations) > 0:
            observation = f"The citizens of your region: {region_id} observe the following tiles:"
            for tile_coord, tile_data in data.observations.items():
                observation += f"- Tile ({tile_coord}) belongs to the region: {tile_data.region}, owned by player: {tile_data.owner}"

                if tile_data.unit != "Empty":
                    observation += f", is occupied by unit: {tile_data.unit}"

                if tile_data.is_command_center:
                    observation += ', is the command center of its region'   

                observation += f", and is {tile_data.distance} units away (coords relative to the region's command center: {tile_data.rel_coord}).\r\n"
        else:
            observation = f"The region: {region_id}'s tiles could not be observed."

        return observation

    @tool
    def get_units() -> list[str]:
        """Reads the list of all unit controlled by the player.

        Returns:
            List containing the identifiers of all controlled units.    
        """

        # Retrieving the uint list from the simulation.
        data = communication.request_data(
            request_type = MessageType.GetUnits,
            request_args = None
        )

        if isinstance(data, dict):
            if data.get("error"):
                return f"An error has occurred during tool execution.\r\nDescription: {data["desc"]}\r\nDetails: {data['details']}"

        unit_list = data.units_list

        # Formatting the tool output to be more readable for the LLM
        if len(unit_list) > 0:
            observation = "Units under your control:"
            for unit in unit_list:
                observation += f", {unit}"

            observation += "."
        else:
            observation = "There are no units under your control."

        return observation

    @tool
    def get_regions() -> list[str]:
        """Reads the list of all regions controlled by the player.

        Returns:
            List containing the identifiers of all controlled regions.    
        """

        # Retrieving the uint list from the simulation.
        data = communication.request_data(
            request_type = MessageType.GetRegions,
            request_args = None
        )

        if isinstance(data, dict):
            if data.get("error"):
                return f"An error has occurred during tool execution.\r\nDescription: {data["desc"]}\r\nDetails: {data['details']}"

        # Formatting the tool output to be more readable for the LLM
        if len(data.regions_list) > 0:
            observation = "Regions under your control:"
            for region in data.regions_list:
                observation += f", {region}"
            observation += "."
        else:
            observation = "You control no regions within the simulation. You shouldn't be here."

        return observation

    @tool
    def get_unit_details(unit_id: str) -> str:
        """Read the parameters, such as strength and speed, of any unit with given id.
        
        Args:
            unit_id: Identifier of the unit to analyze.

        Returns:
            Textual description of the unit's parameters.
        """

        # Retrieving the unit description from the simulation.
        data = communication.request_data(
            request_type = MessageType.GetUnitDetails,
            request_args = {"unit_id": unit_id}
        )

        if isinstance(data, dict):
            if data.get("error"):
                return f"An error has occurred during tool execution.\r\nDescription: {data["desc"]}\r\nDetails: {data['details']}"

        # Formatting the tool output to be more readable for the LLM
        observation = f"""
        Unit {unit_id} has the following parameters:
        - Position:    {data.coord};
        - Owner:       {data.owner};
        - Movement:    {data.movement};
        - Strength:    {data.strength};
        - Upkeep Cost: {data.upkeep}.
        """

        return observation

    @tool
    def get_region_details(region_id: str) -> str:
        """Read the parameters, such as region's owner, supply income, etc., of any region with given region id.

        Args:
            region_id: Identifier of the region to analyze.
        
        Returns:
            Textual description of the region's parameters.
        """

        # Retrieving the region's description from the simulation.
        data = communication.request_data(
            request_type=MessageType.GetRegionDetails,
            request_args={"region_id": region_id}
        )

        if isinstance(data, dict):
            if data.get("error"):
                return f"An error has occurred during tool execution.\r\nDescription: {data["desc"]}\r\nDetails: {data['details']}"

        # Formatting the tool output to be more readable for the LLM
        neighbours_str = ", ".join(data.neighbour_regions) if data.neighbour_regions else "None"
        observation = f"""
        Region {region_id} parameters:
        - Owner:                   {data.owner}
        - Command Center Position: {data.command_center_coord}
        - Size:                    {data.size}
        - Neighbouring Regions:    {neighbours_str}.
        """

        return observation

    @tool
    def get_game_rules(category: Literal[*RULES_CATEGORIES], question: str) -> str:
        """Read the rules of the simulation about the chosen subject.
        
        Args:
            category: The category of the query regarding the game rules. Existing categories: Game Map, Units, Player Actions, Combat System, Round Details, Economy and Upkeep, Player Elimination, Simulation End Conditions.
            question: The question about the simulation rules.
        
        Returns:
            Game rules explaining the given topic.
        """

        query_results = rules_store.similarity_search(
            question,
            k = 3,
            filter={"category": category}
        )

        # Formatting the tool output to be more readable for the LLM
        if len(query_results) > 0:
            observation = "The game facts retrieved from the game rules vector store:"
            for result in query_results:
                observation += f"- {result}\r\n"
        else:
            observation = "No game rules were found, associated with given topic."

        return observation

    return [think_tool, observe_unit, observe_region, get_units, get_regions, get_unit_details, get_region_details, get_game_rules]
