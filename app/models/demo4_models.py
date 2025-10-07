"""
Demo 4: Mobility Maestro Models
T3 Cognitive Autonomous Agent for CNG refueling network optimization
"""
from datetime import datetime
from sqlalchemy import Enum as SQLEnum
import enum
from app import db
from app.core.database import BaseModel, TimestampMixin


class CityTier(enum.Enum):
    """City tier classification"""
    TIER_1 = "tier_1"
    TIER_2 = "tier_2"
    TIER_3 = "tier_3"


class NetworkPosition(enum.Enum):
    """Position in network"""
    URBAN = "urban"
    HIGHWAY = "highway"
    SUBURBAN = "suburban"


class SiteStatus(enum.Enum):
    """Site evaluation status"""
    CANDIDATE = "candidate"
    EVALUATED = "evaluated"
    SELECTED = "selected"
    DEPLOYED = "deployed"
    REJECTED = "rejected"


class CNGSite(BaseModel, TimestampMixin):
    """Candidate CNG refueling station sites"""
    __tablename__ = 'cng_sites'
    
    # Location
    site_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    city = db.Column(db.String(100), nullable=False, index=True)
    state = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    
    # Classification
    city_tier = db.Column(SQLEnum(CityTier), nullable=False)
    network_position = db.Column(SQLEnum(NetworkPosition), nullable=False)
    
    # Site characteristics
    land_area_sqm = db.Column(db.Float)
    land_cost_inr = db.Column(db.Float)
    gas_pipeline_available = db.Column(db.Boolean, default=True)
    pipeline_capacity_scm = db.Column(db.Float)  # Standard Cubic Meters
    
    # Demographics
    population_density = db.Column(db.Float)  # per km²
    avg_household_income = db.Column(db.Float)
    cng_vehicle_penetration_rate = db.Column(db.Float)  # Percentage
    
    # Traffic & Demand
    daily_traffic_count = db.Column(db.Integer)
    estimated_daily_refuels = db.Column(db.Integer)
    peak_hour_demand = db.Column(db.Float)
    
    # Competition
    existing_cng_stations_within_5km = db.Column(db.Integer, default=0)
    nearest_competitor_distance_km = db.Column(db.Float)
    
    # Status
    status = db.Column(SQLEnum(SiteStatus), default=SiteStatus.CANDIDATE)
    
    # Relationships
    evaluation = db.relationship('SiteEvaluation', uselist=False, backref='site')
    
    def __repr__(self):
        return f''
    
    def to_dict(self):
        return {
            'id': self.id,
            'site_id': self.site_id,
            'city': self.city,
            'state': self.state,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'city_tier': self.city_tier.value,
            'network_position': self.network_position.value,
            'daily_traffic_count': self.daily_traffic_count,
            'estimated_daily_refuels': self.estimated_daily_refuels,
            'status': self.status.value,
            'created_at': self.created_at.isoformat()
        }


class SiteEvaluation(BaseModel, TimestampMixin):
    """AI-powered site evaluation results"""
    __tablename__ = 'site_evaluations'
    
    site_id = db.Column(db.Integer, db.ForeignKey('cng_sites.id'), nullable=False)
    
    # Evaluation scores (0-100)
    traffic_score = db.Column(db.Float, nullable=False)
    demographics_score = db.Column(db.Float, nullable=False)
    pipeline_infrastructure_score = db.Column(db.Float, nullable=False)
    competition_score = db.Column(db.Float, nullable=False)
    accessibility_score = db.Column(db.Float, nullable=False)
    
    # Overall
    overall_score = db.Column(db.Float, nullable=False)
    rank = db.Column(db.Integer)
    
    # Financial projections
    capex_inr = db.Column(db.Float)  # Capital expenditure
    opex_annual_inr = db.Column(db.Float)  # Operating expenditure
    revenue_year1_inr = db.Column(db.Float)
    revenue_year5_inr = db.Column(db.Float)
    
    # ROI metrics
    npv_inr = db.Column(db.Float)  # Net Present Value
    irr_percentage = db.Column(db.Float)  # Internal Rate of Return
    payback_years = db.Column(db.Float)
    
    # AI analysis
    evaluated_by_agent = db.Column(db.String(100))
    confidence_score = db.Column(db.Float)  # 0-1
    reasoning = db.Column(db.Text)
    
    # Recommendations
    recommendation = db.Column(db.String(20))  # strong_select, select, consider, reject
    risk_factors = db.Column(db.JSON)
    opportunities = db.Column(db.JSON)
    
    def __repr__(self):
        return f''
    
    def to_dict(self):
        return {
            'id': self.id,
            'site_id': self.site_id,
            'scores': {
                'traffic': round(self.traffic_score, 1),
                'demographics': round(self.demographics_score, 1),
                'pipeline_infrastructure': round(self.pipeline_infrastructure_score, 1),
                'competition': round(self.competition_score, 1),
                'accessibility': round(self.accessibility_score, 1),
                'overall': round(self.overall_score, 1)
            },
            'rank': self.rank,
            'financials': {
                'capex_inr': self.capex_inr,
                'opex_annual_inr': self.opex_annual_inr,
                'npv_inr': self.npv_inr,
                'irr_percentage': self.irr_percentage,
                'payback_years': self.payback_years
            },
            'recommendation': self.recommendation,
            'confidence_score': self.confidence_score,
            'created_at': self.created_at.isoformat()
        }


class NetworkConfiguration(BaseModel, TimestampMixin):
    """Optimized network configurations"""
    __tablename__ = 'network_configurations'
    
    # Configuration info
    config_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Optimization parameters
    total_budget_inr = db.Column(db.Float, nullable=False)
    target_sites_count = db.Column(db.Integer, nullable=False)
    
    # Selected sites
    selected_site_ids = db.Column(db.JSON, nullable=False)  # List of site IDs
    
    # Performance metrics
    total_capex_inr = db.Column(db.Float)
    total_annual_revenue_inr = db.Column(db.Float)
    network_coverage_percentage = db.Column(db.Float)
    population_served = db.Column(db.Integer)
    
    # Optimization results
    optimization_objective = db.Column(db.String(100))  # max_revenue, max_coverage, balanced
    optimization_algorithm = db.Column(db.String(100))
    optimization_time_ms = db.Column(db.Integer)
    
    # ROI
    network_npv_inr = db.Column(db.Float)
    network_irr_percentage = db.Column(db.Float)
    
    # AI agent
    optimized_by_agent = db.Column(db.String(100))
    
    def __repr__(self):
        return f''
    
    def to_dict(self):
        return {
            'id': self.id,
            'config_name': self.config_name,
            'description': self.description,
            'total_budget_inr': self.total_budget_inr,
            'target_sites_count': self.target_sites_count,
            'selected_site_ids': self.selected_site_ids,
            'total_capex_inr': self.total_capex_inr,
            'total_annual_revenue_inr': self.total_annual_revenue_inr,
            'network_coverage_percentage': self.network_coverage_percentage,
            'population_served': self.population_served,
            'network_npv_inr': self.network_npv_inr,
            'network_irr_percentage': self.network_irr_percentage,
            'created_at': self.created_at.isoformat()
        }


class DemandForecast(BaseModel, TimestampMixin):
    """CNG refueling demand forecasts"""
    __tablename__ = 'demand_forecasts'
    
    # Location
    site_id = db.Column(db.Integer, db.ForeignKey('cng_sites.id'), nullable=False)
    
    # Forecast period
    forecast_date = db.Column(db.Date, nullable=False)
    hour = db.Column(db.Integer)  # 0-23 for hourly forecasts
    
    # Demand
    forecasted_refuels = db.Column(db.Integer)
    forecasted_volume_scm = db.Column(db.Float)  # Standard Cubic Meters
    forecasted_revenue_inr = db.Column(db.Float)
    
    # Price
    dynamic_price_inr_scm = db.Column(db.Float)  # Per Standard Cubic Meter
    price_adjustment = db.Column(db.Float)  # Percentage
    
    # Confidence
    confidence_interval_low = db.Column(db.Float)
    confidence_interval_high = db.Column(db.Float)
    
    def __repr__(self):
        return f''
    
    def to_dict(self):
        return {
            'id': self.id,
            'site_id': self.site_id,
            'forecast_date': self.forecast_date.isoformat(),
            'hour': self.hour,
            'forecasted_refuels': self.forecasted_refuels,
            'forecasted_volume_scm': self.forecasted_volume_scm,
            'forecasted_revenue_inr': self.forecasted_revenue_inr,
            'dynamic_price_inr_scm': self.dynamic_price_inr_scm
        }