from dataclasses import dataclass


@dataclass
class example2:
    a: int

    @classmethod
    def from_data(cls, data):
        return cls(**data)