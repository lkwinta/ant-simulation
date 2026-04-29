from agents import AntAgent, FoodSourceAgent, NestAgent

import altair as alt

from model import (
    AntsScenario,
    AntsModel,
)
from logging import WARN
from mesa.mesa_logging import log_to_stderr
from mesa.visualization import (
    SolaraViz,
    SpaceRenderer,
    make_plot_component,
)
from mesa.visualization.components import AgentPortrayalStyle, PropertyLayerStyle

import os
import subprocess
import sys

alt.data_transformers.disable_max_rows()


log_to_stderr(WARN)


def agent_portrayal(agent):
    if isinstance(agent, AntAgent):
        tooltip = {
            "searching": agent.searching,
        }
        color = "red" if agent.searching else "orange"
    elif isinstance(agent, FoodSourceAgent):
        tooltip = {
            "food_amount": agent.food_amount,
        }
        color = "green"
    elif isinstance(agent, NestAgent):
        tooltip = {}
        color = "blue"
    else:
        tooltip = {}
        color = "gray"

    return AgentPortrayalStyle(
        color=color,
        size=5,
        tooltip=tooltip,
    )


def propertylayer_portrayal(layer):
    if layer.name == "wall":
        return PropertyLayerStyle(
            colormap="dark2",
            alpha=0.6,
            colorbar=False,
            vmin=0,
            vmax=10,
        )
    elif layer.name == "feromone":
        return PropertyLayerStyle(
            colormap="viridis",
            alpha=0.5,
            colorbar=True,
            vmin=-1,
            vmax=1,
        )


model_params = {
    "rng": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "n": {
        "type": "SliderInt",
        "value": 20,
        "label": "Number of agents:",
        "min": 10,
        "max": 100,
        "step": 1,
    },
    "width": 100,
    "height": 100,
    "A": {
        "type": "SliderFloat",
        "value": 0.5,
        "label": "Pheromone deposition strength (A):",
        "min": 0.1,
        "max": 1.0,
        "step": 0.1,
    },
    "sigma": {
        "type": "SliderFloat",
        "value": 0.1,
        "label": "Pheromone spread (sigma):",
        "min": 0.01,
        "max": 1.0,
        "step": 0.01,
    },
    "evaporation_rate": {
        "type": "SliderFloat",
        "value": 0.01,
        "label": "Pheromone evaporation rate:",
        "min": 0.0,
        "max": 0.1,
        "step": 0.01,
    },
    "diffusion_rate": {
        "type": "SliderFloat",
        "value": 0.1,
        "label": "Pheromone diffusion rate:",
        "min": 0.0,
        "max": 0.5,
        "step": 0.01,
    },
}

model = AntsModel(
    scenario=AntsScenario(
        n=20,
        width=100,
        height=100,
        A=0.5,
        sigma=0.1,
        evaporation_rate=0.01,
        diffusion_rate=0.05,
    )
)

renderer = (
    SpaceRenderer(model, backend="altair")
    .setup_structure(grid_opacity=0.0)
    .setup_agents(agent_portrayal, cmap="viridis", vmin=0, vmax=10)
    .setup_propertylayer(propertylayer_portrayal)
)
renderer.render()

Feromone_plot = make_plot_component("Feromone Sum")
ant_count_plot = make_plot_component(
    [
        "Ants Count 1 Short",
        "Ants Count 2 Short",
        "Ants Count 1 Long",
        "Ants Count 2 Long",
    ]
)

page = SolaraViz(
    model,
    renderer,
    components=[Feromone_plot, ant_count_plot],
    model_params=model_params,
    name="Random Ants Model",
)
page  # noqa


if __name__ == "__main__" and os.environ.get("SOLARA_APP") != os.path.abspath(__file__):
    try:
        raise SystemExit(
            subprocess.call(
                [sys.executable, "-m", "solara", "run", os.path.abspath(__file__)]
            )
        )
    except KeyboardInterrupt:
        raise SystemExit(130)
