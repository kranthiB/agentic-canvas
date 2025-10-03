"""
System Simulation Module for Engineer's Copilot Demo
Digital twin of the production architecture for demo purposes.
"""

from .event_simulator import SystemEventSimulator, EventType, SystemEvent, event_simulator
from .message_queue import InMemoryMessageQueue, Message, message_queue
from .mock_systems import (
    MockSAPSystem, MockLIMSSystem, MockPLMSystem, 
    MockRegulatorySystem, MockSupplierSystem,
    mock_sap, mock_lims, mock_plm, mock_regulatory, mock_supplier
)
from .agent_orchestrator import AgentOrchestrator, agent_orchestrator
from .specialized_agents import (
    FormulationAgent, TestProtocolAgent, RegulatoryComplianceAgent,
    SupplyChainAgent, KnowledgeMiningAgent,
    formulation_agent, test_protocol_agent, regulatory_agent,
    supply_chain_agent, knowledge_mining_agent
)

__all__ = [
    'SystemEventSimulator', 'EventType', 'SystemEvent', 'event_simulator',
    'InMemoryMessageQueue', 'Message', 'message_queue',
    'MockSAPSystem', 'MockLIMSSystem', 'MockPLMSystem', 
    'MockRegulatorySystem', 'MockSupplierSystem',
    'mock_sap', 'mock_lims', 'mock_plm', 'mock_regulatory', 'mock_supplier',
    'AgentOrchestrator', 'agent_orchestrator',
    'FormulationAgent', 'TestProtocolAgent', 'RegulatoryComplianceAgent',
    'SupplyChainAgent', 'KnowledgeMiningAgent',
    'formulation_agent', 'test_protocol_agent', 'regulatory_agent',
    'supply_chain_agent', 'knowledge_mining_agent'
]
