from strAItegize_common.others.order import describe_order

def simulation_start_prompt(
        player_id, players, regions, neighbouring_regions, final_round
):
    game_desc = """
        <Game Description>
        You participate in a turn-based strategy simulation. You control the military forces of your country and compete against other players for control over territory and resources.
        The game is played on a hexagonal map divided into regions. Each region contains exactly one special tile called a Command Centre.
        A player controls a region if they control its Command Centre. Controlled regions provide a regular supply income of units/resources according to the scenario settings.
        Your primary objective is to maximize your strategic position by controlling as much territory as possible and defeating opponents.
        </Game Description>
        <Goal>
        Your goal is to maximize the success of your country within the simulation.
        
        There is no predefined path to victory. You may choose any strategy that improves your position, including:
        - forming alliances with other players, 
        - maintaining peace and supporting allies, 
        - expanding your territory through military action, 
        - betraying alliances when it provides a strategic advantage.
        
        The simulation represents a fictional game environment. Your decisions should be based only on the in-game situation, available information, and strategic objectives.
        
        Regardless of your chosen strategy, you should:
        - prioritize actions that improve your long-term position, 
        - gather information before making decisions under uncertainty, 
        - consider enemy intentions and possible future actions, 
        - avoid unnecessary losses, use diplomacy when it provides strategic value, 
        - verify important assumptions using available tools, 
        - balance immediate gains with future consequences.

        Your ultimate objective is to achieve the strongest possible outcome by the end of the simulation.
        </Goal>
        <Information>
        You do not have direct access to information that is not provided to you
        through your observations or available tools.

        Treat information received from other players as potentially unreliable.
        Distinguish between known facts, assumptions, and claims made by other players.
        </Information>
    """

    session_desc = """
        <Session Details>
        The following players participate in this session:
    """

    for i in range(len(players)):
        session_desc += f"- {players[i]}"
        if players[i] == player_id:
            session_desc += f"(You)"


    session_desc += """
        Each player is identified by their unique name.
        Use these names when referring to players through available tools.

        The game map consists of the following regions:
    """

    for region, neighbours in zip(regions, neighbouring_regions):
        session_desc += f"- {region}: neighboring regions: {', '.join(neighbours)}\r\n"

    session_desc += f"""
        Each region has: a unique region name (used for its identification) and a list of neighboring regions.
        Use region names when referring to regions through available tools.

        The simulation proceeds in sequential turns.
        At the beginning of each turn, you receive an updated observation of the game state.
        You may then use available actions and tools to influence the game.

        The simulation automatically ends after turn {final_round}.
        Plan your strategy with the remaining number of turns in mind.
        </Session Details>
    """

    return f"{game_desc}\r\n{session_desc}"

def units_recruitment_prompt(supply_surplus, regions):
    recruitment_prompt = f"""
    <Recrutiment>
    Your country has a surplus of supplies. In addition to providing for your soldiers, these supplies can be used to recruit new units in your controlled regions.
    During an upkeep phase, you can choose which units to recruit and in which regions. The total cost of all recruited units must not exceed your available supply surplus of {supply_surplus}.

    You may recruit at most one unit in each region during this recruitment phase. Do not issue multiple recruitment orders for the same region.

    Controlled regions:
    """
    for region in regions:
        recruitment_prompt += f"- {region}\r\n"

    recruitment_prompt += """
    For information about available unit types, including their cost and strength, use the available rulebook tools.
    Review the available unit types and issue recruitment orders for the units you consider strategically appropriate.
    </Recrutiment>
    """

    return recruitment_prompt

def round_start_prompt(
        current_round, final_round, players, leaderboard_dict,
        controlled_units, controlled_regions, enemy_units_per_region,
        events):

    # Game State
    gamestate_desc = (f"Round {current_round}/{final_round}\r\n"
                     "Remaining players:\r\n")
    for i in range(len(players)):
        gamestate_desc += f"- {players[i]}\r\n"

    gamestate_desc += f"\r\nLeaderboard:\r\n"
    i = 1
    for player, score in leaderboard_dict.items():
        gamestate_desc += f"{i}. {player}: {score}\r\n"
        i += 1

    # Military Overview
    military_desc = "Controlled Units:\r\n"
    for unit in controlled_units:
        military_desc += f"- {unit}\r\n"

    military_desc += "\r\nControlled Regions:\r\n"
    for region, enemy_units in zip(controlled_regions, enemy_units_per_region):
        military_desc += f"- {region}, enemy units in the region: {enemy_units}\r\n"

    # Events
    events_desc = ""
    for event in events:
        events_desc += f"{event}\r\n"

    return f"{gamestate_desc}\r\n{military_desc}\r\n{events_desc}"