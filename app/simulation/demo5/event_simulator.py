"""
Event Simulator - Digital twin event tracking for demo purposes.
Simulates events flowing through enterprise architecture.
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from uuid import uuid4
import asyncio
import random


class EventType(Enum):
    """
    Types of events that flow through our system. Each event type represents
    a different kind of activity in the enterprise architecture.
    """
    # User-initiated events
    FORMULATION_REQUEST = "formulation_request"
    PROTOCOL_REQUEST = "protocol_request"
    COMPLIANCE_CHECK = "compliance_check"
    
    # System-to-system events
    SAP_MATERIAL_QUERY = "sap_material_query"
    SAP_COST_QUERY = "sap_cost_query"
    SAP_SUPPLIER_QUERY = "sap_supplier_query"
    
    LIMS_TEST_QUERY = "lims_test_query"
    LIMS_RESULT_UPDATE = "lims_result_update"
    
    PLM_SPECIFICATION_QUERY = "plm_specification_query"
    PLM_BOM_UPDATE = "plm_bom_update"
    
    REGULATORY_STANDARD_CHECK = "regulatory_standard_check"
    REGULATORY_PERMIT_STATUS = "regulatory_permit_status"
    
    SUPPLIER_AVAILABILITY_CHECK = "supplier_availability_check"
    SUPPLIER_PRICE_CHECK = "supplier_price_check"
    
    # Agent events
    AGENT_ANALYSIS_START = "agent_analysis_start"
    AGENT_ANALYSIS_COMPLETE = "agent_analysis_complete"
    AGENT_RECOMMENDATION_READY = "agent_recommendation_ready"
    
    # Knowledge Base and RAG events
    RAG_QUERY_INITIATED = "rag_query_initiated"
    VECTOR_SEARCH_STARTED = "vector_search_started"
    KNOWLEDGE_RETRIEVAL = "knowledge_retrieval"
    LLM_INFERENCE_START = "llm_inference_start"
    LLM_INFERENCE_COMPLETE = "llm_inference_complete"
    KNOWLEDGE_SYNTHESIS = "knowledge_synthesis"
    
    # MCP events
    MCP_CONNECTION_ESTABLISHED = "mcp_connection_established"
    MCP_PROTOCOL_HANDSHAKE = "mcp_protocol_handshake"
    MCP_RESOURCE_ACCESS = "mcp_resource_access"
    
    # System status events
    SYSTEM_CONNECTED = "system_connected"
    SYSTEM_DISCONNECTED = "system_disconnected"
    SYSTEM_ERROR = "system_error"


@dataclass
class SystemEvent:
    """
    Represents a single event in our system. Events are the fundamental unit
    of communication in event-driven architectures.
    
    Each event carries information about what happened, when it happened, where
    it came from, and any relevant data payload.
    """
    event_id: str = field(default_factory=lambda: str(uuid4()))
    event_type: EventType = None
    timestamp: datetime = field(default_factory=datetime.now)
    source_system: str = ""  # e.g., "SAP_ERP", "LIMS", "FormulationAgent"
    target_system: Optional[str] = None  # e.g., "Orchestrator", "UI"
    correlation_id: Optional[str] = None  # Links related events together
    parent_event_id: Optional[str] = None  # For tracing event chains
    
    # The actual data carried by this event
    payload: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata for tracking and debugging
    status: str = "pending"  # pending, processing, completed, failed
    processing_time_ms: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for JSON serialization"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value if self.event_type else None,
            'timestamp': self.timestamp.isoformat(),
            'source_system': self.source_system,
            'target_system': self.target_system,
            'correlation_id': self.correlation_id,
            'parent_event_id': self.parent_event_id,
            'payload': self.payload,
            'status': self.status,
            'processing_time_ms': self.processing_time_ms
        }


class SystemEventSimulator:
    """
    The Event Simulator is like a conductor orchestrating a symphony. It generates
    events, manages their flow, and coordinates the timing so everything feels natural.
    
    In a real system, events come from actual enterprise applications. Here, we simulate
    those events with realistic timing and behavior. The key is making it feel authentic -
    if SAP typically takes 500ms to respond, our simulation does too.
    """
    
    def __init__(self):
        # Store all events for replay and analysis
        self.event_history: List[SystemEvent] = []
        
        # Active event listeners - these get notified when events occur
        self.listeners: Dict[EventType, List[Callable]] = {}
        
        # Track active requests for correlation
        self.active_requests: Dict[str, Dict[str, Any]] = {}
        
        # System health and status
        self.system_status: Dict[str, str] = {
            'SAP_ERP': 'online',
            'LIMS': 'online',
            'PLM': 'online',
            'Regulatory_DB': 'online',
            'Supplier_Portal': 'online'
        }
        
        # Simulate realistic response times (in milliseconds)
        # These are based on typical enterprise system performance
        self.response_times = {
            'SAP_ERP': (300, 800),  # SAP is usually quick but variable
            'LIMS': (500, 1500),    # Lab systems can be slower
            'PLM': (400, 1000),     # PLM is medium speed
            'Regulatory_DB': (200, 600),  # External APIs are fast
            'Supplier_Portal': (1000, 2000)  # External systems are slowest
        }
    
    def register_listener(self, event_type: EventType, callback: Callable):
        """
        Register a callback function to be notified when a specific event occurs.
        This is the publish-subscribe pattern in action.
        """
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)
    
    def emit_event(self, event: SystemEvent) -> str:
        """
        Emit an event into the system. This triggers any registered listeners
        and adds the event to the history for tracking.
        
        Returns the event ID for correlation
        """
        # Add to history
        self.event_history.append(event)
        
        # Notify all registered listeners
        if event.event_type in self.listeners:
            for callback in self.listeners[event.event_type]:
                try:
                    # Call the listener function with the event
                    callback(event)
                except Exception as e:
                    print(f"Error in event listener: {e}")
        
        return event.event_id
    
    async def simulate_system_response(
        self, 
        system_name: str, 
        request_event: SystemEvent
    ) -> SystemEvent:
        """
        Simulate a system processing a request and returning a response.
        This adds realistic delays to make the simulation feel authentic.
        
        Think of this as the "acting" in our digital theater - we're creating
        the illusion of systems working by introducing appropriate delays.
        """
        # Simulate processing time based on system characteristics
        min_time, max_time = self.response_times.get(system_name, (100, 500))
        processing_time = random.randint(min_time, max_time)
        
        # Actually wait (in demo mode, we scale this down for faster demo)
        await asyncio.sleep(processing_time / 1000.0 * 0.1)  # 10x faster for demo
        
        # Create response event
        response = SystemEvent(
            event_type=request_event.event_type,
            source_system=system_name,
            target_system=request_event.source_system,
            correlation_id=request_event.correlation_id,
            parent_event_id=request_event.event_id,
            status='completed',
            processing_time_ms=processing_time
        )
        
        return response
    
    def get_event_chain(self, correlation_id: str) -> List[SystemEvent]:
        """
        Get all events related to a specific request. This is useful for
        visualizing the complete flow of a request through the system.
        """
        return [
            event for event in self.event_history 
            if event.correlation_id == correlation_id
        ]
    
    def get_recent_events(self, limit: int = 50) -> List[SystemEvent]:
        """Get the most recent events for display in the UI"""
        return self.event_history[-limit:]
    
    def clear_history(self):
        """Clear event history (useful for demo resets)"""
        self.event_history.clear()
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """
        Calculate metrics about system performance. This data powers the
        monitoring dashboards in the UI.
        """
        total_events = len(self.event_history)
        
        # Calculate average processing times by system
        processing_times = {}
        for event in self.event_history:
            if event.processing_time_ms:
                system = event.source_system
                if system not in processing_times:
                    processing_times[system] = []
                processing_times[system].append(event.processing_time_ms)
        
        avg_times = {
            system: sum(times) / len(times) 
            for system, times in processing_times.items()
        }
        
        # Count events by type
        event_counts = {}
        for event in self.event_history:
            if event.event_type:
                event_type = event.event_type.value
                event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        return {
            'total_events': total_events,
            'average_processing_times': avg_times,
            'event_type_distribution': event_counts,
            'system_status': self.system_status
        }
    
    async def simulate_formulation_request_flow(
        self, 
        request_data: Dict[str, Any]
    ) -> List[SystemEvent]:
        """
        Simulate the complete flow of a formulation request through the system.
        This is the "grand tour" that shows all systems working together.
        
        A formulation request triggers:
        1. SAP queries for materials and costs
        2. LIMS queries for historical test data
        3. Regulatory checks for compliance
        4. Supplier checks for availability
        5. Agent analysis and recommendations
        
        This method orchestrates all of these in sequence, creating a realistic
        event cascade that demonstrates the system architecture.
        """
        correlation_id = str(uuid4())
        events = []
        
        # Step 1: Initial request event
        initial_event = SystemEvent(
            event_type=EventType.FORMULATION_REQUEST,
            source_system='UI',
            target_system='Orchestrator',
            correlation_id=correlation_id,
            payload=request_data
        )
        events.append(initial_event)
        self.emit_event(initial_event)
        
        # Step 2: Orchestrator starts agent analysis
        agent_start = SystemEvent(
            event_type=EventType.AGENT_ANALYSIS_START,
            source_system='Orchestrator',
            target_system='FormulationAgent',
            correlation_id=correlation_id,
            parent_event_id=initial_event.event_id,
            payload={'analysis_type': 'formulation_optimization'}
        )
        events.append(agent_start)
        self.emit_event(agent_start)
        
        # Step 3: Query SAP for material costs (happens in parallel in reality)
        sap_event = SystemEvent(
            event_type=EventType.SAP_MATERIAL_QUERY,
            source_system='FormulationAgent',
            target_system='SAP_ERP',
            correlation_id=correlation_id,
            parent_event_id=agent_start.event_id,
            payload={'query_type': 'base_oils_and_additives'}
        )
        events.append(sap_event)
        self.emit_event(sap_event)
        
        # Simulate SAP response
        sap_response = await self.simulate_system_response('SAP_ERP', sap_event)
        sap_response.payload = {
            'materials_found': 15,
            'base_oils': ['Group II', 'Group III', 'PAO'],
            'estimated_cost_per_liter': 85.5
        }
        events.append(sap_response)
        self.emit_event(sap_response)
        
        # Step 4: Initialize RAG query for knowledge retrieval
        rag_query = SystemEvent(
            event_type=EventType.RAG_QUERY_INITIATED,
            source_system='FormulationAgent',
            target_system='RAG_Engine',
            correlation_id=correlation_id,
            parent_event_id=agent_start.event_id,
            payload={'query': 'similar_formulations_5W30', 'context': 'formulation_optimization'}
        )
        events.append(rag_query)
        self.emit_event(rag_query)
        
        # Step 4.1: Vector search in knowledge base
        vector_search = SystemEvent(
            event_type=EventType.VECTOR_SEARCH_STARTED,
            source_system='RAG_Engine',
            target_system='Vector_DB',
            correlation_id=correlation_id,
            parent_event_id=rag_query.event_id,
            payload={'embedding_model': 'text-embedding-ada-002', 'top_k': 10}
        )
        events.append(vector_search)
        self.emit_event(vector_search)
        
        # Step 4.2: Knowledge retrieval from knowledge base
        knowledge_retrieval = SystemEvent(
            event_type=EventType.KNOWLEDGE_RETRIEVAL,
            source_system='Vector_DB',
            target_system='Knowledge_Base',
            correlation_id=correlation_id,
            parent_event_id=vector_search.event_id,
            payload={'documents_found': 15, 'relevance_threshold': 0.8}
        )
        events.append(knowledge_retrieval)
        self.emit_event(knowledge_retrieval)
        
        # Step 4.3: LLM inference for knowledge synthesis
        llm_inference = SystemEvent(
            event_type=EventType.LLM_INFERENCE_START,
            source_system='Knowledge_Base',
            target_system='LLM_Models',
            correlation_id=correlation_id,
            parent_event_id=knowledge_retrieval.event_id,
            payload={'model': 'gpt-4o', 'task': 'knowledge_synthesis'}
        )
        events.append(llm_inference)
        self.emit_event(llm_inference)
        
        # Step 4.4: Query LIMS for historical data (via MCP)
        mcp_connection = SystemEvent(
            event_type=EventType.MCP_CONNECTION_ESTABLISHED,
            source_system='LLM_Models',
            target_system='MCP_Gateway',
            correlation_id=correlation_id,
            parent_event_id=llm_inference.event_id,
            payload={'protocol_version': '1.0', 'target_system': 'LIMS'}
        )
        events.append(mcp_connection)
        self.emit_event(mcp_connection)
        
        lims_event = SystemEvent(
            event_type=EventType.LIMS_TEST_QUERY,
            source_system='MCP_Gateway',
            target_system='LIMS',
            correlation_id=correlation_id,
            parent_event_id=mcp_connection.event_id,
            payload={'query': 'similar_formulations_5W30', 'via_mcp': True}
        )
        events.append(lims_event)
        self.emit_event(lims_event)
        
        # Simulate LIMS response
        lims_response = await self.simulate_system_response('LIMS', lims_event)
        lims_response.payload = {
            'historical_tests_found': 47,
            'avg_viscosity_index': 152,
            'success_rate': 0.82
        }
        events.append(lims_response)
        self.emit_event(lims_response)
        
        # Step 5: Check regulatory compliance
        reg_event = SystemEvent(
            event_type=EventType.REGULATORY_STANDARD_CHECK,
            source_system='RegulatoryAgent',
            target_system='Regulatory_DB',
            correlation_id=correlation_id,
            parent_event_id=agent_start.event_id,
            payload={'standards': ['API SN Plus', 'ACEA C3']}
        )
        events.append(reg_event)
        self.emit_event(reg_event)
        
        # Simulate regulatory response
        reg_response = await self.simulate_system_response('Regulatory_DB', reg_event)
        reg_response.payload = {
            'standards_checked': 2,
            'compliance_status': 'compliant',
            'required_permits': ['BIS certification', 'PESO approval']
        }
        events.append(reg_response)
        self.emit_event(reg_response)
        
        # Step 6: Check supplier availability
        supplier_event = SystemEvent(
            event_type=EventType.SUPPLIER_AVAILABILITY_CHECK,
            source_system='SupplyChainAgent',
            target_system='Supplier_Portal',
            correlation_id=correlation_id,
            parent_event_id=agent_start.event_id,
            payload={'materials': ['PAO4', 'ZDDP', 'Calcium Sulfonate']}
        )
        events.append(supplier_event)
        self.emit_event(supplier_event)
        
        # Simulate supplier response
        supplier_response = await self.simulate_system_response('Supplier_Portal', supplier_event)
        supplier_response.payload = {
            'materials_available': 3,
            'lead_time_days': 7,
            'price_competitive': True
        }
        events.append(supplier_response)
        self.emit_event(supplier_response)
        
        # Step 7: Agent completes analysis
        agent_complete = SystemEvent(
            event_type=EventType.AGENT_ANALYSIS_COMPLETE,
            source_system='FormulationAgent',
            target_system='Orchestrator',
            correlation_id=correlation_id,
            parent_event_id=agent_start.event_id,
            payload={'recommendations_generated': 3}
        )
        events.append(agent_complete)
        self.emit_event(agent_complete)
        
        # Step 8: Final recommendation ready
        recommendation = SystemEvent(
            event_type=EventType.AGENT_RECOMMENDATION_READY,
            source_system='Orchestrator',
            target_system='UI',
            correlation_id=correlation_id,
            parent_event_id=agent_complete.event_id,
            payload={
                'recommendations': 3,
                'total_processing_time_ms': sum(e.processing_time_ms or 0 for e in events)
            }
        )
        events.append(recommendation)
        self.emit_event(recommendation)
        
        return events


# Create a global singleton instance for the application
event_simulator = SystemEventSimulator()
