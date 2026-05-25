import os

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from tqdm import tqdm

from model import AntsScenario, AntsModel
from agents import FeromoneAntAgent

from itertools import product
import multiprocessing as mp
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


def run(scenario: AntsScenario, steps: int = 3000, heat_every: int = 10):
    model = AntsModel(scenario=scenario, ant_class=FeromoneAntAgent)

    positions = []
    states = []
    feromones = []

    for t in range(steps):
        model.step()

        if (t % heat_every) == 0:
            current_positions = []
            current_states = []
            for a in model.agents.select(lambda a: isinstance(a, FeromoneAntAgent)):
                current_positions.append(a.cell.position)
                current_states.append(a.searching)

            positions.append(current_positions)
            states.append(current_states)
            feromones.append(model.feromone_layer.data.copy())

        # if (t % 10000) == 0 and t > 0:
        #     print(f"Step {t}: saving model data to CSV...")
        #     df = model.datacollector.get_model_vars_dataframe()
        #     df.to_csv(f"model_data_{t}.csv", index=False)

    # df = model.datacollector.get_model_vars_dataframe()
    # df.to_csv("model_data.csv", index=False)

    return model.wall_layer.data.copy().T, feromones, positions, states
    # return model, heat


def draw_simulation(walls, feromones, positions, states, sim_name="ant_simulation"):
    # animate positions
    fig, ax = plt.subplots(figsize=(10, 6))

    # map
    ax.imshow(1 - walls, cmap="gray", origin="lower")

    artists = []

    for feromone, pos, state in zip(feromones, positions, states):
        x, y = zip(*pos)

        # ant color by searching or not
        colors = ["red" if s else "blue" for s in state]

        im = ax.imshow(
            np.clip(feromone.T, 0, 100), cmap="viridis", alpha=0.5, origin="lower"
        )
        sc = ax.scatter(x, y, color=colors, s=10)
        artists.append([im, sc])

    ani = animation.ArtistAnimation(
        fig, artists, interval=100, blit=True, repeat_delay=1000
    )
    ani.save(f"{sim_name}.gif", writer="imagemagick")


def run_wrap(params):
    A, sigma, diffusion_rate = params
    scenario = AntsScenario(
        n=500,
        width=300,
        height=200,
        epsilon=0.1,
        A=A,
        sigma=sigma,
        evaporation_rate=0.02,
        diffusion_rate=diffusion_rate,
        max_feromone=float("inf"),
        r=1.0,
    )
    return run(scenario=scenario, steps=25_000, heat_every=100), params


if __name__ == "__main__":
    A = [7, 7.5, 8]
    sigma = [50, 52, 55]
    diffusion_rate = [0.04, 0.042, 0.045]

    params = list(product(A, sigma, diffusion_rate))

    os.makedirs("simulations", exist_ok=True)

    with mp.Pool(processes=mp.cpu_count()) as pool:
        for (walls, feromones, positions, states), param in tqdm(
            pool.imap_unordered(
                run_wrap,
                params,
            )
        ):
            sim_name = f"simulations/sim_A{param[0]}_sigma{param[1]}_diff{param[2]}"
            draw_simulation(walls, feromones, positions, states, sim_name=sim_name)

    # model = run(scenario=scenario, steps=25_000, heat_every=100)
    # save_heatmap(heat, path="heatmap.png", title="Ant position heatmap")
