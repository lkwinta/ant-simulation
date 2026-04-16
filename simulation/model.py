import numpy as np

from mesa import Model
from mesa.datacollection import DataCollector
from mesa.discrete_space import OrthogonalMooreGrid, PropertyLayer
from mesa.experimental.data_collection import DataRecorder, DatasetConfig
from mesa.experimental.scenarios import Scenario

from random_agent import RandomAntAgent
from diamond import get_diamond_mask


class AntsScenario(Scenario):
    n: int = 100
    width: int = 100
    height: int = 100


class RandomAntsModel(Model):
    def __init__(self, scenario: AntsScenario =None):

        if scenario is None:
            scenario = AntsScenario()

        super().__init__(scenario=scenario)

        walls_layer = PropertyLayer(
            "walls", (scenario.width, scenario.height), default_value=0, dtype=np.uint8
        )
        wall_mask = get_diamond_mask(scenario.width, scenario.height)
        walls_layer.data = wall_mask.astype(np.uint8)

        self.num_agents = scenario.n
        self.grid = OrthogonalMooreGrid(
            (scenario.width, scenario.height), random=self.random
        )

        self.grid.add_property_layer(walls_layer)

        self.recorder = DataRecorder(self)
        # TODO: Add metrics to the recorder

        # Set up data collection
        self.datacollector = DataCollector(
            # TODO: Add model-level and agent-level data collection functions
        )
        RandomAntAgent.create_agents(
            self,
            self.num_agents,
            self.random.choices(self.grid.all_cells.cells, k=self.num_agents),
        )

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        self.agents.shuffle_do("step")  # Activate all agents in random order
        self.datacollector.collect(self)  # Collect data
        