"""
Demo 3: Safety Guardian Models
T2 Procedural Workflow Agent for refinery safety
"""
from datetime import datetime
from sqlalchemy import Enum as SQLEnum
import enum
from app import db
from app.core.database import BaseModel, TimestampMixin


class PermitType(enum.Enum):
    """Permit-to-work type"""
    HOT_WORK = "hot_work"
    CONFINED_SPACE = "confined_space"
    HEIGHT_WORK = "height_work"
    ELECTRICAL = "electrical"
    LINE_BREAKING = "line_breaking"


class PermitStatus(enum.Enum):
    """Permit status"""
    PENDING = "pending"
    APPROVED = "approved"
    ACTIVE = "active"
    COMPLETED = "completed"
    SUSPENDED = "suspended"
    REJECTED = "rejected"


class RiskLevel(enum.Enum):
    """Risk level"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertLevel(enum.Enum):
    """Gas alert level"""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"


class PermitToWork(BaseModel, TimestampMixin):
    """Permit-to-work records"""
    __tablename__ = 'permits_to_work'
    
    # Permit info
    permit_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    permit_type = db.Column(SQLEnum(PermitType), nullable=False)
    status = db.Column(SQLEnum(PermitStatus), default=PermitStatus.PENDING)
    
    # Work details
    work_description = db.Column(db.Text, nullable=False)
    area = db.Column(db.String(100), nullable=False)
    
    # Location (3D coordinates in refinery)
    coordinates_x = db.Column(db.Float)
    coordinates_y = db.Column(db.Float)
    coordinates_z = db.Column(db.Float)  # Height/level
    
    # Personnel
    worker_name = db.Column(db.String(100), nullable=False)
    worker_id = db.Column(db.String(50))
    supervisor_name = db.Column(db.String(100))
    
    # Timing
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    duration_hours = db.Column(db.Float)
    
    # Risk assessment
    risk_score = db.Column(db.Float)  # 0-100
    risk_level = db.Column(SQLEnum(RiskLevel), default=RiskLevel.MEDIUM)
    hazards_identified = db.Column(db.JSON)
    
    # Safety measures
    safety_measures = db.Column(db.JSON)
    ppe_required = db.Column(db.JSON)
    
    # Completion
    actual_completion_time = db.Column(db.DateTime)
    incidents_reported = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f''
    
    def to_dict(self):
        return {
            'id': self.id,
            'permit_number': self.permit_number,
            'permit_type': self.permit_type.value,
            'status': self.status.value,
            'work_description': self.work_description,
            'area': self.area,
            'coordinates': {
                'x': self.coordinates_x,
                'y': self.coordinates_y,
                'z': self.coordinates_z
            },
            'worker_name': self.worker_name,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'risk_score': self.risk_score,
            'risk_level': self.risk_level.value,
            'created_at': self.created_at.isoformat()
        }


class GasSensorReading(BaseModel, TimestampMixin):
    """Gas detector readings"""
    __tablename__ = 'gas_sensor_readings'
    
    # Sensor info
    sensor_id = db.Column(db.String(50), nullable=False, index=True)
    area = db.Column(db.String(100), nullable=False)
    
    # Location
    coordinates_x = db.Column(db.Float)
    coordinates_y = db.Column(db.Float)
    coordinates_z = db.Column(db.Float)
    
    # Gas readings
    o2_percentage = db.Column(db.Float)  # Oxygen
    lel_percentage = db.Column(db.Float)  # Lower Explosive Limit
    h2s_ppm = db.Column(db.Float)  # Hydrogen Sulfide
    co_ppm = db.Column(db.Float)  # Carbon Monoxide
    
    # Alert status
    alert_level = db.Column(SQLEnum(AlertLevel), default=AlertLevel.NORMAL)
    threshold_exceeded = db.Column(db.Boolean, default=False)
    
    # Alarm
    alarm_triggered = db.Column(db.Boolean, default=False)
    alarm_acknowledged = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f''
    
    def to_dict(self):
        return {
            'id': self.id,
            'sensor_id': self.sensor_id,
            'area': self.area,
            'readings': {
                'O2': self.o2_percentage,
                'LEL': self.lel_percentage,
                'H2S': self.h2s_ppm,
                'CO': self.co_ppm
            },
            'alert_level': self.alert_level.value,
            'threshold_exceeded': self.threshold_exceeded,
            'alarm_triggered': self.alarm_triggered,
            'timestamp': self.created_at.isoformat()
        }


class SafetyConflict(BaseModel, TimestampMixin):
    """Detected permit conflicts and hazards"""
    __tablename__ = 'safety_conflicts'
    
    # Conflict type
    conflict_type = db.Column(db.String(100), nullable=False)  # proximity, temporal, incompatible_activities
    severity = db.Column(SQLEnum(RiskLevel), nullable=False)
    
    # Involved permits
    permit1_id = db.Column(db.Integer, db.ForeignKey('permits_to_work.id'))
    permit2_id = db.Column(db.Integer, db.ForeignKey('permits_to_work.id'))
    
    # Details
    description = db.Column(db.Text, nullable=False)
    recommendation = db.Column(db.Text)
    
    # AI analysis
    detected_by_agent = db.Column(db.String(100))
    confidence_score = db.Column(db.Float)
    
    # Resolution
    resolved = db.Column(db.Boolean, default=False)
    resolution_action = db.Column(db.Text)
    resolved_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f''
    
    def to_dict(self):
        return {
            'id': self.id,
            'conflict_type': self.conflict_type,
            'severity': self.severity.value,
            'description': self.description,
            'recommendation': self.recommendation,
            'confidence_score': self.confidence_score,
            'resolved': self.resolved,
            'created_at': self.created_at.isoformat()
        }


class SafetyIncident(BaseModel, TimestampMixin):
    """Safety incident records"""
    __tablename__ = 'safety_incidents'
    
    # Incident info
    incident_number = db.Column(db.String(50), unique=True, nullable=False)
    incident_type = db.Column(db.String(100), nullable=False)
    severity = db.Column(SQLEnum(RiskLevel), nullable=False)
    
    # Details
    description = db.Column(db.Text, nullable=False)
    area = db.Column(db.String(100), nullable=False)
    
    # Related permit
    permit_id = db.Column(db.Integer, db.ForeignKey('permits_to_work.id'))
    
    # Personnel
    personnel_involved = db.Column(db.JSON)
    injuries = db.Column(db.Integer, default=0)
    fatalities = db.Column(db.Integer, default=0)
    
    # Investigation
    root_cause = db.Column(db.Text)
    corrective_actions = db.Column(db.JSON)
    
    # Status
    investigation_complete = db.Column(db.Boolean, default=False)
    report_filed = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f''
    
    def to_dict(self):
        return {
            'id': self.id,
            'incident_number': self.incident_number,
            'incident_type': self.incident_type,
            'severity': self.severity.value,
            'description': self.description,
            'area': self.area,
            'injuries': self.injuries,
            'fatalities': self.fatalities,
            'investigation_complete': self.investigation_complete,
            'created_at': self.created_at.isoformat()
        }


class RiskHeatmap(BaseModel, TimestampMixin):
    """Real-time risk heatmap data"""
    __tablename__ = 'risk_heatmaps'
    
    # Snapshot time
    snapshot_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Risk data (3D grid)
    risk_grid = db.Column(db.JSON, nullable=False)  # 3D array of risk scores
    
    # Active hazards
    active_permits_count = db.Column(db.Integer, default=0)
    gas_alarms_count = db.Column(db.Integer, default=0)
    conflicts_count = db.Column(db.Integer, default=0)
    
    # Overall risk
    overall_risk_score = db.Column(db.Float)
    overall_risk_level = db.Column(SQLEnum(RiskLevel))
    
    def __repr__(self):
        return f''
    
    def to_dict(self):
        return {
            'id': self.id,
            'snapshot_time': self.snapshot_time.isoformat(),
            'risk_grid': self.risk_grid,
            'active_permits_count': self.active_permits_count,
            'gas_alarms_count': self.gas_alarms_count,
            'conflicts_count': self.conflicts_count,
            'overall_risk_score': self.overall_risk_score,
            'overall_risk_level': self.overall_risk_level.value if self.overall_risk_level else None
        }