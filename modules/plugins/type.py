from dataclasses import dataclass, field, asdict

class MetaBase:
    def to_dict(self):
        return asdict(self)
    def __getitem__(self, key):
        return getattr(self, key)