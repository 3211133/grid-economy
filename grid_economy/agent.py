"""Agent classes representing different types of agents in the simulation."""

import random
import uuid
from typing import Tuple, Optional, Dict
from .good import Good


class Agent:
    """Base class for all agents in the simulation.
    
    Agents consume goods and produce goods. They exist at a specific position
    on the grid and have conversion mechanisms.
    """
    
    def __init__(self, 
                 position: Tuple[int, int],
                 consumes: Good,
                 produces: Good,
                 consumption_rate: float = 1.0,
                 production_rate: float = 1.0,
                 search_radius: int = 1):
        """Initialize an agent.
        
        Args:
            position: (x, y) position on the grid
            consumes: Type of good this agent consumes
            produces: Type of good this agent produces
            consumption_rate: Amount of good consumed per time step
            production_rate: Amount of good produced per time step
            search_radius: Radius to search for goods
        """
        self.agent_id = str(uuid.uuid4())
        self.position = position
        self.consumes = consumes
        self.produces = produces
        self.consumption_rate = consumption_rate
        self.production_rate = production_rate
        self.search_radius = search_radius
        self.alive = True
    
    def can_convert(self, available_goods: Dict[Good, float]) -> bool:
        """Check if the agent can perform conversion given available goods.
        
        Args:
            available_goods: Dictionary of available good types and their amounts
            
        Returns:
            True if conversion is possible
        """
        return available_goods.get(self.consumes, 0) >= self.consumption_rate
    
    def convert(self, available_goods: Dict[Good, float]) -> Tuple[Dict[Good, float], Dict[Good, float]]:
        """Perform the conversion if possible.
        
        Args:
            available_goods: Dictionary of available good types and their amounts
            
        Returns:
            Tuple of (consumed_goods, produced_goods)
        """
        if not self.can_convert(available_goods):
            return {}, {}
        
        consumed = {self.consumes: self.consumption_rate}
        produced = {self.produces: self.production_rate}
        
        return consumed, produced
    
    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.agent_id[:8]}, pos={self.position})"


class OrganicAgent(Agent):
    """Organic agent that can reproduce and die based on resource availability.
    
    Organic agents:
    - Die if they don't have enough resources
    - Reproduce if they have sufficient resources
    - Inherit traits from parent with possible mutations
    - Can create inorganic agents
    """
    
    def __init__(self,
                 position: Tuple[int, int],
                 consumes: Good,
                 produces: Good,
                 consumption_rate: float = 1.0,
                 production_rate: float = 1.0,
                 search_radius: int = 1,
                 reproduction_threshold: float = 10.0,
                 starvation_threshold: float = 0.5,
                 mutation_rate: float = 0.1):
        """Initialize an organic agent.
        
        Args:
            position: (x, y) position on the grid
            consumes: Type of good this agent consumes
            produces: Type of good this agent produces
            consumption_rate: Amount of good consumed per time step
            production_rate: Amount of good produced per time step
            search_radius: Radius to search for goods
            reproduction_threshold: Resource level needed to reproduce
            starvation_threshold: Resource level below which agent dies
            mutation_rate: Probability of mutation during reproduction
        """
        super().__init__(position, consumes, produces, consumption_rate, 
                        production_rate, search_radius)
        self.reproduction_threshold = reproduction_threshold
        self.starvation_threshold = starvation_threshold
        self.mutation_rate = mutation_rate
        self.resources_accumulated = 0.0
    
    def update(self, consumed: Dict[Good, float], produced: Dict[Good, float]):
        """Update agent state after conversion.
        
        The agent benefits from the conversion process - the produced goods
        represent accumulated resources for the agent.
        
        Args:
            consumed: Goods consumed this time step
            produced: Goods produced this time step
        """
        # Track net resources from production (this represents the agent's benefit)
        produced_amount = produced.get(self.produces, 0)
        self.resources_accumulated += produced_amount
        
        # Check for starvation (death if no resources left)
        if self.resources_accumulated < self.starvation_threshold:
            self.alive = False
    
    def can_reproduce(self) -> bool:
        """Check if agent has enough resources to reproduce."""
        return self.resources_accumulated >= self.reproduction_threshold
    
    def reproduce(self, 
                  world_size: Tuple[int, int],
                  new_good_probability: float = 0.05) -> Optional['OrganicAgent']:
        """Create a child agent with inherited traits and possible mutations.
        
        Args:
            world_size: (width, height) of the world
            new_good_probability: Probability of creating a new good type
            
        Returns:
            New OrganicAgent if reproduction successful, None otherwise
        """
        if not self.can_reproduce():
            return None
        
        # Pay reproduction cost
        self.resources_accumulated -= self.reproduction_threshold / 2
        
        # Find nearby position for offspring
        dx = random.randint(-1, 1)
        dy = random.randint(-1, 1)
        new_x = max(0, min(world_size[0] - 1, self.position[0] + dx))
        new_y = max(0, min(world_size[1] - 1, self.position[1] + dy))
        new_position = (new_x, new_y)
        
        # Inherit traits with possible mutation
        consumes = self.consumes
        produces = self.produces
        
        if random.random() < self.mutation_rate:
            # Mutation: change what is consumed or produced
            if random.random() < 0.5:
                # Mutate consumption
                existing_goods = list(Good.get_all_good_types().values())
                if existing_goods:
                    consumes = random.choice(existing_goods)
            else:
                # Mutate production
                if random.random() < new_good_probability:
                    # Create new good type
                    produces = Good()
                else:
                    existing_goods = list(Good.get_all_good_types().values())
                    if existing_goods:
                        produces = random.choice(existing_goods)
        
        consumption_rate = self.consumption_rate
        production_rate = self.production_rate
        
        if random.random() < self.mutation_rate:
            # Mutate rates slightly
            consumption_rate *= random.uniform(0.8, 1.2)
            production_rate *= random.uniform(0.8, 1.2)
        
        child = OrganicAgent(
            position=new_position,
            consumes=consumes,
            produces=produces,
            consumption_rate=consumption_rate,
            production_rate=production_rate,
            search_radius=self.search_radius,
            reproduction_threshold=self.reproduction_threshold,
            starvation_threshold=self.starvation_threshold,
            mutation_rate=self.mutation_rate
        )
        
        return child
    
    def create_inorganic_agent(self,
                               world_size: Tuple[int, int],
                               new_good_probability: float = 0.05) -> Optional['InorganicAgent']:
        """Create an inorganic agent with random conversion mechanism.
        
        Args:
            world_size: (width, height) of the world
            new_good_probability: Probability of creating a new good type
            
        Returns:
            New InorganicAgent if creation successful, None otherwise
        """
        # Inorganic agents have random conversion mechanisms
        existing_goods = list(Good.get_all_good_types().values())
        if not existing_goods:
            return None
        
        consumes = random.choice(existing_goods)
        
        # Probabilistically create new good type for production
        if random.random() < new_good_probability:
            produces = Good()
        else:
            produces = random.choice(existing_goods)
        
        # Find nearby position
        dx = random.randint(-1, 1)
        dy = random.randint(-1, 1)
        new_x = max(0, min(world_size[0] - 1, self.position[0] + dx))
        new_y = max(0, min(world_size[1] - 1, self.position[1] + dy))
        new_position = (new_x, new_y)
        
        inorganic = InorganicAgent(
            position=new_position,
            consumes=consumes,
            produces=produces,
            consumption_rate=random.uniform(0.5, 2.0),
            production_rate=random.uniform(0.5, 2.0),
            search_radius=random.randint(1, 3)
        )
        
        return inorganic


class InorganicAgent(Agent):
    """Inorganic agent that converts goods but doesn't die or reproduce.
    
    Inorganic agents:
    - Stop converting when no resources available
    - Don't die from lack of resources
    - Don't reproduce
    """
    
    def __init__(self,
                 position: Tuple[int, int],
                 consumes: Good,
                 produces: Good,
                 consumption_rate: float = 1.0,
                 production_rate: float = 1.0,
                 search_radius: int = 1):
        """Initialize an inorganic agent.
        
        Args:
            position: (x, y) position on the grid
            consumes: Type of good this agent consumes
            produces: Type of good this agent produces
            consumption_rate: Amount of good consumed per time step
            production_rate: Amount of good produced per time step
            search_radius: Radius to search for goods
        """
        super().__init__(position, consumes, produces, consumption_rate,
                        production_rate, search_radius)
    
    def convert(self, available_goods: Dict[Good, float]) -> Tuple[Dict[Good, float], Dict[Good, float]]:
        """Perform conversion if resources available, otherwise do nothing.
        
        Args:
            available_goods: Dictionary of available good types and their amounts
            
        Returns:
            Tuple of (consumed_goods, produced_goods)
        """
        if not self.can_convert(available_goods):
            # Inorganic agents just stop converting, they don't die
            return {}, {}
        
        return super().convert(available_goods)
