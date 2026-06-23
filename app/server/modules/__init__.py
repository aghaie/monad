"""Module registry. Add a module: create modules/<name>.py exposing spec(),
then append its spec() here. The server mounts every route automatically."""
from app.server.modules import self_interpret

MODULE_REGISTRY = [self_interpret.spec()]
