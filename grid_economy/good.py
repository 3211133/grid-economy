"""Good class representing different types of goods in the simulation."""

import uuid
from typing import Dict, Any


class Good:
    """Represents a type of good that can be consumed and produced by agents.
    
    Goods have a unique ID and can have additional characteristics attached.
    """
    
    # Class variable to track all good types
    _good_types: Dict[str, 'Good'] = {}
    _next_type_id = 0
    
    def __init__(self, good_type_id: str = None, characteristics: Dict[str, Any] = None):
        """Initialize a good type.
        
        Args:
            good_type_id: Unique identifier for this good type. If None, auto-generated.
            characteristics: Dictionary of characteristics for this good type.
        """
        if good_type_id is None:
            good_type_id = f"good_{Good._next_type_id}"
            Good._next_type_id += 1
        
        self.good_type_id = good_type_id
        self.characteristics = characteristics or {}
        
        # Register this good type
        Good._good_types[good_type_id] = self
    
    def __repr__(self):
        return f"Good(type={self.good_type_id})"
    
    def __eq__(self, other):
        if not isinstance(other, Good):
            return False
        return self.good_type_id == other.good_type_id
    
    def __hash__(self):
        return hash(self.good_type_id)
    
    @classmethod
    def get_good_type(cls, good_type_id: str) -> 'Good':
        """Get a good type by its ID."""
        return cls._good_types.get(good_type_id)
    
    @classmethod
    def get_all_good_types(cls) -> Dict[str, 'Good']:
        """Get all registered good types."""
        return cls._good_types.copy()
    
    @classmethod
    def reset_goods(cls):
        """Reset all goods (useful for testing)."""
        cls._good_types.clear()
        cls._next_type_id = 0
