# mods/registry.py
class Services:
    def __init__(self):
        self._registry = {}

    def register(self, key: str, factory):
        self._registry[key] = factory

    def resolve(self, key: str, **kwargs):
        if key not in self._registry:
            raise KeyError(f"No service registered for '{key}'")
        return self._registry[key](**kwargs)

services = Services()
