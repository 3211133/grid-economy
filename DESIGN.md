# Grid Economy - Design Document

## Overview

This document describes the design decisions and implementation details of the grid-economy simulation system.

## Requirements (from Problem Statement)

The system simulates a 2D grid-based world with the following characteristics:

### Agents
1. **Organic Agents (有機エージェント)**:
   - Consume nearby good X and produce good Y
   - Die without sufficient good X
   - Reproduce when they have sufficient good X
   - Inherit parent traits with probabilistic mutations
   - Can create inorganic agents for survival advantage

2. **Inorganic Agents (無機エージェント)**:
   - Consume nearby good X and produce good Y
   - Stop converting without good X but don't die
   - Don't reproduce
   - Have random conversion mechanisms regardless of parent traits

### Goods (財)
- Multiple types exist
- New goods can emerge probabilistically when new agents are created
- Characteristics can be added to goods (extensible design)

## Architecture

### Class Hierarchy

```
Good
  - Represents a type of good with unique ID and characteristics

Agent (base class)
  - Base functionality for conversion mechanics
  ├── OrganicAgent
  │     - Reproduction with inheritance and mutation
  │     - Death from starvation
  │     - Can create inorganic agents
  └── InorganicAgent
        - Persistent (no death)
        - No reproduction
```

### Key Design Decisions

#### 1. Resource Accumulation Model

**Decision**: Organic agents accumulate resources from all goods they produce.

**Rationale**: 
- Represents the agent's benefit from successful conversion
- Simple and intuitive model
- Works well with single-good production (typical case)

**Trade-off**: For multi-good production scenarios, this may accumulate resources faster than intended. Could be made configurable in future versions.

#### 2. Starvation Check Frequency

**Decision**: Check starvation on every step by calling `update({}, {})` even when no conversion occurs.

**Rationale**:
- Ensures consistent death mechanics
- Prevents agents from surviving indefinitely without resources
- Simple and predictable behavior

**Trade-off**: Slightly less efficient for large simulations. Could be optimized by checking resources_accumulated threshold before calling update().

#### 3. Good Type Registry

**Decision**: Global registry of all good types in the Good class.

**Rationale**:
- Easy to track all good types
- Convenient for mutation mechanics (selecting existing goods)
- Simple cleanup for testing

**Trade-off**: Not thread-safe. For multi-world simulations, would need per-world registries.

#### 4. Grid Cell Storage

**Decision**: Store goods as dictionaries per cell: `grid[x][y][good_type] = amount`.

**Rationale**:
- Efficient for sparse distributions
- Easy to add/remove good types
- Natural Python data structure

**Alternative considered**: Array-based storage would be faster but less flexible for dynamic good types.

#### 5. Configurable Probabilities

**Decision**: Make reproduction and inorganic creation probabilities configurable World parameters.

**Rationale**:
- Allows experimentation with different simulation dynamics
- Avoids magic numbers in code
- Easy to tune for different scenarios

**Default values**: 
- `organic_reproduction_chance = 0.3` (30%)
- `inorganic_creation_chance = 0.05` (5%)

#### 6. Mutation Rate

**Decision**: Mutation rate is a property of OrganicAgent, default 0.1 (10%).

**Rationale**:
- Agents can evolve different mutation rates
- Heritable trait that can affect evolution
- Reasonable default for interesting dynamics

#### 7. Search Radius

**Decision**: Each agent has a configurable search_radius for finding nearby goods.

**Rationale**:
- Adds spatial dynamics to the simulation
- Different agent types can have different ranges
- Can be mutated for evolutionary advantage

## Implementation Details

### World.step() Flow

1. Iterate through all agents
2. For each agent:
   a. Check if alive (skip if dead)
   b. Get goods within search radius
   c. Attempt conversion if possible
   d. Update organic agent state
   e. Check for death
   f. Check for reproduction (organic agents)
   g. Check for inorganic agent creation (organic agents)
3. Remove dead agents
4. Add new agents

### Good Creation

- Automatic ID generation: `good_0`, `good_1`, etc.
- Custom IDs supported: `Good("custom_name")`
- Characteristics stored as dictionary (extensible)

### Reproduction and Mutation

**Inheritance**:
- Child inherits parent's consumption/production goods
- Child inherits rates (with mutation)
- Child inherits search_radius, thresholds, mutation_rate

**Mutation mechanisms**:
1. Consumption good change (select from existing goods)
2. Production good change (create new or select existing)
3. Rate adjustment (multiply by 0.8-1.2)

**Mutation probability**: Checked per trait during reproduction.

### Inorganic Agent Creation

When an organic agent creates an inorganic agent:
- Consumption good: random from existing goods
- Production good: probabilistically new or existing
- Rates: random (0.5-2.0)
- Search radius: random (1-3)
- Position: random nearby cell

This implements the requirement that inorganic agents have random conversion mechanisms.

## Testing Strategy

### Test Coverage

1. **Good tests** (5 tests): Creation, IDs, characteristics, equality, registry
2. **Agent tests** (7 tests): Creation, conversion, starvation, reproduction, mutation, inorganic creation
3. **World tests** (10 tests): Creation, agent management, good distribution, conversion, death, statistics

### Testing Philosophy

- Test each component in isolation
- Test integration through World.step()
- Use fixtures for common setup
- Test both success and failure cases
- Verify side effects (death, reproduction)

## Performance Considerations

### Current Implementation

- Time complexity per step: O(A × R²) where A = agents, R = search radius
- Space complexity: O(W × H × G) where W,H = world size, G = good types per cell

### Optimization Opportunities (Future)

1. Spatial indexing for agent/good lookups
2. Lazy starvation checking
3. Event-driven updates instead of full grid scan
4. Parallel agent processing
5. Agent pooling/recycling

## Future Enhancements

### Potential Features

1. **Agent Communication**: Agents could share information about good locations
2. **Trade Mechanisms**: Agents could exchange goods
3. **Territory/Ownership**: Agents could claim cells
4. **Social Structures**: Groups of agents with shared goals
5. **Environmental Factors**: Temperature, terrain affecting conversion rates
6. **Visualization**: Real-time display of simulation state
7. **Persistence**: Save/load simulation state
8. **Analytics**: More detailed statistics and metrics

### API Extensions

1. Custom agent types (plugin system)
2. Custom mutation strategies
3. Event hooks (on_birth, on_death, on_convert)
4. Multiple worlds in parallel
5. Agent memory/learning capabilities

## Conclusion

The current implementation provides a solid foundation for grid-based economic simulations with evolutionary dynamics. It meets all requirements from the problem statement and is designed to be extensible for future enhancements.
