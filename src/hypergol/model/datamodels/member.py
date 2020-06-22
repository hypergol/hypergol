from dataclasses import dataclass


@dataclass
class Member:
    name: str
    type: str
    isList: bool = False
    innerType: str = ""
    needConversion: bool = False
