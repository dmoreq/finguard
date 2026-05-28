"""Load semantic router route definitions from YAML."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

DEFAULT_ROUTES_PATH = (
    Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "router_routes.yaml"
)


@dataclass(frozen=True)
class RouteDefinition:
    name: str
    utterances: tuple[str, ...]


def load_route_definitions(path: Path | None = None) -> list[RouteDefinition]:
    routes_path = path or DEFAULT_ROUTES_PATH
    raw = yaml.safe_load(routes_path.read_text())
    routes: list[RouteDefinition] = []
    for item in raw.get("routes", []):
        routes.append(
            RouteDefinition(
                name=str(item["name"]),
                utterances=tuple(str(u) for u in item["utterances"]),
            )
        )
    return routes
