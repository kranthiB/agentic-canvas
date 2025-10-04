"""
Demo 4: Extended Models for Mobility Maestro
Permits, Events, Real-time Operations, Market Intelligence
"""
from datetime import datetime, date
from sqlalchemy import Enum as SQLEnum
import enum
from app import db
from app.core.database import BaseModel, TimestampMixin


# =====================================================
# 1. Permit Management Models
# =====================================================

class PermitType(enum.Enum):
    """Types of permits required"""
    LAND_USE = "land_use"
    ENVIRONMENTAL = "environmental"
    FIRE_SAFETY = "fire_safety"
    ELECTRICAL = "electrical"
    BUILDING = "building"
    GRID_CONNECTION = "grid_connection"
    EV_LICENSE = "ev_license"
    COMMERCIAL_OPERATION = "commercial_operation"


class PermitStatus(enum.Enum):
    """Permit application status"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    ADDITIONAL_INFO_REQUIRED = "additional_info_required"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class TEPermit(BaseModel, TimestampMixin):
    """Permit applications and tracking"""
    __tablename__ = 'te_permits'
    
    # Site reference
    site_id = db.Column(db.Integer, db.ForeignKey('charging_sites.id'), nullable=False)
    
    # Permit details
    permit_type = db.Column(SQLEnum(PermitType), nullable=False)
    permit_number = db.Column(db.String(100), unique=True, index=True)
    
    # Agency information
    agency_name = db.Column(db.String(200), nullable=False)
    agency_state = db.Column(db.String(100))
    submission_portal = db.Column(db.String(200))
    
    # Status tracking
    status = db.Column(SQLEnum(PermitStatus), default=PermitStatus.DRAFT)
    submitted_date = db.Column(db.Date)
    expected_approval_date = db.Column(db.Date)
    actual_approval_date = db.Column(db.Date)
    
    # Timeline
    processing_days_estimated = db.Column(db.Integer)
    processing_days_actual = db.Column(db.Integer)
    
    # Documents
    documents_submitted = db.Column(db.JSON)  # List of document names
    additional_info_requested = db.Column(db.JSON)
    
    # Financial
    application_fee_inr = db.Column(db.Float)
    processing_fee_inr = db.Column(db.Float)
    
    # Notes
    notes = db.Column(db.Text)
    rejection_reason = db.Column(db.Text)
    
    # Agent tracking
    managed_by_agent = db.Column(db.String(100))
    
    def to_dict(self):
        return {
            'id': self.id,
            'site_id': self.site_id,
            'permit_type': self.permit_type.value,
            'permit_number': self.permit_number,
            'agency_name': self.agency_name,
            'status': self.status.value,
            'submitted_date': self.submitted_date.isoformat() if self.submitted_date else None,
            'expected_approval_date': self.expected_approval_date.isoformat() if self.expected_approval_date else None,
            'processing_days_actual': self.processing_days_actual,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class TEGovernmentAgency(BaseModel, TimestampMixin):
    """Government agencies for permit processing"""
    __tablename__ = 'te_government_agencies'
    
    agency_name = db.Column(db.String(200), nullable=False, unique=True)
    agency_type = db.Column(db.String(100))  # municipal, state, central
    state = db.Column(db.String(100))
    
    # Contact
    portal_url = db.Column(db.String(500))
    contact_email = db.Column(db.String(200))
    contact_phone = db.Column(db.String(50))
    
    # Processing info
    avg_processing_days = db.Column(db.Integer)
    digital_submission = db.Column(db.Boolean, default=False)
    
    # Performance metrics
    approval_rate = db.Column(db.Float)  # Percentage
    avg_response_time_days = db.Column(db.Integer)
    
    def to_dict(self):
        return {
            'id': self.id,
            'agency_name': self.agency_name,
            'agency_type': self.agency_type,
            'state': self.state,
            'portal_url': self.portal_url,
            'avg_processing_days': self.avg_processing_days,
            'digital_submission': self.digital_submission
        }


# =====================================================
# 2. Event Tracking Models (Similar to Demo 5)
# =====================================================

class TEAgentActivity(BaseModel, TimestampMixin):
    """Agent activity for event flow visualization"""
    __tablename__ = 'te_mobility_agent_activity'
    
    correlation_id = db.Column(db.String(100), index=True)
    agent_name = db.Column(db.String(100), nullable=False)
    action_type = db.Column(db.String(100), nullable=False)
    input_params = db.Column(db.JSON)
    output_data = db.Column(db.JSON)
    status = db.Column(db.String(20), default='success')
    latency_ms = db.Column(db.Integer)
    source_system = db.Column(db.String(50))
    target_system = db.Column(db.String(50))
    
    def to_dict(self):
        return {
            'id': self.id,
            'correlation_id': self.correlation_id,
            'agent_name': self.agent_name,
            'action_type': self.action_type,
            'source_system': self.source_system,
            'target_system': self.target_system,
            'latency_ms': self.latency_ms,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class TEEventTrace(BaseModel, TimestampMixin):
    """Event traces for flow visualization"""
    __tablename__ = 'te_mobility_event_traces'
    
    correlation_id = db.Column(db.String(100), nullable=False, index=True)
    event_type = db.Column(db.String(100), nullable=False)
    source_system = db.Column(db.String(100))
    target_system = db.Column(db.String(100))
    payload = db.Column(db.JSON)
    processing_time_ms = db.Column(db.Integer)
    
    def to_dict(self):
        return {
            'id': self.id,
            'correlation_id': self.correlation_id,
            'event_type': self.event_type,
            'source_system': self.source_system,
            'target_system': self.target_system,
            'payload': self.payload,
            'processing_time_ms': self.processing_time_ms,
            'timestamp': self.created_at.isoformat() if self.created_at else None
        }


class TEScenario(BaseModel, TimestampMixin):
    """Pre-defined scenarios for simulation"""
    __tablename__ = 'te_mobility_scenarios'
    
    scenario_name = db.Column(db.String(200), nullable=False)
    scenario_type = db.Column(db.String(100))  # expansion, optimization, crisis, permit
    description = db.Column(db.Text)
    
    # Scenario parameters
    target_city = db.Column(db.String(100))
    target_state = db.Column(db.String(100))
    site_count = db.Column(db.Integer)
    
    # Agent involvement
    agents_involved = db.Column(db.JSON)  # List of agent names
    systems_involved = db.Column(db.JSON)  # External systems
    
    # Flow definition
    event_flow = db.Column(db.JSON)  # Step-by-step event flow
    
    # Expected outcomes
    expected_duration_ms = db.Column(db.Integer)
    expected_recommendations = db.Column(db.Integer)
    
    # Metadata
    difficulty_level = db.Column(db.String(20))  # easy, medium, hard
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'scenario_name': self.scenario_name,
            'scenario_type': self.scenario_type,
            'description': self.description,
            'target_city': self.target_city,
            'site_count': self.site_count,
            'agents_involved': self.agents_involved,
            'systems_involved': self.systems_involved,
            'event_flow': self.event_flow,
            'expected_duration_ms': self.expected_duration_ms
        }


# =====================================================
# 3. Real-time Operations Models
# =====================================================

class TEChargingSession(BaseModel, TimestampMixin):
    """Real-time charging sessions"""
    __tablename__ = 'te_charging_sessions'
    
    site_id = db.Column(db.Integer, db.ForeignKey('charging_sites.id'), nullable=False)
    session_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    
    # Session details
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    duration_minutes = db.Column(db.Integer)
    
    # Charging metrics
    energy_delivered_kwh = db.Column(db.Float)
    peak_power_kw = db.Column(db.Float)
    battery_soc_start = db.Column(db.Float)  # State of Charge
    battery_soc_end = db.Column(db.Float)
    
    # Financial
    price_per_kwh = db.Column(db.Float)
    total_amount_inr = db.Column(db.Float)
    payment_method = db.Column(db.String(50))
    
    # Vehicle
    vehicle_type = db.Column(db.String(100))
    connector_type = db.Column(db.String(50))
    
    def to_dict(self):
        return {
            'session_id': self.session_id,
            'site_id': self.site_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'duration_minutes': self.duration_minutes,
            'energy_delivered_kwh': self.energy_delivered_kwh,
            'total_amount_inr': self.total_amount_inr
        }


class TEStationStatus(BaseModel, TimestampMixin):
    """Real-time station operational status"""
    __tablename__ = 'te_station_status'
    
    site_id = db.Column(db.Integer, db.ForeignKey('charging_sites.id'), nullable=False)
    
    # Operational status
    is_operational = db.Column(db.Boolean, default=True)
    total_chargers = db.Column(db.Integer)
    available_chargers = db.Column(db.Integer)
    in_use_chargers = db.Column(db.Integer)
    faulty_chargers = db.Column(db.Integer, default=0)
    
    # Current metrics
    current_load_kw = db.Column(db.Float)
    max_capacity_kw = db.Column(db.Float)
    utilization_percentage = db.Column(db.Float)
    
    # Grid status
    grid_voltage_v = db.Column(db.Float)
    grid_frequency_hz = db.Column(db.Float)
    grid_connection_status = db.Column(db.String(50))
    
    # Environmental
    temperature_celsius = db.Column(db.Float)
    
    # Last update
    last_heartbeat = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'site_id': self.site_id,
            'is_operational': self.is_operational,
            'available_chargers': self.available_chargers,
            'total_chargers': self.total_chargers,
            'current_load_kw': self.current_load_kw,
            'utilization_percentage': self.utilization_percentage,
            'last_heartbeat': self.last_heartbeat.isoformat() if self.last_heartbeat else None
        }


class TEGridMetrics(BaseModel, TimestampMixin):
    """Grid capacity and metrics"""
    __tablename__ = 'te_grid_metrics'
    
    site_id = db.Column(db.Integer, db.ForeignKey('charging_sites.id'), nullable=False)
    
    # Grid connection
    connection_capacity_kw = db.Column(db.Float)
    transformer_capacity_kva = db.Column(db.Float)
    
    # Usage metrics
    peak_demand_kw = db.Column(db.Float)
    average_demand_kw = db.Column(db.Float)
    power_factor = db.Column(db.Float)
    
    # Cost
    electricity_rate_inr_kwh = db.Column(db.Float)
    demand_charge_inr_kw = db.Column(db.Float)
    
    # Reliability
    uptime_percentage = db.Column(db.Float)
    outage_count = db.Column(db.Integer)
    
    # Date
    metric_date = db.Column(db.Date, nullable=False)
    
    def to_dict(self):
        return {
            'site_id': self.site_id,
            'connection_capacity_kw': self.connection_capacity_kw,
            'peak_demand_kw': self.peak_demand_kw,
            'electricity_rate_inr_kwh': self.electricity_rate_inr_kwh,
            'uptime_percentage': self.uptime_percentage,
            'metric_date': self.metric_date.isoformat() if self.metric_date else None
        }


# =====================================================
# 4. Market Intelligence Models
# =====================================================

class TEMarketTrends(BaseModel, TimestampMixin):
    """Market trends and intelligence"""
    __tablename__ = 'te_market_trends'
    
    # Location
    city = db.Column(db.String(100), nullable=False, index=True)
    state = db.Column(db.String(100))
    
    # EV market data
    total_ev_registrations = db.Column(db.Integer)
    monthly_ev_registrations = db.Column(db.Integer)
    ev_growth_rate = db.Column(db.Float)  # Percentage
    
    # Demographics
    total_vehicles = db.Column(db.Integer)
    ev_penetration_rate = db.Column(db.Float)
    avg_household_income = db.Column(db.Float)
    population = db.Column(db.Integer)
    
    # Infrastructure
    existing_charging_stations = db.Column(db.Integer)
    public_chargers = db.Column(db.Integer)
    private_chargers = db.Column(db.Integer)
    
    # Forecasts
    forecasted_ev_count_1yr = db.Column(db.Integer)
    forecasted_ev_count_3yr = db.Column(db.Integer)
    forecasted_ev_count_5yr = db.Column(db.Integer)
    
    # Data source
    data_source = db.Column(db.String(200))
    data_date = db.Column(db.Date, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'city': self.city,
            'state': self.state,
            'total_ev_registrations': self.total_ev_registrations,
            'ev_growth_rate': self.ev_growth_rate,
            'ev_penetration_rate': self.ev_penetration_rate,
            'existing_charging_stations': self.existing_charging_stations,
            'data_date': self.data_date.isoformat() if self.data_date else None
        }


class TECompetitorAnalysis(BaseModel, TimestampMixin):
    """Competitor charging networks"""
    __tablename__ = 'te_competitor_analysis'
    
    competitor_name = db.Column(db.String(200), nullable=False)
    
    # Presence
    total_stations = db.Column(db.Integer)
    cities_present = db.Column(db.JSON)  # List of cities
    
    # Metrics
    estimated_market_share = db.Column(db.Float)
    pricing_strategy = db.Column(db.String(100))
    avg_price_inr_kwh = db.Column(db.Float)
    
    # Strengths/Weaknesses
    strengths = db.Column(db.JSON)
    weaknesses = db.Column(db.JSON)
    
    # Intelligence
    recent_expansions = db.Column(db.JSON)
    planned_locations = db.Column(db.JSON)
    
    # Analysis date
    analysis_date = db.Column(db.Date, nullable=False)
    analyzed_by_agent = db.Column(db.String(100))
    
    def to_dict(self):
        return {
            'id': self.id,
            'competitor_name': self.competitor_name,
            'total_stations': self.total_stations,
            'cities_present': self.cities_present,
            'avg_price_inr_kwh': self.avg_price_inr_kwh,
            'strengths': self.strengths,
            'weaknesses': self.weaknesses
        }
