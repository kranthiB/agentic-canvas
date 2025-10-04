"""
Event Simulator - Tracks event flow through the EV charging network system
"""
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Event types for EV charging network operations"""
    # User interactions
    USER_QUERY = "user_query"
    EXPANSION_REQUEST = "expansion_request"
    OPTIMIZATION_REQUEST = "optimization_request"
    
    # Gateway routing
    QUERY_ROUTING = "query_routing"
    REQUEST_VALIDATION = "request_validation"
    
    # Agent invocations
    AGENT_INVOCATION = "agent_invocation"
    AGENT_ANALYSIS_START = "agent_analysis_start"
    AGENT_ANALYSIS_COMPLETE = "agent_analysis_complete"
    AGENT_RECOMMENDATION_READY = "agent_recommendation_ready"
    
    # Geographic intelligence
    SITE_ANALYSIS_START = "site_analysis_start"
    LOCATION_SCORING = "location_scoring"
    TRAFFIC_ANALYSIS = "traffic_analysis"
    DEMOGRAPHIC_ANALYSIS = "demographic_analysis"
    
    # External system calls
    VAHAN_API_QUERY = "vahan_api_query"
    VAHAN_API_RESPONSE = "vahan_api_response"
    CENSUS_DB_QUERY = "census_db_query"
    CENSUS_DB_RESPONSE = "census_db_response"
    MUNICIPAL_PORTAL_QUERY = "municipal_portal_query"
    MUNICIPAL_PORTAL_RESPONSE = "municipal_portal_response"
    GRID_CAPACITY_CHECK = "grid_capacity_check"
    GRID_CAPACITY_RESPONSE = "grid_capacity_response"
    
    # Financial analysis
    FINANCIAL_ANALYSIS_START = "financial_analysis_start"
    CAPEX_CALCULATION = "capex_calculation"
    ROI_PROJECTION = "roi_projection"
    NPV_CALCULATION = "npv_calculation"
    FINANCIAL_REPORT_READY = "financial_report_ready"
    
    # Permit management
    PERMIT_CHECK_START = "permit_check_start"
    PERMIT_REQUIREMENTS_QUERY = "permit_requirements_query"
    PERMIT_STATUS_CHECK = "permit_status_check"
    PERMIT_TIMELINE_ESTIMATE = "permit_timeline_estimate"
    PERMIT_REPORT_READY = "permit_report_ready"
    
    # Market intelligence
    MARKET_ANALYSIS_START = "market_analysis_start"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    DEMAND_FORECAST = "demand_forecast"
    MARKET_REPORT_READY = "market_report_ready"
    
    # Network optimization
    NETWORK_OPTIMIZATION_START = "network_optimization_start"
    SITE_SELECTION = "site_selection"
    COVERAGE_OPTIMIZATION = "coverage_optimization"
    BUDGET_ALLOCATION = "budget_allocation"
    NETWORK_PLAN_READY = "network_plan_ready"
    
    # Response delivery
    RESPONSE_AGGREGATION = "response_aggregation"
    RESPONSE_DELIVERY = "response_delivery"
    
    # Crisis management
    CRISIS_ALERT = "crisis_alert"
    CRISIS_ASSESSMENT = "crisis_assessment"
    CRISIS_RESOLUTION = "crisis_resolution"
    
    # System events
    SYSTEM_ERROR = "system_error"
    SYSTEM_WARNING = "system_warning"


class SystemEvent:
    """Represents a system event in the EV charging network"""
    
    def __init__(
        self,
        event_type: EventType,
        source_system: str,
        target_system: Optional[str] = None,
        correlation_id: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        processing_time_ms: Optional[int] = None
    ):
        self.event_type = event_type
        self.source_system = source_system
        self.target_system = target_system
        self.correlation_id = correlation_id
        self.payload = payload or {}
        self.processing_time_ms = processing_time_ms
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            'event_type': self.event_type.value,
            'source_system': self.source_system,
            'target_system': self.target_system,
            'correlation_id': self.correlation_id,
            'payload': self.payload,
            'processing_time_ms': self.processing_time_ms,
            'timestamp': self.timestamp.isoformat()
        }


class EventSimulator:
    """Simulates and tracks events in the EV charging network system"""
    
    def __init__(self):
        self.events: List[SystemEvent] = []
        self.active_correlations: Dict[str, List[SystemEvent]] = {}
        self.event_listeners: List[callable] = []
    
    def emit_event(self, event: SystemEvent):
        """Emit an event and track it"""
        self.events.append(event)
        
        # Track by correlation ID
        if event.correlation_id:
            if event.correlation_id not in self.active_correlations:
                self.active_correlations[event.correlation_id] = []
            self.active_correlations[event.correlation_id].append(event)
        
        # Notify listeners
        for listener in self.event_listeners:
            try:
                listener(event)
            except Exception as e:
                logger.error(f"Error notifying listener: {e}")
        
        logger.info(
            f"Event: {event.event_type.value} | "
            f"{event.source_system} → {event.target_system} | "
            f"Correlation: {event.correlation_id}"
        )
    
    def add_listener(self, listener: callable):
        """Add an event listener"""
        self.event_listeners.append(listener)
    
    def get_events_by_correlation(self, correlation_id: str) -> List[SystemEvent]:
        """Get all events for a correlation ID"""
        return self.active_correlations.get(correlation_id, [])
    
    def get_recent_events(self, limit: int = 50) -> List[SystemEvent]:
        """Get recent events"""
        return self.events[-limit:]
    
    def clear_events(self):
        """Clear all events"""
        self.events.clear()
        self.active_correlations.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get event statistics"""
        return {
            'total_events': len(self.events),
            'active_correlations': len(self.active_correlations),
            'event_types': len(set(e.event_type for e in self.events)),
            'systems_involved': len(set(
                [e.source_system for e in self.events] + 
                [e.target_system for e in self.events if e.target_system]
            ))
        }


# Global event simulator instance
event_simulator = EventSimulator()
