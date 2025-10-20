"""World class representing the 2D grid simulation environment."""

import random
from typing import Dict, List, Tuple, Optional
from .good import Good
from .agent import Agent, OrganicAgent, InorganicAgent


class World:
    """Represents the 2D grid world where agents and goods exist and interact.
    
    The world manages:
    - A 2D grid of cells
    - Agents at various positions
    - Goods distributed across the grid
    - Time-based event execution and updates
    """
    
    def __init__(self, 
                 width: int, 
                 height: int,
                 organic_reproduction_chance: float = 0.3,
                 inorganic_creation_chance: float = 0.05):
        """Initialize the world.
        
        Args:
            width: Width of the grid
            height: Height of the grid
            organic_reproduction_chance: Probability of reproduction when able (0-1)
            inorganic_creation_chance: Probability of creating inorganic agent per step (0-1)
        """
        self.width = width
        self.height = height
        self.time = 0
        self.organic_reproduction_chance = organic_reproduction_chance
        self.inorganic_creation_chance = inorganic_creation_chance
        
        # Agents indexed by their ID
        self.agents: Dict[str, Agent] = {}
        
        # Goods stored per cell: grid[x][y][good_type] = amount
        self.grid: List[List[Dict[Good, float]]] = [
            [dict() for _ in range(height)] 
            for _ in range(width)
        ]
    
    def add_agent(self, agent: Agent):
        """Add an agent to the world.
        
        Args:
            agent: Agent to add
        """
        self.agents[agent.agent_id] = agent
    
    def remove_agent(self, agent_id: str):
        """Remove an agent from the world.
        
        Args:
            agent_id: ID of agent to remove
        """
        if agent_id in self.agents:
            del self.agents[agent_id]
    
    def add_good(self, position: Tuple[int, int], good: Good, amount: float):
        """Add a good at a specific position.
        
        Args:
            position: (x, y) position
            good: Type of good
            amount: Amount to add
        """
        x, y = position
        if 0 <= x < self.width and 0 <= y < self.height:
            if good not in self.grid[x][y]:
                self.grid[x][y][good] = 0
            self.grid[x][y][good] += amount
    
    def get_goods_at(self, position: Tuple[int, int]) -> Dict[Good, float]:
        """Get all goods at a specific position.
        
        Args:
            position: (x, y) position
            
        Returns:
            Dictionary of goods and their amounts
        """
        x, y = position
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[x][y].copy()
        return {}
    
    def get_goods_nearby(self, position: Tuple[int, int], radius: int) -> Dict[Good, float]:
        """Get all goods within a radius of a position.
        
        Args:
            position: (x, y) center position
            radius: Search radius
            
        Returns:
            Dictionary of goods and their total amounts within radius
        """
        x, y = position
        nearby_goods: Dict[Good, float] = {}
        
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    for good, amount in self.grid[nx][ny].items():
                        if good not in nearby_goods:
                            nearby_goods[good] = 0
                        nearby_goods[good] += amount
        
        return nearby_goods
    
    def consume_good(self, position: Tuple[int, int], good: Good, amount: float) -> float:
        """Consume a good from a specific position.
        
        Args:
            position: (x, y) position
            good: Type of good to consume
            amount: Amount to consume
            
        Returns:
            Actual amount consumed (may be less if not enough available)
        """
        x, y = position
        if 0 <= x < self.width and 0 <= y < self.height:
            available = self.grid[x][y].get(good, 0)
            consumed = min(available, amount)
            self.grid[x][y][good] = available - consumed
            if self.grid[x][y][good] <= 0:
                del self.grid[x][y][good]
            return consumed
        return 0
    
    def consume_good_nearby(self, position: Tuple[int, int], good: Good, 
                           amount: float, radius: int) -> float:
        """Consume a good from nearby positions.
        
        Args:
            position: (x, y) center position
            good: Type of good to consume
            amount: Amount to consume
            radius: Search radius
            
        Returns:
            Actual amount consumed
        """
        x, y = position
        remaining = amount
        
        # Build list of positions with this good
        positions_with_good = []
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if good in self.grid[nx][ny] and self.grid[nx][ny][good] > 0:
                        positions_with_good.append((nx, ny))
        
        # Consume from positions
        for pos in positions_with_good:
            if remaining <= 0:
                break
            consumed = self.consume_good(pos, good, remaining)
            remaining -= consumed
        
        return amount - remaining
    
    def step(self):
        """Execute one time step of the simulation.
        
        This processes all agents:
        1. Check if organic agents should die
        2. Attempt conversion for each agent
        3. Check if organic agents should reproduce or create inorganic agents
        4. Remove dead agents
        """
        self.time += 1
        
        # Track new agents to add after iteration
        new_agents: List[Agent] = []
        dead_agents: List[str] = []
        
        # Process each agent
        for agent_id, agent in list(self.agents.items()):
            if not agent.alive:
                dead_agents.append(agent_id)
                continue
            
            # Get available goods nearby
            nearby_goods = self.get_goods_nearby(agent.position, agent.search_radius)
            
            # Attempt conversion
            if agent.can_convert(nearby_goods):
                consumed_dict, produced_dict = agent.convert(nearby_goods)
                
                # Actually consume and produce goods
                for good, amount in consumed_dict.items():
                    self.consume_good_nearby(
                        agent.position, good, amount, agent.search_radius
                    )
                
                for good, amount in produced_dict.items():
                    self.add_good(agent.position, good, amount)
                
                # Update organic agent state after conversion
                if isinstance(agent, OrganicAgent):
                    agent.update(consumed_dict, produced_dict)
            
            # Check for organic agent specific behaviors
            if isinstance(agent, OrganicAgent):
                # Check starvation
                if agent.resources_accumulated < agent.starvation_threshold:
                    agent.alive = False
                    dead_agents.append(agent_id)
                    continue
                
                # Check reproduction
                if agent.can_reproduce():
                    if random.random() < self.organic_reproduction_chance:
                        child = agent.reproduce((self.width, self.height))
                        if child:
                            new_agents.append(child)
                
                # Chance to create inorganic agent
                if random.random() < self.inorganic_creation_chance:
                    inorganic = agent.create_inorganic_agent((self.width, self.height))
                    if inorganic:
                        new_agents.append(inorganic)
        
        # Remove dead agents
        for agent_id in dead_agents:
            self.remove_agent(agent_id)
        
        # Add new agents
        for agent in new_agents:
            self.add_agent(agent)
    
    def get_statistics(self) -> Dict:
        """Get statistics about the current world state.
        
        Returns:
            Dictionary with various statistics
        """
        organic_count = sum(1 for a in self.agents.values() if isinstance(a, OrganicAgent))
        inorganic_count = sum(1 for a in self.agents.values() if isinstance(a, InorganicAgent))
        
        good_totals: Dict[Good, float] = {}
        for x in range(self.width):
            for y in range(self.height):
                for good, amount in self.grid[x][y].items():
                    if good not in good_totals:
                        good_totals[good] = 0
                    good_totals[good] += amount
        
        return {
            'time': self.time,
            'total_agents': len(self.agents),
            'organic_agents': organic_count,
            'inorganic_agents': inorganic_count,
            'good_types': len(Good.get_all_good_types()),
            'good_totals': good_totals
        }
    
    def __repr__(self):
        stats = self.get_statistics()
        return (f"World(time={self.time}, size={self.width}x{self.height}, "
                f"agents={stats['total_agents']}, goods={stats['good_types']})")
