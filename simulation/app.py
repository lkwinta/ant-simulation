import altair as alt
# alt.data_transformers.enable("vegafusion") 

import os
import subprocess
import sys

from model import (
    AntsScenario,
    RandomAntsModel,
)
from mesa.mesa_logging import INFO, log_to_stderr
from mesa.visualization import (
    SolaraViz,
    SpaceRenderer,
    make_plot_component,
)
from mesa.visualization.components import AgentPortrayalStyle, PropertyLayerStyle

log_to_stderr(INFO)


def agent_portrayal(agent):
    return AgentPortrayalStyle(
        color="red",
        tooltip={"Agent ID": agent.unique_id},
    )  # we are using a colormap to translate wealth to color

def propertylayer_portrayal(layer):
    if layer.name == "walls":
        return PropertyLayerStyle(
            colormap="greys",
            # alpha=0.9,
            # colorbar=False,
            # vmin=0,
            # vmax=1,
        )
    return None

model_params = {
    "rng": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "n": {
        "type": "SliderInt",
        "value": 50,
        "label": "Number of agents:",
        "min": 10,
        "max": 100,
        "step": 1,
    },
    "width": 100,
    "height": 100,
}

model = RandomAntsModel(
    scenario=AntsScenario(
        n=200,
        width=100,
        height=100,
    )
)

renderer = (
    SpaceRenderer(model, backend="altair")
    .setup_structure(  # To customize the grid appearance.
        grid_color="black", grid_dash=[6, 2], grid_opacity=0.3
    )
    # .setup_propertylayer(propertylayer_portrayal)
    .setup_agents(agent_portrayal, cmap="viridis", vmin=0, vmax=10)
)
renderer.render()

page = SolaraViz(
    model,
    renderer,
    components=[],
    model_params=model_params,
    name="Random Ants Model",
)
page  # noqa


if __name__ == "__main__" and os.environ.get("SOLARA_APP") != os.path.abspath(__file__):
    # Running through Solara starts the web server instead of exiting silently.
    try:
        raise SystemExit(
            subprocess.call(
                [sys.executable, "-m", "solara", "run", os.path.abspath(__file__)]
            )
        )
    except KeyboardInterrupt:
        raise SystemExit(130)
