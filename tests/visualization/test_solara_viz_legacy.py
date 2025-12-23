"""Test Solara visualizations - Legacy/Backwards Compatibility.

This file tests deprecated dict-based portrayals and legacy component APIs.
These tests ensure backwards compatibility is maintained until deprecated
features are removed.

For modern API tests using AgentPortrayalStyle, PropertyLayerStyle, and
SpaceRenderer, see test_solara_viz.py.

NOTE: This file will be removed when legacy support is dropped.
"""

import random

import solara

import mesa
import mesa.visualization.components.altair_components
import mesa.visualization.components.matplotlib_components
from mesa.space import MultiGrid, PropertyLayer
from mesa.visualization.components.altair_components import make_altair_space
from mesa.visualization.components.matplotlib_components import make_mpl_space_component
from mesa.visualization.solara_viz import SolaraViz


class MockAgent(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)


class MockModel(mesa.Model):
    def __init__(self, seed=None):
        super().__init__(seed=seed)
        layer1 = PropertyLayer(
            name="sugar", width=10, height=10, default_value=10.0, dtype=float
        )
        self.grid = MultiGrid(
            width=10, height=10, torus=True, property_layers=layer1
        )
        a = MockAgent(self)
        self.grid.place_agent(a, (5, 5))


def test_legacy_dict_portrayal_matplotlib(mocker):
    mock_space_matplotlib = mocker.spy(
        mesa.visualization.components.matplotlib_components, "SpaceMatplotlib"
    )

    model = MockModel()

    def agent_portrayal(agent):
        return {"marker": "o", "color": "gray"}

    propertylayer_portrayal = None

    solara.render(
        SolaraViz(
            model,
            components=[make_mpl_space_component(agent_portrayal)],
        )
    )

    mock_space_matplotlib.assert_called_with(
        model, agent_portrayal, propertylayer_portrayal, post_process=None
    )


def test_legacy_dict_portrayal_altair(mocker):
    mock_space_altair = mocker.spy(
        mesa.visualization.components.altair_components, "SpaceAltair"
    )

    model = MockModel()

    def agent_portrayal(agent):
        return {"marker": "o", "color": "gray"}

    solara.render(SolaraViz(model, components="default"))

    assert mock_space_altair.call_count == 1


def test_legacy_altair_with_propertylayer_dict(mocker):
    mock_space_altair = mocker.spy(
        mesa.visualization.components.altair_components, "SpaceAltair"
    )
    mock_chart_property_layer = mocker.spy(
        mesa.visualization.components.altair_components, "chart_property_layers"
    )

    model = MockModel()

    def agent_portrayal(agent):
        return {"marker": "o", "color": "gray"}

    propertylayer_portrayal = {
        "sugar": {
            "colormap": "pastel1",
            "alpha": 0.75,
            "colorbar": True,
            "vmin": 0,
            "vmax": 10,
        }
    }

    mock_post_process = mocker.MagicMock()

    solara.render(
        SolaraViz(
            model,
            components=[
                make_altair_space(
                    agent_portrayal,
                    post_process=mock_post_process,
                    propertylayer_portrayal=propertylayer_portrayal,
                )
            ],
        )
    )

    args, kwargs = mock_space_altair.call_args
    assert args == (model, agent_portrayal)
    assert kwargs == {
        "post_process": mock_post_process,
        "propertylayer_portrayal": propertylayer_portrayal,
    }
    mock_post_process.assert_called_once()
    assert mock_chart_property_layer.call_count == 1


def test_legacy_voronoi_grid_matplotlib(mocker):
    mock_space_matplotlib = mocker.spy(
        mesa.visualization.components.matplotlib_components, "SpaceMatplotlib"
    )

    def agent_portrayal(agent):
        return {"marker": "o", "color": "gray"}

    voronoi_model = mesa.Model()
    voronoi_model.grid = mesa.discrete_space.VoronoiGrid(
        centroids_coordinates=[(0, 1), (0, 0), (1, 0)],
        random=random.Random(42),
    )

    solara.render(
        SolaraViz(
            voronoi_model,
            components=[make_mpl_space_component(agent_portrayal)]
        )
    )

    assert mock_space_matplotlib.call_count == 1


def test_legacy_custom_space_component(mocker):
    model = MockModel()

    class AltSpace:
        @staticmethod
        def drawer(model):
            return

    altspace_drawer = mocker.spy(AltSpace, "drawer")
    solara.render(SolaraViz(model, components=[AltSpace.drawer]))
    altspace_drawer.assert_called_with(model)
