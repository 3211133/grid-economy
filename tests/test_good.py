"""Tests for Good class."""

import pytest
from grid_economy.good import Good


def test_good_creation():
    """Test creating a good."""
    Good.reset_goods()
    good = Good("test_good")
    assert good.good_type_id == "test_good"
    assert good.characteristics == {}


def test_good_auto_id():
    """Test automatic ID generation."""
    Good.reset_goods()
    good1 = Good()
    good2 = Good()
    assert good1.good_type_id == "good_0"
    assert good2.good_type_id == "good_1"


def test_good_characteristics():
    """Test adding characteristics to goods."""
    Good.reset_goods()
    characteristics = {"color": "red", "weight": 1.5}
    good = Good("apple", characteristics)
    assert good.characteristics["color"] == "red"
    assert good.characteristics["weight"] == 1.5


def test_good_equality():
    """Test good equality."""
    Good.reset_goods()
    good1 = Good("test")
    good2 = Good("test")
    good3 = Good("other")
    
    # Same type_id means same good
    assert good1 == good2
    assert good1 != good3


def test_good_registry():
    """Test good type registry."""
    Good.reset_goods()
    good1 = Good("apple")
    good2 = Good("banana")
    
    all_goods = Good.get_all_good_types()
    assert len(all_goods) == 2
    assert "apple" in all_goods
    assert "banana" in all_goods
    
    retrieved = Good.get_good_type("apple")
    assert retrieved == good1
