"""Tests for Agent classes."""

import pytest
from grid_economy.good import Good
from grid_economy.agent import Agent, OrganicAgent, InorganicAgent


@pytest.fixture
def setup_goods():
    """Setup goods for testing."""
    Good.reset_goods()
    good_x = Good("X")
    good_y = Good("Y")
    return good_x, good_y


def test_agent_creation(setup_goods):
    """Test creating a basic agent."""
    good_x, good_y = setup_goods
    agent = Agent(
        position=(5, 5),
        consumes=good_x,
        produces=good_y,
        consumption_rate=1.0,
        production_rate=2.0
    )
    
    assert agent.position == (5, 5)
    assert agent.consumes == good_x
    assert agent.produces == good_y
    assert agent.alive is True


def test_agent_can_convert(setup_goods):
    """Test agent conversion check."""
    good_x, good_y = setup_goods
    agent = Agent(
        position=(0, 0),
        consumes=good_x,
        produces=good_y,
        consumption_rate=2.0
    )
    
    # Enough resources
    assert agent.can_convert({good_x: 5.0})
    
    # Not enough resources
    assert not agent.can_convert({good_x: 1.0})
    
    # No resources
    assert not agent.can_convert({})


def test_agent_convert(setup_goods):
    """Test agent conversion."""
    good_x, good_y = setup_goods
    agent = Agent(
        position=(0, 0),
        consumes=good_x,
        produces=good_y,
        consumption_rate=2.0,
        production_rate=3.0
    )
    
    consumed, produced = agent.convert({good_x: 5.0})
    
    assert consumed == {good_x: 2.0}
    assert produced == {good_y: 3.0}


def test_organic_agent_starvation(setup_goods):
    """Test organic agent starvation."""
    good_x, good_y = setup_goods
    agent = OrganicAgent(
        position=(0, 0),
        consumes=good_x,
        produces=good_y,
        starvation_threshold=1.0
    )
    
    # Agent starts alive
    assert agent.alive is True
    
    # Simulate starvation
    agent.resources_accumulated = 0.0
    agent.update({}, {})
    
    assert agent.alive is False


def test_organic_agent_reproduction(setup_goods):
    """Test organic agent reproduction."""
    good_x, good_y = setup_goods
    agent = OrganicAgent(
        position=(5, 5),
        consumes=good_x,
        produces=good_y,
        reproduction_threshold=10.0
    )
    
    # Not enough resources
    agent.resources_accumulated = 5.0
    assert not agent.can_reproduce()
    child = agent.reproduce((10, 10))
    assert child is None
    
    # Enough resources
    agent.resources_accumulated = 15.0
    assert agent.can_reproduce()
    child = agent.reproduce((10, 10))
    assert child is not None
    assert isinstance(child, OrganicAgent)
    
    # Check inheritance (should be same or mutated)
    # Child's consumes should either be inherited or mutated to another registered good
    all_good_ids = set(Good.get_all_good_types().keys())
    assert child.consumes.good_type_id in all_good_ids


def test_organic_agent_create_inorganic(setup_goods):
    """Test organic agent creating inorganic agent."""
    good_x, good_y = setup_goods
    agent = OrganicAgent(
        position=(5, 5),
        consumes=good_x,
        produces=good_y
    )
    
    inorganic = agent.create_inorganic_agent((10, 10))
    assert inorganic is not None
    assert isinstance(inorganic, InorganicAgent)
    assert inorganic.alive is True


def test_inorganic_agent_no_death(setup_goods):
    """Test that inorganic agents don't die from lack of resources."""
    good_x, good_y = setup_goods
    agent = InorganicAgent(
        position=(0, 0),
        consumes=good_x,
        produces=good_y
    )
    
    # Convert without resources - should just return empty
    consumed, produced = agent.convert({})
    assert consumed == {}
    assert produced == {}
    
    # Agent should still be alive
    assert agent.alive is True
