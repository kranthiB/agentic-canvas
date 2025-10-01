"""
Demo 2: GridMind AI Models
T4 Multi-Agent Generative System for Khavda renewable energy plant
"""
from datetime import datetime
from sqlalchemy import Enum as SQLEnum
import enum
from app import db
from app.core.database import BaseModel, TimestampMixin


class AgentType(enum.Enum):
    """Agent type enumeration"""
    WEATHER = "weather"
    DEMAND = "demand"
    STORAGE = "storage"
    TRADING = "trading"
    MAINTENANCE = "maintenance"


class AgentStatus(enum.Enum):
    """Agent status enumeration"""
    ACTIVE = "active"
    IDLE = "idle"
    ERROR = "error"
    LEARNING = "learning"


class PlantStatus(enum.Enum):
    """Plant operational status"""
    OPTIMAL = "optimal"
    NORMAL = "normal"
    SUBOPTIMAL = "suboptimal"
    CRITICAL = "critical"


class PlantState(BaseModel, TimestampMixin):
    """Real-time plant operational state"""
    __tablename__ = 'plant_states'
    
    # Generation
    solar_generation_mw = db.Column(db.Float, nullable=False)
    wind_generation_mw = db.Column(db.Float, nullable=False)
    total_generation_mw = db.Column(db.Float, nullable=False)
    
    # Storage
    battery_soc = db.Column(db.Float, nullable=False)  # State of charge (0-1)
    battery_power_mw = db.Column(db.Float, default=0.0)  # Positive=charging, negative=discharging
    
    # Grid
    grid_frequency_hz = db.Column(db.Float, default=50.0)
    grid_demand_mw = db.Column(db.Float)
    
    # Market
    market_price_inr_mwh = db.Column(db.Float)
    
    # Weather
    solar_irradiance = db.Column(db.Float)  # W/m²
    wind_speed_ms = db.Column(db.Float)  # m/s
    temperature_c = db.Column(db.Float)
    
    # Status
    status = db.Column(SQLEnum(PlantStatus), default=PlantStatus.NORMAL)
    
    # Performance
    capacity_factor = db.Column(db.Float)  # Percentage
    revenue_inr = db.Column(db.Float)

    @property
    def current_generation_mw(self):
        """Alias for total_generation_mw"""
        return self.total_generation_mw if self.total_generation_mw else 0.0

    @property
    def battery_soc_percent(self):
        """Battery state of charge as percentage"""
        return (self.battery_soc * 100) if self.battery_soc else 0.0

    @property
    def capacity_factor_percent(self):
        """Capacity factor as percentage (already in percentage)"""
        return self.capacity_factor if self.capacity_factor else 0.0

    @property
    def curtailment_percent(self):
        """Calculate curtailment percentage"""
        # Curtailment = unused generation capacity
        # Max capacity is 30,000 MW (30 GW plant)
        max_capacity = 30000.0
        if self.total_generation_mw and max_capacity > 0:
            return ((max_capacity - self.total_generation_mw) / max_capacity) * 100
        return 0.0

    @property
    def market_price_per_mwh(self):
        """Alias for market_price_inr_mwh"""
        return self.market_price_inr_mwh if self.market_price_inr_mwh else 0.0
    
    def __repr__(self):
        return f''
    
    def to_dict(self):
        return {
            'id': self.id,
            'solar_generation_mw': round(self.solar_generation_mw, 1),
            'wind_generation_mw': round(self.wind_generation_mw, 1),
            'total_generation_mw': round(self.total_generation_mw, 1),
            'battery_soc': round(self.battery_soc, 3),
            'battery_power_mw': round(self.battery_power_mw, 1),
            'grid_frequency_hz': round(self.grid_frequency_hz, 2),
            'grid_demand_mw': round(self.grid_demand_mw, 1) if self.grid_demand_mw else None,
            'market_price_inr_mwh': round(self.market_price_inr_mwh, 2) if self.market_price_inr_mwh else None,
            'status': self.status.value,
            'capacity_factor': round(self.capacity_factor, 2) if self.capacity_factor else None,
            'timestamp': self.created_at.isoformat()
        }


class AgentDecision(BaseModel, TimestampMixin):
    """Decisions made by individual agents"""
    __tablename__ = 'agent_decisions'
    
    # Agent info
    agent_id = db.Column(db.String(100), nullable=False, index=True)
    agent_type = db.Column(SQLEnum(AgentType), nullable=False)
    
    # Decision
    decision_type = db.Column(db.String(100), nullable=False)
    decision_data = db.Column(db.JSON, nullable=False)
    
    # Reasoning
    reasoning = db.Column(db.Text)
    confidence_score = db.Column(db.Float)  # 0-1
    
    # Context
    plant_state_id = db.Column(db.Integer, db.ForeignKey('plant_states.id'))
    
    # Execution
    executed = db.Column(db.Boolean, default=False)
    execution_result = db.Column(db.JSON)
    
    def __repr__(self):
        return f''
    
    def to_dict(self):
        return {
            'id': self.id,
            'agent_id': self.agent_id,
            'agent_type': self.agent_type.value,
            'decision_type': self.decision_type,
            'decision_data': self.decision_data,
            'reasoning': self.reasoning,
            'confidence_score': self.confidence_score,
            'executed': self.executed,
            'timestamp': self.created_at.isoformat()
        }


class AgentCommunication(BaseModel, TimestampMixin):
    """Inter-agent communication log"""
    __tablename__ = 'agent_communications'
    
    # Agents
    sender_agent_id = db.Column(db.String(100), nullable=False)
    receiver_agent_id = db.Column(db.String(100), nullable=False)
    
    # Message
    message_type = db.Column(db.String(50), nullable=False)
    message_content = db.Column(db.JSON, nullable=False)
    
    # Protocol
    protocol = db.Column(db.String(50), default='direct')  # direct, broadcast, consensus
    priority = db.Column(db.Integer, default=3)
    
    # Status
    delivered = db.Column(db.Boolean, default=True)
    acknowledged = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f' {self.receiver_agent_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'sender': self.sender_agent_id,
            'receiver': self.receiver_agent_id,
            'message_type': self.message_type,
            'message_content': self.message_content,
            'protocol': self.protocol,
            'timestamp': self.created_at.isoformat()
        }


class ConsensusRound(BaseModel, TimestampMixin):
    """Multi-agent consensus protocol rounds"""
    __tablename__ = 'consensus_rounds'
    
    # Round info
    round_number = db.Column(db.Integer, nullable=False)
    decision_topic = db.Column(db.String(200), nullable=False)
    
    # Proposals
    proposals = db.Column(db.JSON, nullable=False)  # List of agent proposals
    
    # Consensus
    consensus_reached = db.Column(db.Boolean, default=False)
    final_decision = db.Column(db.JSON)
    
    # Voting
    votes = db.Column(db.JSON)  # Agent votes
    convergence_time_ms = db.Column(db.Integer)
    
    def __repr__(self):
        return f''
    
    def to_dict(self):
        return {
            'id': self.id,
            'round_number': self.round_number,
            'decision_topic': self.decision_topic,
            'proposals': self.proposals,
            'consensus_reached': self.consensus_reached,
            'final_decision': self.final_decision,
            'convergence_time_ms': self.convergence_time_ms,
            'timestamp': self.created_at.isoformat()
        }


class MaintenanceSchedule(BaseModel, TimestampMixin):
    """Predictive maintenance schedule"""
    __tablename__ = 'maintenance_schedules'
    
    # Asset
    asset_type = db.Column(db.String(50), nullable=False)  # solar, wind, battery
    asset_id = db.Column(db.String(100), nullable=False)
    
    # Health
    health_score = db.Column(db.Float, nullable=False)  # 0-1
    predicted_failure_date = db.Column(db.DateTime)
    
    # Maintenance
    maintenance_type = db.Column(db.String(100), nullable=False)
    scheduled_date = db.Column(db.DateTime, nullable=False)
    estimated_duration_hours = db.Column(db.Float)
    estimated_cost_inr = db.Column(db.Float)
    
    # Status
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    actual_cost_inr = db.Column(db.Float)
    
    def __repr__(self):
        return f'<Maintenance {self.asset_type}/{self.asset_id} on {self.scheduled_date}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'asset_type': self.asset_type,
            'asset_id': self.asset_id,
            'health_score': round(self.health_score, 3),
            'maintenance_type': self.maintenance_type,
            'scheduled_date': self.scheduled_date.isoformat(),
            'estimated_duration_hours': self.estimated_duration_hours,
            'estimated_cost_inr': self.estimated_cost_inr,
            'completed': self.completed,
            'created_at': self.created_at.isoformat()
        }