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

class RandomAntAgent(AntAgent):
    def __init__(self, model, cell: Cell, nest: NestAgent):
        super().__init__(model, cell, nest)
        self.walls = self.model.wall_layer.data
        self.feromone = self.model.feromone_layer.data
        self.prev_cell = cell

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


class FeromoneAntAgent(AntAgent):
    def __init__(self, model, cell: Cell, nest: NestAgent):
        super().__init__(model, cell, nest)
        self.walls = self.model.wall_layer.data
        self.feromone = self.model.feromone_layer.data
        self.epsilon = self.model.epsilon
        self.searching = True
        self.food_position = None

    def step(self):
        possible_moves = self._filter_neighbors(self.cell.neighborhood.cells)

        if self.searching:
            curr_feromone = self.feromone[self.cell.coordinate[0], self.cell.coordinate[1]]
            gradients = [self.feromone[n.coordinate[0], n.coordinate[1]] - curr_feromone for n in possible_moves]
            weights = [self._move_weight(g) for g in gradients]

            if sum(weights) == 0:
                weights = [1] * len(possible_moves)

            self.prev_cell = self.cell
            self.cell = self.random.choices(possible_moves, weights=weights, k=1)[0]
            self.pos = self.cell.coordinate

            if any(isinstance(a, FoodSourceAgent) for a in self.cell.agents):
                self.searching = False
                self.food_position = self.cell.coordinate
        else:
            self.prev_cell = self.cell
            self.cell = self._return_move(possible_moves, self.nest.pos)
            self.pos = self.cell.coordinate
        
            if any(isinstance(a, NestAgent) for a in self.cell.agents):
                self.searching = True

    def deposit_feromone(self):
        if not self.searching:
            food_dist = np.linalg.norm(np.array(self.food_position) - np.array(self.cell.coordinate))
            self.feromone[self.cell.coordinate[0], self.cell.coordinate[1]] += self.model.A * np.exp(-np.pow(food_dist, 2)/self.model.sigma)

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
    
    def _return_move(self, possible_moves, nest_pos):
        nest = np.array(nest_pos, dtype=float)
        curr = np.array(self.cell.coordinate, dtype=float)
        curr_dist = np.linalg.norm(curr - nest)

        scored = []
        for n in possible_moves:
            if self.prev_cell is not None and n == self.prev_cell:
                continue
            d = np.linalg.norm(np.array(n.coordinate, dtype=float) - nest)

            # preferuj ruchy nieoddalające
            if d <= curr_dist + 1e-9:
                scored.append((n, d))

        # fallback: jeśli nie ma żadnego kroku "w dobrą stronę", pozwól na wszystkie
        if not scored:
            scored = [(n, np.linalg.norm(np.array(n.coordinate, dtype=float) - nest)) for n in possible_moves
                    if self.prev_cell is None or n != self.prev_cell]
            if not scored:
                scored = [(n, np.linalg.norm(np.array(n.coordinate, dtype=float) - nest)) for n in possible_moves]

        scored.sort(key=lambda x: x[1])
        best = scored[: min(3, len(scored))]

        moves, dists = zip(*best)
        weights = [1.0 / (d + self.epsilon) for d in dists]
        return self.random.choices(list(moves), weights=weights, k=1)[0]
