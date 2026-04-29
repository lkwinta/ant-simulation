import numpy as np

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

class RandomAntAgent(CellAgent):
    def __init__(self, model, cell: Cell):
        super().__init__(model)
        self.cell = cell
        self.pos = cell.coordinate
        self.walls = self.model.wall_layer.data
        self.feromone = self.model.feromone_layer.data

    def step(self):
        possible_moves = self._filter_neighbors(self.cell.neighborhood.cells)
        self.cell = self.random.choice(possible_moves)
        self.pos = self.cell.coordinate

    def deposit_feromone(self):
        pass

    def _filter_neighbors(self, neighbors):
        # Filter out neighbors that are walls (if needed)
        return [n for n in neighbors if not self._is_wall(n)]
    
    def _is_wall(self, cell: Cell):
        return self.walls[cell.coordinate[0], cell.coordinate[1]]


class FeromoneAntAgent(CellAgent):
    def __init__(self, model, cell: Cell):
        super().__init__(model)
        self.cell = cell
        self.pos = cell.coordinate
        self.walls = self.model.wall_layer.data
        self.feromone = self.model.feromone_layer.data
        self.epsilon = 0.01
        self.searching = True
        self.food_distance = 0.0

    def step(self):
        possible_moves = self._filter_neighbors(self.cell.neighborhood.cells)

        curr_feromone = self.feromone[self.cell.coordinate[0], self.cell.coordinate[1]]
        gradients = [self.feromone[n.coordinate[0], n.coordinate[1]] - curr_feromone for n in possible_moves]
        weights = [self._move_weight(g) for g in gradients]

        self.cell = self.random.choices(possible_moves, weights=weights, k=1)[0]
        self.pos = self.cell.coordinate

    def deposit_feromone(self):
        if not self.searching:
            self.feromone[self.cell.coordinate[0], self.cell.coordinate[1]] += self.model.A * np.exp(np.pow(self.food_distance, 2)/self.model.sigma)

    def _move_weight(self, gradient):
        if gradient > 0:
            return 1 + gradient  # Prefer moves with higher pheromone
        elif gradient < 0:
            return self.epsilon
        else:
            return 1  # Neutral move if no gradient

    def _filter_neighbors(self, neighbors):
        # Filter out neighbors that are walls (if needed)
        return [n for n in neighbors if not self._is_wall(n)]
    
    def _is_wall(self, cell: Cell):
        return self.walls[cell.coordinate[0], cell.coordinate[1]]
    
