import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

from model import AntsScenario, AntsModel
from agents import FeromoneAntAgent, RandomAntAgent

def run(steps: int = 2000, heat_every: int = 10):
    scenario = AntsScenario(
        n=100,
        width=300,
        height=200,
    )
    model = AntsModel(scenario=scenario, ant_class=FeromoneAntAgent)
    heat = np.zeros((scenario.width, scenario.height), dtype=np.int64)

    for t in tqdm(range(steps)):
        model.step()

        if (t % heat_every) == 0:
            for a in model.agents.select(lambda a: isinstance(a, FeromoneAntAgent)):
                x, y = a.pos
                heat[x, y] += 1

    return model, heat


def save_heatmap(heat, path="heatmap.png", title="Ant position heatmap"):
    plt.figure(figsize=(10, 6))
    # transpose + origin lower to match your earlier conventions
    plt.imshow(heat.T, origin="lower")
    plt.colorbar(label="visits")
    plt.title(title)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()

if __name__ == "__main__":
    model, heat = run(steps=3000, heat_every=10)
    save_heatmap(heat, path="heatmap.png", title="Ant position heatmap")
