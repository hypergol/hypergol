from dataclasses import dataclass
from dataclasses import field
from typing import List
from typing import Dict


@dataclass
class DataModelType:
    name: str
    doAddList: bool = False
    dependencies: List[str] = field(default_factory=list)
    members: List[Dict] = field(default_factory=list)