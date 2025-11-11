# mods/loader.py
import importlib, json, pathlib

def load_manifest(path: str):
    data = json.loads(pathlib.Path(path).read_text())
    # { "rules": "my_mod.rules.GuidelineRules", "shapes": "...", "bag": "..." }
    instances = {}
    for key, dotted in data.items():
        module, cls = dotted.rsplit(".", 1)
        impl = getattr(importlib.import_module(module), cls)
        instances[key] = impl()
    return instances
