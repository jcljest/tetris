# mods/registry.py
class Services:
    def __init__(self): self._f = {}
    def register(self, key: str, factory): self._f[key] = factory
    def resolve(self, key: str, **kwargs): return self._f[key](**kwargs)

services = Services()
