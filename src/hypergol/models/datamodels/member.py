from dataclasses import dataclass
from dataclasses import field    
    

@dataclass
class Member:
    name: str
    type: str
    isList: bool = False
    innerType: str = ""
    needConversion: bool = False