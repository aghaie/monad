from app.server.main import build_routes, dispatch


def call(method, path):
    routes = build_routes()
    return dispatch(routes, method, path)


def test_modules_endpoint_lists_self_interpret():
    status, payload = call("GET", "/api/modules")
    assert status == 200
    assert any(m["id"] == "self-interpret" for m in payload)


def test_verse_endpoint():
    status, payload = call("GET", "/api/verse/1:1")
    assert status == 200
    assert payload["ref"] == "1:1"


def test_interpret_endpoint_canonical():
    status, payload = call("GET", "/api/interpret/2:255")
    assert status == 200
    assert any(r["ayah"] == "7:97" for r in payload)


def test_communities_endpoint():
    status, payload = call("GET", "/api/graph/communities")
    assert status == 200
    assert len(payload["nodes"]) == 114


def test_unknown_route_404():
    status, _ = call("GET", "/api/nope")
    assert status == 404
