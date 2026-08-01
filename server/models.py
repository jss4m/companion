from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class Prompt:
    user_message: str
    memories: List[Dict[str, str]]
    personality: str
    plan: Dict[str, Any]