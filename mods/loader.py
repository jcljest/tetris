# mods/loader.py
import importlib
import json
import pathlib
from typing import Any, Dict

def load_manifest(path: str) -> Dict[str, Any]:
    """
    Load a mod manifest (JSON) mapping identifiers to Python import strings.
    Example JSON:
    {
      "rules": "tetris.core.rules_default.DefaultRuleSet",
      "shapes": "tetris.core.shapes.SrsShapeSet",
      "bag": "tetris.core.bag.SevenBag",
      "theme": "tetris.render.theme_default.DefaultTheme"
    }
    """
    p = pathlib.Path(path)
    if not p.exists():
        print(f"[mods.loader] Manifest not found: {path}")
        return {}
    data = json.loads(p.read_text())
    instances: Dict[str, Any] = {}
    for key, dotted in data.items():
        try:
            module_name, cls_name = dotted.rsplit(".", 1)
            mod = importlib.import_module(module_name)
            cls = getattr(mod, cls_name)
            instances[key] = cls()  # instantiate default constructor
        except Exception as e:
            print(f"[mods.loader] Could not load {key}='{dotted}': {e}")
    return instances
