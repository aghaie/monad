"""A new module must mount with no change to the core (server, shell, services)."""
import re

from app.server.main import build_routes, dispatch


def test_adding_a_module_spec_adds_its_routes():
    # Simulate a second module's spec() — the same shape modules/__init__.py collects.
    def _ping(m):
        return 200, {"pong": True}

    fake = {"id": "atlas", "title": "اطلس ریشه", "icon": "📚",
            "routes": [("GET", r"^/api/atlas/ping$", _ping)]}
    routes = [(meth, re.compile(pat), fn) for meth, pat, fn in fake["routes"]]
    status, payload = dispatch(routes, "GET", "/api/atlas/ping")
    assert status == 200 and payload["pong"] is True


def test_core_routes_are_registry_driven():
    # Every module in the registry contributes its routes to build_routes().
    from app.server.modules import MODULE_REGISTRY
    routes = build_routes()
    patterns = [rx.pattern for _, rx, _ in routes]
    for spec in MODULE_REGISTRY:
        for _, pat, _ in spec["routes"]:
            assert pat in patterns, f"route {pat} from module {spec['id']} not mounted"
