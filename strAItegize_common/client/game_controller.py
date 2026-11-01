from strAItegize_common.client.multiagent_system import MultiAgentSystem
from strAItegize_common.client.communication.communication_context import CommunicationContext

class GameController:
    def __init__(self, simulation_port, multiagent_system: MultiAgentSystem, human_mode=False, **kwargs):
        self.communication = CommunicationContext()
        self.communication.start_connection(simulation_port=int(simulation_port))
        self.is_next_round_upkeep = False

        # Graph
        self.multiagent_system = multiagent_system(
            communication=self.communication,
            human_mode=human_mode,
            **kwargs
        )

    def initialize_simulation(self):
        # Waiting for the simulation to start 
        session_data = self.communication.start_simulation()

        # Generating simulation start prompt message
        self.your_id = session_data["your_id"]

        # Checking if next round is an upkeep one
        self.is_next_round_upkeep = session_data["is_start_upkeep"]

        self.multiagent_system.initialize_graph(
            player_id=session_data["your_id"],
            players=session_data["players"],
            regions=session_data["regions"],
            neighbouring_regions=session_data["neighbouring_regions"],
            final_round=session_data["final_round"]
        )

    def start_simulation(self):
        while True:
            # Perform upkeep phase if needed
            if self.is_next_round_upkeep:
                upkeep_data = self.communication.await_upkeep()

                recruitment_to_send = self.multiagent_system.invoke_upkeep(
                    supply_surplus=upkeep_data["supply_surplus"],
                    regions=upkeep_data["regions"]
                )
                self.communication.submit_recruitment(recruitment=recruitment_to_send)

            # Await for the new round
            round_data = self.communication.await_round_start()

            orders_to_send = self.multiagent_system.invoke_orders(
                current_round=round_data["current_round"],
                final_round=round_data["final_round"],
                players=round_data["players"],
                leaderboard=round_data["leaderboard"],
                units=round_data["units"],
                regions=round_data["regions"],
                tresspasers=round_data["tresspasers"],
                events=round_data["events"]
            )

            # Sending the orders to the simulation
            self.communication.submit_orders(orders=orders_to_send)

            # Awaiting next round
            self.is_next_round_upkeep = self.communication.end_round()

            # Checking if the server signalled the simulation end
            if self.is_next_round_upkeep is None:
                break