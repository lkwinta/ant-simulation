import numpy as np

from mesa import Model
from mesa.datacollection import DataCollector
from mesa.discrete_space import OrthogonalMooreGrid, PropertyLayer
from mesa.experimental.data_collection import DataRecorder, DatasetConfig
from mesa.experimental.scenarios import Scenario

from agents import FeromoneAntAgent, RandomAntAgent, FoodSourceAgent, NestAgent
from diamond import get_diamond_mask


class AntsScenario(Scenario):
    n: int = 100
    width: int = 100
    height: int = 100


class AntsModel(Model):
    def __init__(self, scenario: AntsScenario =None, ant_class=FeromoneAntAgent):

        if scenario is None:
            scenario = AntsScenario()

        super().__init__(scenario=scenario)
  
        self.num_agents = scenario.n
        self.ant_class = ant_class

        self.grid = OrthogonalMooreGrid(
            (scenario.width, scenario.height), random=self.random
        )

        self.wall_layer = PropertyLayer("wall", (scenario.width, scenario.height), default_value=False)
        mask = get_diamond_mask(scenario.width, scenario.height)
        self.wall_layer.data = mask["wall_mask"].astype(bool)

        self.feromone_layer = PropertyLayer("feromone", (scenario.width, scenario.height), default_value=0.0)
        
        self.grid.add_property_layer(self.wall_layer)
        self.grid.add_property_layer(self.feromone_layer)

        left_room_center = ((mask["params"]["left_room"][0] + mask["params"]["left_room"][2]) // 2,
                            (mask["params"]["left_room"][1] + mask["params"]["left_room"][3]) // 2)
        right_room_center = ((mask["params"]["right_room"][0] + mask["params"]["right_room"][2]) // 2,
                             (mask["params"]["right_room"][1] + mask["params"]["right_room"][3]) // 2)

        FoodSourceAgent(self, self.grid[right_room_center[0], right_room_center[1]], food_amount=1000)
        NestAgent(self, self.grid[left_room_center[0], left_room_center[1]])

        # TODO: place on grid

        self.recorder = DataRecorder(self)
        # TODO: Add metrics to the recorder

        # Set up data collection
        self.datacollector = DataCollector(
            # TODO: Add model-level and agent-level data collection functions
        )

        max_spawn_radius = left_room_center[0] - mask["params"]["left_room"][0]

        for _ in range(self.num_agents):
            x = int(self.random.normalvariate(left_room_center[0], max_spawn_radius / 3))
            y = int(self.random.normalvariate(left_room_center[1], max_spawn_radius / 3))
            ant = self.ant_class(self, self.grid[x, y])
            self.grid.agents.add(ant)

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        ants = self.agents.select(lambda a: isinstance(a, self.ant_class))

        ants.shuffle_do("step")  # Activate all agents in random order
        ants.shuffle_do("deposit_feromone")  # Activate all agents in random order
        
        # todo: add pheromone diffusion and evaporation steps here

        self.datacollector.collect(self)  # Collect data

        