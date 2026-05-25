import numpy as np
from collections import deque

from mesa.discrete_space import Cell, CellAgent


class FoodSourceAgent(CellAgent):
    def __init__(self, model, cell: Cell, food_amount: int):
        super().__init__(model)
        self.cell = cell
        self.pos = cell.coordinate
        self.food_amount = food_amount


class NestAgent(CellAgent):
    def __init__(self, model, cell: Cell):
        super().__init__(model)
        self.cell = cell
        self.pos = cell.coordinate


class AntAgent(CellAgent):
    def __init__(self, model, cell: Cell, nest: NestAgent):
        super().__init__(model)
        self.cell = cell
        self.pos = cell.coordinate
        self.nest = nest

    def step(self):
        pass

    def deposit_feromone(self):
        pass

    def _filter_neighbors(self, neighbors):
        return [
            neighbor
            for neighbor in neighbors
            if self.model.is_passable_move(self.cell.coordinate, neighbor.coordinate)
        ]


class RandomAntAgent(AntAgent):
    def __init__(self, model, cell: Cell, nest: NestAgent):
        super().__init__(model, cell, nest)
        self.feromone = self.model.feromone_layer.data
        self.prev_cell = cell

    def step(self):
        possible_moves = self._filter_neighbors(self.cell.neighborhood.cells)
        self.cell = self.random.choice(possible_moves)
        self.pos = self.cell.coordinate

    def deposit_feromone(self):
        pass


class FeromoneAntAgent(AntAgent):
    def __init__(self, model, cell: Cell, nest: NestAgent):
        super().__init__(model, cell, nest)
        self.feromone = self.model.feromone_layer.data
        self.epsilon = self.model.epsilon
        self.searching = True
        self.food_position = None
        self.recent_positions = deque(maxlen=10)

    def step(self):
        possible_moves = self._filter_neighbors(self.cell.neighborhood.cells)

        if self.searching:
            curr_f = np.log1p(
                self.feromone[self.cell.coordinate[0], self.cell.coordinate[1]]
            )

            gradients = [
                np.log1p(self.feromone[n.coordinate[0], n.coordinate[1]]) - curr_f
                for n in possible_moves
            ]
            weights = [self._move_weight(g) for g in gradients]

            for i, move in enumerate(possible_moves):
                if move in self.recent_positions:
                    weights[i] *= 0.01

            if sum(weights) == 0:
                weights = [1] * len(possible_moves)

            self.prev_cell = self.cell
            self.cell = self.random.choices(possible_moves, weights=weights, k=1)[0]
            self.pos = self.cell.coordinate
            self.recent_positions.append(self.cell)

            if any(isinstance(a, FoodSourceAgent) for a in self.cell.agents):
                self.searching = False
                self.food_position = self.cell.coordinate
        else:
            self.prev_cell = self.cell
            self.cell = self._return_move(possible_moves)
            self.pos = self.cell.coordinate

            if any(isinstance(a, NestAgent) for a in self.cell.agents):
                self.searching = True
                self.recent_positions.clear()

    def deposit_feromone(self):
        if not self.searching:
            food_dist = np.linalg.norm(
                np.array(self.food_position) - np.array(self.cell.coordinate)
            )
            x, y = self.cell.coordinate
            self.feromone[x, y] += self.model.A * np.exp(
                -np.pow(food_dist, 1) / np.pow(self.model.sigma, 1)
            )
            self.feromone[x, y] = min(self.feromone[x, y], self.model.max_feromone)

    def _move_weight(self, gradient):
        if gradient > 0:
            return 1 + gradient  # Prefer moves with higher pheromone
        elif gradient < 0:
            return self.epsilon
        else:
            return 1  # Neutral move if no gradient

    def _return_move(self, possible_moves):
        curr_dist = self.model.nest_distance[self.cell.coordinate]

        scored = []
        for n in possible_moves:
            if self.prev_cell is not None and n == self.prev_cell:
                continue
            d = self.model.nest_distance[n.coordinate]
            if not np.isfinite(d):
                continue

            if not np.isfinite(curr_dist) or d < curr_dist:
                scored.append((n, d))

        if not scored:
            scored = [
                (n, self.model.nest_distance[n.coordinate])
                for n in possible_moves
                if self.prev_cell is None or n != self.prev_cell
                if np.isfinite(self.model.nest_distance[n.coordinate])
            ]
            if not scored:
                scored = [
                    (n, self.model.nest_distance[n.coordinate])
                    for n in possible_moves
                    if np.isfinite(self.model.nest_distance[n.coordinate])
                ]

        if not scored:
            return self.prev_cell if self.prev_cell is not None else self.cell

        scored.sort(key=lambda x: x[1])
        best = scored[: min(3, len(scored))]

        moves, dists = zip(*best)
        weights = [1.0 / (d + self.epsilon) for d in dists]
        return self.random.choices(list(moves), weights=weights, k=1)[0]
