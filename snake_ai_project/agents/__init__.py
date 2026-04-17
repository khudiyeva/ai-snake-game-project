from agents.astar_agent import AStarAgent
from agents.base import BaseSnakeAgent
from agents.human_agent import HumanAgent
from agents.rl_agent import RLAgent


AGENT_REGISTRY: dict[str, type[BaseSnakeAgent]] = {
    "human": HumanAgent,
    "astar": AStarAgent,
    "rl": RLAgent,
}

ACTIVE_MODES = ("human", "astar")
DISABLED_MODES = ("rl",)


def create_agent(mode: str) -> BaseSnakeAgent:
    agent_class = AGENT_REGISTRY.get(mode)
    if agent_class is None:
        supported = ", ".join(sorted(AGENT_REGISTRY))
        raise ValueError(f"Unsupported mode '{mode}'. Expected one of: {supported}")
    return agent_class()
