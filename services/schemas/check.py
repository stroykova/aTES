import pathlib
import importlib.util
import sys
from pydantic import BaseModel

schemas = pathlib.Path(__file__).parent / 'schemas'
registry = {}
for f in schemas.rglob('*.py'):
    parts = list(f.parts[-3:])
    parts[-1] = parts[-1].split('.')[0]
    print(parts)
    spec = importlib.util.spec_from_file_location(".".join(parts), f)
    module = importlib.util.module_from_spec(spec)
    sys.modules[".".join(parts)] = module
    spec.loader.exec_module(module)
    registry[".".join(parts)] = module.EVENT_CLASS
print(registry)


def check_event(event: dict):
    model_class = registry[f"{event['event_domain']}.{event['event_name']}.v{event['event_version']}"]
    model_class(**event)
    