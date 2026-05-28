"""Route fixture loader tests."""

from __future__ import annotations

from actions.chat.routing.routes_loader import load_route_definitions


def test_router_routes_fixture_has_minimum_routes() -> None:
    routes = load_route_definitions()
    assert len(routes) >= 6
    for route in routes:
        assert len(route.utterances) >= 3
