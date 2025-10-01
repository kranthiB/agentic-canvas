"""
Demo 1: Carbon Compass Models
T3 Cognitive Autonomous Agent for emissions management
"""
from datetime import datetime
from sqlalchemy import Enum as SQLEnum
import enum
from app import db
from app.core.database import BaseModel, TimestampMixin


class EmissionStatus(enum.Enum):
    """Emission status enumeration"""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    OPTIMIZED = "optimized"


class ActionType(enum.Enum):
    """Carbon action type enumeration"""
    REDUCE_RATE = "reduce_rate"
    OPTIMIZE_PROCESS = "optimize_process"
    SWITCH_FUEL = "switch_fuel"
    SCHEDULE_MAINTENANCE = "schedule_maintenance"
    NO_ACTION = "no_action"


class CarbonBudget(BaseModel, TimestampMixin):
    """Annual carbon budget tracking"""
    __tablename__ = 'carbon_budgets'
    
    year = db.Column(db.Integer, nullable=False, unique=True, index=True)
    total_budget_mt = db.Column(db.Float, nullable=False)  # Mt CO2e
    consumed_mt = db.Column(db.Float, default=0.0)
    remaining_mt = db.Column(db.Float)
    status = db.Column(SQLEnum(EmissionStatus), default=EmissionStatus.NORMAL)
    
    # Relationships
    readings = db.relationship('EmissionReading', backref='budget', lazy='dynamic')
    actions = db.relationship('CarbonAction', backref='budget', lazy='dynamic')
    
    def __repr__(self):
        return f'<CarbonBudget {self.year}: {self.consumed_mt}/{self.total_budget_mt} Mt>'
    
    def update_consumption(self, amount_mt):
        """Update consumed amount"""
        self.consumed_mt += amount_mt
        self.remaining_mt = self.total_budget_mt - self.consumed_mt
        
        # Update status
        consumption_pct = (self.consumed_mt / self.total_budget_mt) * 100
        if consumption_pct >= 95:
            self.status = EmissionStatus.CRITICAL
        elif consumption_pct >= 80:
            self.status = EmissionStatus.WARNING
        else:
            self.status = EmissionStatus.NORMAL
        
        db.session.commit()

    @property
    def consumed_percentage(self):
        """Calculate consumed percentage"""
        if self.total_budget_mt == 0:
            return 0.0
        return (self.consumed_mt / self.total_budget_mt) * 100
    
    @property
    def remaining_percentage(self):
        """Calculate remaining percentage"""
        return 100.0 - self.consumed_percentage
    
    def to_dict(self):
        return {
            'id': self.id,
            'year': self.year,
            'total_budget_mt': self.total_budget_mt,
            'consumed_mt': round(self.consumed_mt, 2),
            'remaining_mt': round(self.remaining_mt, 2),
            'consumption_percentage': round((self.consumed_mt / self.total_budget_mt) * 100, 2),
            'status': self.status.value,
            'created_at': self.created_at.isoformat()
        }


class EmissionReading(BaseModel, TimestampMixin):
    """Real-time emission readings"""
    __tablename__ = 'emission_readings'
    
    budget_id = db.Column(db.Integer, db.ForeignKey('carbon_budgets.id'), nullable=False)
    
    # Measurements
    emissions_rate_kg_hr = db.Column(db.Float, nullable=False)
    production_rate = db.Column(db.Float)  # barrels/hr or units/hr
    intensity = db.Column(db.Float)  # kg CO2e per unit
    
    # Operational context
    facility = db.Column(db.String(100))
    unit = db.Column(db.String(100))
    
    # Status
    is_anomaly = db.Column(db.Boolean, default=False)
    status = db.Column(SQLEnum(EmissionStatus), default=EmissionStatus.NORMAL)
    
    def __repr__(self):
        return f'<EmissionReading {self.emissions_rate_kg_hr} kg/hr at {self.created_at}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'emissions_rate_kg_hr': round(self.emissions_rate_kg_hr, 2),
            'production_rate': round(self.production_rate, 2) if self.production_rate else None,
            'intensity': round(self.intensity, 4) if self.intensity else None,
            'facility': self.facility,
            'unit': self.unit,
            'is_anomaly': self.is_anomaly,
            'status': self.status.value,
            'timestamp': self.created_at.isoformat()
        }


class CarbonAction(BaseModel, TimestampMixin):
    """AI-recommended carbon reduction actions"""
    __tablename__ = 'carbon_actions'
    
    budget_id = db.Column(db.Integer, db.ForeignKey('carbon_budgets.id'), nullable=False)
    
    # Action details
    action_type = db.Column(SQLEnum(ActionType), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Expected impact
    expected_reduction_kg_hr = db.Column(db.Float)
    expected_cost = db.Column(db.Float)
    
    # AI reasoning
    reasoning = db.Column(db.Text)
    confidence_score = db.Column(db.Float)  # 0-1
    agent_id = db.Column(db.String(100))
    
    # Execution
    implemented = db.Column(db.Boolean, default=False)
    implemented_at = db.Column(db.DateTime)
    actual_reduction_kg_hr = db.Column(db.Float)
    
    # Priority
    priority = db.Column(db.Integer, default=3)  # 1=high, 5=low
    
    def __repr__(self):
        return f'<CarbonAction {self.action_type.value}: {self.expected_reduction_kg_hr} kg/hr>'
    
    def implement(self):
        """Mark action as implemented"""
        self.implemented = True
        self.implemented_at = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'action_type': self.action_type.value,
            'description': self.description,
            'expected_reduction_kg_hr': self.expected_reduction_kg_hr,
            'expected_cost': self.expected_cost,
            'reasoning': self.reasoning,
            'confidence_score': self.confidence_score,
            'implemented': self.implemented,
            'implemented_at': self.implemented_at.isoformat() if self.implemented_at else None,
            'priority': self.priority,
            'created_at': self.created_at.isoformat()
        }


class CounterfactualScenario(BaseModel, TimestampMixin):
    """What-if scenario analysis"""
    __tablename__ = 'counterfactual_scenarios'
    
    budget_id = db.Column(db.Integer, db.ForeignKey('carbon_budgets.id'), nullable=False)
    
    # Scenario definition
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Parameters
    parameters = db.Column(db.JSON)  # Scenario parameters
    
    # Results
    projected_emissions_mt = db.Column(db.Float)
    projected_savings_mt = db.Column(db.Float)
    projected_cost = db.Column(db.Float)
    
    # Analysis
    feasibility_score = db.Column(db.Float)  # 0-1
    risk_level = db.Column(db.String(20))
    
    def __repr__(self):
        return f''
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'parameters': self.parameters,
            'projected_emissions_mt': self.projected_emissions_mt,
            'projected_savings_mt': self.projected_savings_mt,
            'projected_cost': self.projected_cost,
            'feasibility_score': self.feasibility_score,
            'risk_level': self.risk_level,
            'created_at': self.created_at.isoformat()
        }