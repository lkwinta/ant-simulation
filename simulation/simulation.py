import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

from model import AntsScenario, AntsModel
from agents import FeromoneAntAgent, RandomAntAgent

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


def run(steps: int = 3000, heat_every: int = 10):
    scenario = AntsScenario(
        n=100,
        width=300,
        height=200,
        epsilon=0.5,
        A=0.5,
        sigma=0.1,
        evaporation_rate=0.001,
        diffusion_rate=0.1,
    )
    model = AntsModel(scenario=scenario, ant_class=FeromoneAntAgent)
    heat = np.zeros((scenario.width, scenario.height), dtype=np.int64)

    for t in tqdm(range(steps)):
        model.step()

        if (t % heat_every) == 0:
            for a in model.agents.select(lambda a: isinstance(a, FeromoneAntAgent)):
                x, y = a.pos
                heat[x, y] += 1

        if (t % 10000) == 0:
            save_heatmap(heat, path=f"heatmap_{t}.png", title=f"Ant position heatmap at step {t}")
            heat = np.zeros((scenario.width, scenario.height), dtype=np.int64)  # reset heatmap after saving

    df = model.datacollector.get_model_vars_dataframe()
    df.to_csv("model_data.csv", index=False)

    return model, heat


if __name__ == "__main__":
    model, heat = run(steps=100000, heat_every=10)
    save_heatmap(heat, path="heatmap.png", title="Ant position heatmap")
