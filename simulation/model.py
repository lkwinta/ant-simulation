from collections import deque

import numpy as np

from mesa import Model
from mesa.datacollection import DataCollector
from mesa.discrete_space import OrthogonalMooreGrid, PropertyLayer
from mesa.experimental.data_collection import DataRecorder, DatasetConfig
from mesa.experimental.scenarios import Scenario

from agents import (
    FeromoneAntAgent,
    FoodSourceAgent,
    NestAgent,
    AntAgent,
)
from double_diamond import build_double_diamond_mask


class AntsScenario(Scenario):
    n: int = 100
    width: int = 100
    height: int = 100
    A: float = 1.0
    sigma: float = 0.5
    epsilon: float = 0.01
    evaporation_rate: float = 0.01
    diffusion_rate: float = 0.1
    max_feromone: float = 1000.0
    r = 1.4


class AntsModel(Model):
    def __init__(
        self,
        scenario: AntsScenario = None,
        ant_class: type[AntAgent] = FeromoneAntAgent,
    ):
        if scenario is None:
            scenario = AntsScenario()

        super().__init__(scenario=scenario)

        self.A = scenario.A
        self.sigma = scenario.sigma
        self.evaporation_rate = scenario.evaporation_rate
        self.diffusion_rate = scenario.diffusion_rate
        self.epsilon = scenario.epsilon
        self.max_feromone = scenario.max_feromone

        self.num_agents = scenario.n
        self.ant_class = ant_class

        self.grid = OrthogonalMooreGrid(
            (scenario.width, scenario.height), random=self.random
        )

        self.wall_layer = PropertyLayer(
            "wall", (scenario.width, scenario.height), default_value=False
        )
        mask = build_double_diamond_mask(scenario.width, scenario.height, r=scenario.r)
        self.wall_layer.data = mask["wall_mask"].astype(bool)
        self.detector_1_short = mask["params"]["shortest_branch_mid_1"]
        self.detector_2_short = mask["params"]["shortest_branch_mid_2"]
        self.detector_1_long = mask["params"]["longest_branch_mid_1"]
        self.detector_2_long = mask["params"]["longest_branch_mid_2"]

        self.feromone_layer = PropertyLayer(
            "feromone", (scenario.width, scenario.height), default_value=0.0
        )

        self.grid.add_property_layer(self.wall_layer)
        self.grid.add_property_layer(self.feromone_layer)

        left_room_center = (
            (mask["params"]["left_room"][0] + mask["params"]["left_room"][2]) // 2,
            (mask["params"]["left_room"][1] + mask["params"]["left_room"][3]) // 2,
        )
        right_room_center = (
            (mask["params"]["right_room"][0] + mask["params"]["right_room"][2]) // 2,
            (mask["params"]["right_room"][1] + mask["params"]["right_room"][3]) // 2,
        )

        # spawn several food sources in one spot to make it more likely for ants to find them
        self.food_source = FoodSourceAgent(
            self,
            self.grid[right_room_center[0], right_room_center[1]],
            food_amount=1000,
        )

        for cell in self.food_source.cell.neighborhood.cells:
            pos = cell.position
            FoodSourceAgent(self, self.grid[pos[0], pos[1]], food_amount=1000)

        self.nest = NestAgent(self, self.grid[left_room_center[0], left_room_center[1]])
        self.nest_distance = self._build_distance_field(self.nest.pos)

        # TODO: place on grid

        self.recorder = DataRecorder(self)
        # TODO: Add metrics to the recorder

        (
            self.data_registry.track_model(self, "model_data", "feromone_sum").record(
                self.recorder, configuration=DatasetConfig(start_time=4, interval=2)
            )
        )
        (
            self.data_registry.track_model(
                self,
                "model_data",
                [
                    "count_ants_1_short",
                    "count_ants_2_short",
                    "count_ants_1_long",
                    "count_ants_2_long",
                ],
            ).record(
                self.recorder, configuration=DatasetConfig(start_time=4, interval=2)
            )
        )

        # Set up data collection
        self.datacollector = DataCollector(
            # TODO: Add model-level and agent-level data collection functions
            model_reporters={
                "Feromone Sum": "feromone_sum",
                "Ants Count 1 Short": "count_ants_1_short",
                "Ants Count 2 Short": "count_ants_2_short",
                "Ants Count 1 Long": "count_ants_1_long",
                "Ants Count 2 Long": "count_ants_2_long",
            },
        )

        max_spawn_radius = left_room_center[0] - mask["params"]["left_room"][0]

        for _ in range(self.num_agents):
            x = int(
                self.random.normalvariate(left_room_center[0], max_spawn_radius / 3)
            )
            y = int(
                self.random.normalvariate(left_room_center[1], max_spawn_radius / 3)
            )

            x = np.clip(
                x, mask["params"]["left_room"][0], mask["params"]["left_room"][2] - 1
            )
            y = np.clip(
                y, mask["params"]["left_room"][1], mask["params"]["left_room"][3] - 1
            )

            ant = self.ant_class(self, self.grid[x, y], self.nest)
            self.grid.agents.add(ant)

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        ants = self.agents.select(lambda a: isinstance(a, self.ant_class))

        ants.shuffle_do("step")  # Activate all agents in random order
        ants.shuffle_do("deposit_feromone")  # Activate all agents in random order

        # todo: add pheromone diffusion and evaporation steps here
        self.feromone_layer.data *= 1 - self.evaporation_rate
        self.feromone_layer.data = AntsModel._diffusion(
            self.feromone_layer.data,
            self.diffusion_rate,
            self.wall_layer.data.astype(bool),
        )
        np.clip(
            self.feromone_layer.data,
            0.0,
            self.max_feromone,
            out=self.feromone_layer.data,
        )

        self.datacollector.collect(self)  # Collect data

    @property
    def feromone_sum(self):
        return np.sum(self.feromone_layer.data)

    @property
    def count_ants_1_short(self):
        filt = lambda a: isinstance(a, self.ant_class)
        return self.count_agents_in_area(self.detector_1_short, 5, 25, filt)

    @property
    def count_ants_2_short(self):
        filt = lambda a: isinstance(a, self.ant_class)
        return self.count_agents_in_area(self.detector_2_short, 5, 25, filt)

    @property
    def count_ants_1_long(self):
        filt = lambda a: isinstance(a, self.ant_class)
        return self.count_agents_in_area(self.detector_1_long, 5, 25, filt)

    @property
    def count_ants_2_long(self):
        filt = lambda a: isinstance(a, self.ant_class)
        return self.count_agents_in_area(self.detector_2_long, 5, 25, filt)

    def count_agents_in_area(self, center, radius_x, radius_y, agent_filter=None):
        cx, cy = center
        x0 = max(0, cx - radius_x)
        x1 = min(self.grid.width - 1, cx + radius_x)
        y0 = max(0, cy - radius_y)
        y1 = min(self.grid.height - 1, cy + radius_y)

        cnt = 0
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                cell = self.grid[(x, y)]
                for a in cell.agents:
                    if agent_filter is None or agent_filter(a):
                        cnt += 1
        return cnt

    def is_passable_move(self, start, end):
        sx, sy = start
        ex, ey = end

        if not (0 <= ex < self.grid.width and 0 <= ey < self.grid.height):
            return False
        if self.wall_layer.data[sx, sy] or self.wall_layer.data[ex, ey]:
            return False

        dx = ex - sx
        dy = ey - sy
        if abs(dx) > 1 or abs(dy) > 1 or (dx == 0 and dy == 0):
            return False

        # Block diagonal corner-cutting through walls.
        if abs(dx) == 1 and abs(dy) == 1:
            if self.wall_layer.data[sx + dx, sy] or self.wall_layer.data[sx, sy + dy]:
                return False

        return True

    def _build_distance_field(self, start):
        distances = np.full(self.wall_layer.data.shape, np.inf, dtype=float)
        if self.wall_layer.data[start]:
            raise ValueError("Nest cannot be placed inside a wall.")

        queue = deque([start])
        distances[start] = 0.0

        while queue:
            x, y = queue.popleft()
            base_distance = distances[x, y]

            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue

                    nx = x + dx
                    ny = y + dy
                    neighbor = (nx, ny)

                    if not self.is_passable_move((x, y), neighbor):
                        continue
                    if np.isfinite(distances[neighbor]):
                        continue

                    distances[neighbor] = base_distance + 1.0
                    queue.append(neighbor)

        return distances

    @staticmethod
    def _diffusion(F, lam, wall_mask):
        W, H = F.shape

        F0 = F.copy()
        F0[wall_mask] = 0.0

        nbr_sum = np.zeros_like(F0, dtype=float)

        shifts = [
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1),
            (1, 1),
            (1, -1),
            (-1, 1),
            (-1, -1),
        ]
        for dx, dy in shifts:
            src_x0 = max(0, -dx)
            src_x1 = min(W, W - dx)
            src_y0 = max(0, -dy)
            src_y1 = min(H, H - dy)
            dst_x0 = max(0, dx)
            dst_x1 = min(W, W + dx)
            dst_y0 = max(0, dy)
            dst_y1 = min(H, H + dy)

            src = (slice(src_x0, src_x1), slice(src_y0, src_y1))
            dst = (slice(dst_x0, dst_x1), slice(dst_y0, dst_y1))

            nbr_sum[dst] += F0[src]

        F_new = (1.0 - lam) * F0 + (lam / len(shifts)) * nbr_sum
        F_new[wall_mask] = 0.0
        F_new[F_new < 0] = 0.0
        return F_new
