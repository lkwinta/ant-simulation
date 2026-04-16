from mesa.discrete_space import CellAgent

class RandomAntAgent(CellAgent):
    def __init__(self, model, cell):
        super().__init__(model)
        self.cell = cell

    def step(self):
        possible_moves = self.cell.neighborhood.cells
        self.cell = self.random.choice(possible_moves)
