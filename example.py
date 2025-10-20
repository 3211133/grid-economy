#!/usr/bin/env python
"""Example simulation demonstrating the grid economy system."""

import random
from grid_economy import Good, OrganicAgent, InorganicAgent, World


def run_simulation(steps=100, world_size=(20, 20)):
    """Run a simple simulation.
    
    Args:
        steps: Number of simulation steps to run
        world_size: (width, height) of the world grid
    """
    print("=== Grid Economy Simulation ===\n")
    
    # Reset goods from any previous runs
    Good.reset_goods()
    
    # Create initial good types
    food = Good("food", {"color": "green", "nutritional": True})
    water = Good("water", {"color": "blue", "liquid": True})
    energy = Good("energy", {"color": "yellow"})
    
    print(f"Initial goods: {list(Good.get_all_good_types().keys())}")
    
    # Create world
    world = World(world_size[0], world_size[1])
    print(f"Created world: {world_size[0]}x{world_size[1]} grid\n")
    
    # Add initial resources scattered around
    print("Distributing initial resources...")
    for _ in range(50):
        x = random.randint(0, world_size[0] - 1)
        y = random.randint(0, world_size[1] - 1)
        world.add_good((x, y), food, random.uniform(10, 50))
    
    for _ in range(30):
        x = random.randint(0, world_size[0] - 1)
        y = random.randint(0, world_size[1] - 1)
        world.add_good((x, y), water, random.uniform(10, 30))
    
    # Add initial organic agents
    print("Creating initial organic agents...")
    for _ in range(5):
        x = random.randint(0, world_size[0] - 1)
        y = random.randint(0, world_size[1] - 1)
        
        agent = OrganicAgent(
            position=(x, y),
            consumes=food,
            produces=energy,
            consumption_rate=1.0,
            production_rate=1.5,
            search_radius=2,
            reproduction_threshold=20.0,
            starvation_threshold=0.5,
            mutation_rate=0.15
        )
        agent.resources_accumulated = 10.0  # Start with some resources
        world.add_agent(agent)
    
    # Add a few inorganic agents
    print("Creating initial inorganic agents...")
    for _ in range(3):
        x = random.randint(0, world_size[0] - 1)
        y = random.randint(0, world_size[1] - 1)
        
        agent = InorganicAgent(
            position=(x, y),
            consumes=water,
            produces=food,
            consumption_rate=0.5,
            production_rate=1.0,
            search_radius=1
        )
        world.add_agent(agent)
    
    print(f"\nInitial state: {world}")
    print("-" * 60)
    
    # Run simulation
    print(f"\nRunning simulation for {steps} steps...\n")
    
    # Report every N steps
    report_interval = max(1, steps // 10)
    
    for step in range(steps):
        world.step()
        
        if (step + 1) % report_interval == 0:
            stats = world.get_statistics()
            print(f"Step {step + 1:3d}: "
                  f"Agents={stats['total_agents']:3d} "
                  f"(Organic={stats['organic_agents']:2d}, "
                  f"Inorganic={stats['inorganic_agents']:2d}), "
                  f"Good types={stats['good_types']}")
            
            # Show good totals
            if stats['good_totals']:
                good_summary = ", ".join(
                    f"{good.good_type_id}={amount:.1f}"
                    for good, amount in list(stats['good_totals'].items())[:5]
                )
                print(f"         Goods: {good_summary}")
    
    # Final statistics
    print("\n" + "=" * 60)
    print("=== Final Statistics ===")
    stats = world.get_statistics()
    
    print(f"\nTime steps: {stats['time']}")
    print(f"Total agents: {stats['total_agents']}")
    print(f"  - Organic agents: {stats['organic_agents']}")
    print(f"  - Inorganic agents: {stats['inorganic_agents']}")
    print(f"Total good types: {stats['good_types']}")
    
    print("\nGood types:")
    for good_id, good in Good.get_all_good_types().items():
        total = stats['good_totals'].get(good, 0)
        print(f"  - {good_id}: {total:.2f} units")
        if good.characteristics:
            print(f"    Characteristics: {good.characteristics}")
    
    print("\nAgent positions (first 10):")
    for i, (agent_id, agent) in enumerate(list(world.agents.items())[:10]):
        agent_type = "Organic" if isinstance(agent, OrganicAgent) else "Inorganic"
        print(f"  - {agent_type} at {agent.position}: "
              f"consumes {agent.consumes.good_type_id}, "
              f"produces {agent.produces.good_type_id}")
    
    if len(world.agents) > 10:
        print(f"  ... and {len(world.agents) - 10} more agents")
    
    print("\n" + "=" * 60)
    print("Simulation complete!")
    
    return world


if __name__ == "__main__":
    # Set random seed for reproducibility
    random.seed(42)
    
    # Run simulation
    world = run_simulation(steps=100, world_size=(20, 20))
    
    print("\n💡 Observations:")
    print("  - Organic agents reproduce when they have enough resources")
    print("  - Organic agents die when they run out of resources")
    print("  - Inorganic agents continue working as long as resources are available")
    print("  - New good types may emerge through mutations")
    print("  - Agents inherit traits from parents with some mutations")
