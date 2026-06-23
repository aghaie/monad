"""Module 1: the self-interpretation engine — its module-specific routes."""
from app.server.services.network import interpret

MODULE = {"id": "self-interpret", "title": "خودتفسیر", "icon": "🕸"}


def _interpret(m):
    return 200, interpret(int(m["s"]), int(m["a"]))


ROUTES = [("GET", r"^/api/interpret/(?P<s>\d+):(?P<a>\d+)$", _interpret)]


def spec():
    return {**MODULE, "routes": ROUTES}
