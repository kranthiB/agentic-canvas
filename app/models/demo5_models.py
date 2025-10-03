"""
TotalEnergies-Specific Models for Engineer's Copilot
Extended models for realistic demo scenarios
"""
from datetime import datetime
from sqlalchemy import Enum as SQLEnum
import enum
from app import db
from app.core.database import BaseModel, TimestampMixin


# =====================================================
# 1. TotalEnergies Product Catalog
# =====================================================
class TEProduct(BaseModel, TimestampMixin):
    """TotalEnergies product catalog"""
    __tablename__ = 'te_products'
    
    product_name = db.Column(db.String(200), nullable=False, index=True)
    product_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    product_type = db.Column(db.String(50), nullable=False)  # lubricant, lpg, special_fluid
    grade = db.Column(db.String(100))
    specifications = db.Column(db.JSON)  # All product specs
    formulation_summary = db.Column(db.JSON)  # High-level formulation
    market_segment = db.Column(db.String(100))
    status = db.Column(db.String(20), default='active')
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_name': self.product_name,
            'product_code': self.product_code,
            'product_type': self.product_type,
            'grade': self.grade,
            'specifications': self.specifications,
            'market_segment': self.market_segment,
            'status': self.status
        }


# =====================================================
# 2. Technical Documents (Enhanced Knowledge Base)
# =====================================================
class TETechnicalDoc(BaseModel, TimestampMixin):
    """Technical documents - formulation specs, test protocols, standards"""
    __tablename__ = 'te_technical_docs'
    
    doc_type = db.Column(db.String(50), nullable=False, index=True)
    title = db.Column(db.String(500), nullable=False)
    product_related = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    doc_metadata = db.Column(db.JSON)  # author, version, etc.
    tags = db.Column(db.String(500))
    indexed_at = db.Column(db.DateTime, default=datetime.utcnow)
    relevance_score = db.Column(db.Float, default=1.0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'doc_type': self.doc_type,
            'title': self.title,
            'product_related': self.product_related,
            'content': self.content[:500] + '...' if len(self.content) > 500 else self.content,
            'doc_metadata': self.doc_metadata,
            'indexed_at': self.indexed_at.isoformat() if self.indexed_at else None
        }


# =====================================================
# 3. Formulation Trials (Extended)
# =====================================================
class TEFormulationTrial(BaseModel, TimestampMixin):
    """Detailed formulation trial records"""
    __tablename__ = 'te_formulation_trials'
    
    trial_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    product_family = db.Column(db.String(100), nullable=False, index=True)
    formulation = db.Column(db.JSON, nullable=False)  # Detailed formulation
    test_results = db.Column(db.JSON)  # All test results
    status = db.Column(db.String(50), default='in_progress')
    engineer_name = db.Column(db.String(100))
    notes = db.Column(db.Text)
    completed_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'trial_code': self.trial_code,
            'product_family': self.product_family,
            'formulation': self.formulation,
            'test_results': self.test_results,
            'status': self.status,
            'engineer_name': self.engineer_name,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# =====================================================
# 4. SAP ERP Inventory (Mock)
# =====================================================
class TESAPInventory(db.Model, TimestampMixin):
    """Mock SAP ERP inventory data"""
    __tablename__ = 'te_sap_inventory'
    
    material_code = db.Column(db.String(50), primary_key=True)
    material_name = db.Column(db.String(200), nullable=False)
    material_category = db.Column(db.String(100))
    stock_quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(10), nullable=False)
    price = db.Column(db.Float, nullable=False)
    supplier = db.Column(db.String(200))
    plant_location = db.Column(db.String(100), default='Mumbai')
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'material_code': self.material_code,
            'material_name': self.material_name,
            'material_category': self.material_category,
            'stock_quantity': self.stock_quantity,
            'unit': self.unit,
            'price': self.price,
            'supplier': self.supplier,
            'plant_location': self.plant_location,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }


# =====================================================
# 5. LIMS Test Results (Mock)
# =====================================================
class TELIMSTest(db.Model, TimestampMixin):
    """Mock LIMS test results"""
    __tablename__ = 'te_lims_tests'
    
    test_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    batch_code = db.Column(db.String(50), nullable=False, index=True)
    product_code = db.Column(db.String(50))
    test_type = db.Column(db.String(100), nullable=False)
    test_date = db.Column(db.Date, nullable=False)
    results = db.Column(db.JSON, nullable=False)
    pass_fail = db.Column(db.String(10), nullable=False)
    analyst = db.Column(db.String(100))
    notes = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'test_id': self.test_id,
            'batch_code': self.batch_code,
            'product_code': self.product_code,
            'test_type': self.test_type,
            'test_date': self.test_date.isoformat() if self.test_date else None,
            'results': self.results,
            'pass_fail': self.pass_fail,
            'analyst': self.analyst
        }


# =====================================================
# 6. Supplier Catalog (Mock)
# =====================================================
class TESupplier(db.Model, TimestampMixin):
    """Supplier catalog for raw materials"""
    __tablename__ = 'te_supplier_catalog'
    
    supplier_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    supplier_name = db.Column(db.String(200), nullable=False)
    material_type = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    lead_time_days = db.Column(db.Integer)
    quality_rating = db.Column(db.Float)
    certifications = db.Column(db.JSON)
    is_approved = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier_name,
            'material_type': self.material_type,
            'location': self.location,
            'lead_time_days': self.lead_time_days,
            'quality_rating': self.quality_rating,
            'certifications': self.certifications,
            'is_approved': self.is_approved
        }


# =====================================================
# 7. Query History (Enhanced)
# =====================================================
class TEQueryHistory(BaseModel, TimestampMixin):
    """Enhanced query history for analytics"""
    __tablename__ = 'te_query_history'
    
    query_text = db.Column(db.Text, nullable=False)
    query_text_hindi = db.Column(db.Text)
    query_category = db.Column(db.String(100))
    agents_involved = db.Column(db.JSON)
    response = db.Column(db.Text, nullable=False)
    response_hindi = db.Column(db.Text)
    sources_cited = db.Column(db.JSON)
    processing_time_ms = db.Column(db.Integer)
    user_rating = db.Column(db.Integer)
    user_feedback = db.Column(db.Text)
    language = db.Column(db.String(20), default='english')
    session_id = db.Column(db.String(100))
    
    def to_dict(self):
        return {
            'id': self.id,
            'query_text': self.query_text,
            'query_category': self.query_category,
            'agents_involved': self.agents_involved,
            'response': self.response,
            'sources_cited': self.sources_cited,
            'processing_time_ms': self.processing_time_ms,
            'language': self.language,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# =====================================================
# 9. Agent Activity Log
# =====================================================
class TEAgentActivity(BaseModel, TimestampMixin):
    """Agent activity for event flow visualization"""
    __tablename__ = 'te_agent_activity'
    
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


# =====================================================
# 10. Event Traces (for Visualization)
# =====================================================
class TEEventTrace(BaseModel, TimestampMixin):
    """Event traces for flow visualization"""
    __tablename__ = 'te_event_traces'
    
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


# =====================================================
# 9. Greeting Responses & Capabilities
# =====================================================
class TEGreetingResponse(BaseModel, TimestampMixin):
    """Store greeting responses and copilot capabilities"""
    __tablename__ = 'te_greeting_responses'
    
    greeting_type = db.Column(db.String(50), nullable=False, index=True)  # hello, hi, namaste, capabilities, help
    language = db.Column(db.String(10), nullable=False, default='en')  # en, hi
    response_text = db.Column(db.Text, nullable=False)
    response_category = db.Column(db.String(50), nullable=False)  # greeting, capabilities, help
    priority = db.Column(db.Integer, default=1)  # For randomizing responses
    active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'greeting_type': self.greeting_type,
            'language': self.language,
            'response_text': self.response_text,
            'response_category': self.response_category,
            'priority': self.priority,
            'active': self.active
        }
