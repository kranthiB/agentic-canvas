"""
Simulation Module for Agentic Canvas
Contains demo-specific simulation components.
"""

# Import demo5 simulation components for backward compatibility
from .demo5.event_simulator import (
    SystemEventSimulator, EventType, SystemEvent, event_simulator
)
from .demo5.message_queue import (
    InMemoryMessageQueue, Message, message_queue
)
from .demo5.mock_systems import (
    MockSAPSystem, MockLIMSSystem, MockPLMSystem,
    MockRegulatorySystem, MockSupplierSystem,
    mock_sap, mock_lims, mock_plm, mock_regulatory, mock_supplier
)
from .demo5.agent_orchestrator import AgentOrchestrator, agent_orchestrator
from .demo5.specialized_agents import (
    FormulationAgent, TestProtocolAgent, RegulatoryComplianceAgent,
    SupplyChainAgent, KnowledgeMiningAgent,
    formulation_agent, test_protocol_agent, regulatory_agent,
    supply_chain_agent, knowledge_mining_agent
)

__all__ = [
    # Event Simulator
    'SystemEventSimulator', 'EventType', 'SystemEvent', 'event_simulator',
    # Message Queue
    'InMemoryMessageQueue', 'Message', 'message_queue',
    # Mock Systems
    'MockSAPSystem', 'MockLIMSSystem', 'MockPLMSystem',
    'MockRegulatorySystem', 'MockSupplierSystem',
    'mock_sap', 'mock_lims', 'mock_plm', 'mock_regulatory', 'mock_supplier',
    # Agent Orchestrator
    'AgentOrchestrator', 'agent_orchestrator',
    # Specialized Agents
    'FormulationAgent', 'TestProtocolAgent', 'RegulatoryComplianceAgent',
    'SupplyChainAgent', 'KnowledgeMiningAgent',
    'formulation_agent', 'test_protocol_agent', 'regulatory_agent',
    'supply_chain_agent', 'knowledge_mining_agent'
]
