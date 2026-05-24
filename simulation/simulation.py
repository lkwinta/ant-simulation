import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from tqdm import tqdm

from model import AntsScenario, AntsModel
from agents import FeromoneAntAgent

# from copy import deepcopy


def save_heatmap(heat, path="heatmap.png", title="Ant position heatmap", clip=None):
    plt.figure(figsize=(10, 6))
    # transpose + origin lower to match your earlier conventions
    if clip is not None:
        heat = np.clip(heat, 0, clip)
    else:
        heat = heat
    plt.imshow(heat.T, origin="lower")
    plt.colorbar(label="visits")
    plt.title(title)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()


def run(steps: int = 3000, heat_every: int = 10):
    # scenario = AntsScenario(
    #     n=100,
    #     width=300,
    #     height=200,
    #     epsilon=0.5,
    #     A=10.0,
    #     sigma=0.1,
    #     evaporation_rate=0.0001,
    #     diffusion_rate=0.1,
    #     max_feromone=100.0,
    #     r=1.7,
    # )
    scenario = AntsScenario(
        n=1000,
        width=300,
        height=200,
        epsilon=0.1,
        A=20.0,
        sigma=25.0,
        evaporation_rate=0.001,
        diffusion_rate=0.01,
        max_feromone=250.0,
        r=1.0,
    )
    model = AntsModel(scenario=scenario, ant_class=FeromoneAntAgent)
    # heat = np.zeros((scenario.width, scenario.height), dtype=np.int64)

    positions = []
    feromones = []

    for t in tqdm(range(steps)):
        model.step()

        if (t % heat_every) == 0:
            positions.append(
                [
                    a.cell
                    for a in model.agents.select(
                        lambda a: isinstance(a, FeromoneAntAgent)
                    )
                ]
            )
            feromones.append(model.feromone_layer.data.copy())
            # for a in model.agents.select(lambda a: isinstance(a, FeromoneAntAgent)):
            #     x, y = a.pos
            #     heat[x, y] += 1
        if (t % 10000) == 0:
            # save_heatmap(
            #     heat, path=f"heatmap_{t}.png", title=f"Ant position heatmap at step {t}"
            # )
            save_heatmap(
                model.grid._mesa_property_layers["feromone"].data,
                path=f"feromone_{t}.png",
                title=f"Feromone map at step {t}",
                clip=min(
                    scenario.max_feromone,
                    np.percentile(
                        model.grid._mesa_property_layers["feromone"].data, 95
                    ),
                ),
            )
            heat = np.zeros(
                (scenario.width, scenario.height), dtype=np.int64
            )  # reset heatmap after saving

        if (t % 10000) == 0 and t > 0:
            print(f"Step {t}: saving model data to CSV...")
            df = model.datacollector.get_model_vars_dataframe()
            df.to_csv(f"model_data_{t}.csv", index=False)

    df = model.datacollector.get_model_vars_dataframe()
    df.to_csv("model_data.csv", index=False)

    # animate positions
    fig, ax = plt.subplots(figsize=(10, 6))

    # map
    ax.imshow(1 - model.wall_layer.data.T, cmap="gray", origin="lower")

    artists = []

    for feromone, pos in zip(feromones, positions):
        x, y = zip(*[p.coordinate for p in pos])
        im = ax.imshow(feromone.T, cmap="viridis", alpha=0.5, origin="lower")
        sc = ax.scatter(x, y, color="red", s=10)
        artists.append([im, sc])

    ani = animation.ArtistAnimation(
        fig, artists, interval=200, blit=True, repeat_delay=1000
    )
    ani.save("ant_simulation.gif", writer="imagemagick")

    return model, heat


if __name__ == "__main__":
    model, heat = run(steps=20_000, heat_every=500)
    save_heatmap(heat, path="heatmap.png", title="Ant position heatmap")
