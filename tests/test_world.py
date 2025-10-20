"""Tests for World class."""

import pytest
from grid_economy.good import Good
from grid_economy.agent import OrganicAgent, InorganicAgent
from grid_economy.world import World


@pytest.fixture
def setup_world():
    """Setup world and goods for testing."""
    Good.reset_goods()
    good_x = Good("X")
    good_y = Good("Y")
    world = World(10, 10)
    return world, good_x, good_y


def test_world_creation():
    """Test creating a world."""
    world = World(20, 15)
    assert world.width == 20
    assert world.height == 15
    assert world.time == 0
    assert len(world.agents) == 0


def test_add_remove_agent(setup_world):
    """Test adding and removing agents."""
    world, good_x, good_y = setup_world
    
    agent = OrganicAgent(
        position=(5, 5),
        consumes=good_x,
        produces=good_y
    )
    
    world.add_agent(agent)
    assert len(world.agents) == 1
    assert agent.agent_id in world.agents
    
    world.remove_agent(agent.agent_id)
    assert len(world.agents) == 0


def test_add_get_goods(setup_world):
    """Test adding and getting goods."""
    world, good_x, good_y = setup_world
    
    world.add_good((5, 5), good_x, 10.0)
    world.add_good((5, 5), good_y, 5.0)
    
    goods = world.get_goods_at((5, 5))
    assert goods[good_x] == 10.0
    assert goods[good_y] == 5.0


def test_get_goods_nearby(setup_world):
    """Test getting goods in radius."""
    world, good_x, good_y = setup_world
    
    # Add goods at center and nearby
    world.add_good((5, 5), good_x, 10.0)
    world.add_good((6, 5), good_x, 5.0)
    world.add_good((5, 6), good_y, 3.0)
    
    nearby = world.get_goods_nearby((5, 5), radius=1)
    
    assert nearby[good_x] == 15.0  # 10 + 5
    assert nearby[good_y] == 3.0


def test_consume_good(setup_world):
    """Test consuming goods."""
    world, good_x, good_y = setup_world
    
    world.add_good((5, 5), good_x, 10.0)
    
    consumed = world.consume_good((5, 5), good_x, 3.0)
    assert consumed == 3.0
    
    remaining = world.get_goods_at((5, 5))
    assert remaining[good_x] == 7.0


def test_consume_good_nearby(setup_world):
    """Test consuming goods from nearby cells."""
    world, good_x, good_y = setup_world
    
    world.add_good((5, 5), good_x, 5.0)
    world.add_good((6, 5), good_x, 5.0)
    
    consumed = world.consume_good_nearby((5, 5), good_x, 8.0, radius=1)
    assert consumed == 8.0


def test_world_step_with_organic_agent(setup_world):
    """Test world simulation step with organic agent."""
    world, good_x, good_y = setup_world
    
    # Create agent that consumes X and produces Y
    agent = OrganicAgent(
        position=(5, 5),
        consumes=good_x,
        produces=good_y,
        consumption_rate=1.0,
        production_rate=2.0,
        starvation_threshold=0.0
    )
    
    world.add_agent(agent)
    
    # Add some good X nearby
    world.add_good((5, 5), good_x, 10.0)
    
    initial_time = world.time
    world.step()
    
    assert world.time == initial_time + 1
    
    # Agent should have consumed X and produced Y
    goods = world.get_goods_at((5, 5))
    assert goods[good_x] < 10.0  # Some consumed
    assert good_y in goods  # Y produced


def test_organic_agent_death_in_world(setup_world):
    """Test organic agent death from starvation."""
    world, good_x, good_y = setup_world
    
    agent = OrganicAgent(
        position=(5, 5),
        consumes=good_x,
        produces=good_y,
        starvation_threshold=1.0
    )
    agent.resources_accumulated = 0.0
    
    world.add_agent(agent)
    assert len(world.agents) == 1
    
    # Step without resources - agent should die
    world.step()
    
    assert len(world.agents) == 0


def test_inorganic_agent_survives_without_resources(setup_world):
    """Test inorganic agent survives without resources."""
    world, good_x, good_y = setup_world
    
    agent = InorganicAgent(
        position=(5, 5),
        consumes=good_x,
        produces=good_y
    )
    
    world.add_agent(agent)
    
    # Step without resources
    world.step()
    world.step()
    world.step()
    
    # Agent should still be alive
    assert len(world.agents) == 1
    assert agent.agent_id in world.agents


def test_world_statistics(setup_world):
    """Test world statistics."""
    world, good_x, good_y = setup_world
    
    # Add agents
    organic = OrganicAgent((0, 0), good_x, good_y)
    inorganic = InorganicAgent((1, 1), good_x, good_y)
    world.add_agent(organic)
    world.add_agent(inorganic)
    
    # Add goods
    world.add_good((5, 5), good_x, 10.0)
    world.add_good((6, 6), good_y, 5.0)
    
    stats = world.get_statistics()
    
    assert stats['total_agents'] == 2
    assert stats['organic_agents'] == 1
    assert stats['inorganic_agents'] == 1
    assert stats['good_types'] == 2
    assert stats['good_totals'][good_x] == 10.0
    assert stats['good_totals'][good_y] == 5.0
