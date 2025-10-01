"""
Demo 5: Engineer's Copilot Models
T2 Procedural Workflow Agent + Generative for TCAP Mumbai R&D
"""
from datetime import datetime
from sqlalchemy import Enum as SQLEnum
import enum
from app import db
from app.core.database import BaseModel, TimestampMixin


class DocumentType(enum.Enum):
    """Research document type"""
    PAPER = "paper"
    REPORT = "report"
    THESIS = "thesis"
    PATENT = "patent"
    STANDARD = "standard"


class TrialStatus(enum.Enum):
    """Formulation trial status"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"


class FormulationStatus(enum.Enum):
    """Recommended formulation status"""
    RECOMMENDED = "recommended"
    UNDER_TESTING = "under_testing"
    APPROVED = "approved"
    REJECTED = "rejected"


class ProtocolStatus(enum.Enum):
    """Test protocol status"""
    DRAFT = "draft"
    GENERATED = "generated"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class ResearchPaper(BaseModel, TimestampMixin):
    """Research papers and documents"""
    __tablename__ = 'research_papers'
    
    # Document info
    paper_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    title = db.Column(db.String(300), nullable=False, index=True)
    authors = db.Column(db.JSON)  # List of author names
    
    # Publication
    publication_date = db.Column(db.Date)
    source = db.Column(db.String(200))  # Journal, conference, internal
    document_type = db.Column(SQLEnum(DocumentType), default=DocumentType.PAPER)
    
    # Content
    abstract = db.Column(db.Text)
    keywords = db.Column(db.JSON)
    full_text = db.Column(db.Text)  # For semantic search
    
    # Classification
    research_area = db.Column(db.String(100))  # engine_oils, industrial_lubricants, etc.
    product_category = db.Column(db.String(100))
    
    # Embeddings (for vector search)
    embedding_vector = db.Column(db.JSON)  # Store embeddings for semantic search
    
    # Language
    language = db.Column(db.String(10), default='en')
    
    # Metadata
    citation_count = db.Column(db.Integer, default=0)
    relevance_score = db.Column(db.Float)
    
    def __repr__(self):
        return f''
    
    def to_dict(self):
        return {
            'id': self.id,
            'paper_id': self.paper_id,
            'title': self.title,
            'authors': self.authors,
            'publication_date': self.publication_date.isoformat() if self.publication_date else None,
            'source': self.source,
            'document_type': self.document_type.value,
            'abstract': self.abstract,
            'keywords': self.keywords,
            'research_area': self.research_area,
            'language': self.language,
            'created_at': self.created_at.isoformat()
        }


class FormulationTrial(BaseModel, TimestampMixin):
    """Lubricant formulation trial records"""
    __tablename__ = 'formulation_trials'
    
    # Trial info
    trial_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    trial_name = db.Column(db.String(200), nullable=False)
    
    # Formulation
    base_oil = db.Column(db.String(200), nullable=False)
    base_oil_percentage = db.Column(db.Float, nullable=False)
    additive_package = db.Column(db.JSON, nullable=False)  # List of additives with percentages
    
    # Product info
    product_type = db.Column(db.String(100), nullable=False)  # Engine oil, hydraulic oil, etc.
    target_viscosity_grade = db.Column(db.String(50))
    
    # Test results
    viscosity_40c = db.Column(db.Float)
    viscosity_100c = db.Column(db.Float)
    viscosity_index = db.Column(db.Float)
    pour_point_c = db.Column(db.Float)
    flash_point_c = db.Column(db.Float)
    
    # Performance tests
    wear_resistance_score = db.Column(db.Float)  # Four-ball test
    oxidation_stability_hours = db.Column(db.Float)
    foam_characteristics = db.Column(db.String(50))
    
    # Overall assessment
    performance_score = db.Column(db.Float)  # 0-100
    meets_specifications = db.Column(db.Boolean, default=False)
    
    # Cost
    cost_per_liter_inr = db.Column(db.Float)
    
    # Status
    status = db.Column(SQLEnum(TrialStatus), default=TrialStatus.PLANNED)
    
    # Personnel
    researcher_name = db.Column(db.String(100))
    approved_by = db.Column(db.String(100))
    
    # Notes
    observations = db.Column(db.Text)
    recommendations = db.Column(db.Text)
    
    def __repr__(self):
        return f''
    
    def to_dict(self):
        return {
            'id': self.id,
            'trial_id': self.trial_id,
            'trial_name': self.trial_name,
            'base_oil': self.base_oil,
            'product_type': self.product_type,
            'test_results': {
                'viscosity_index': self.viscosity_index,
                'wear_resistance_score': self.wear_resistance_score,
                'oxidation_stability_hours': self.oxidation_stability_hours,
                'performance_score': self.performance_score
            },
            'cost_per_liter_inr': self.cost_per_liter_inr,
            'status': self.status.value,
            'meets_specifications': self.meets_specifications,
            'created_at': self.created_at.isoformat()
        }


class FormulationRequest(BaseModel, TimestampMixin):
    """Engineer's request for formulation recommendation"""
    __tablename__ = 'formulation_requests'
    
    # Request info
    request_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    request_title = db.Column(db.String(200), nullable=False)
    
    # Requirements
    product_type = db.Column(db.String(100), nullable=False)
    target_properties = db.Column(db.JSON, nullable=False)
    constraints = db.Column(db.JSON)  # Cost, availability, regulations
    
    # Context
    application = db.Column(db.String(200))
    operating_conditions = db.Column(db.JSON)
    
    # Requested by
    researcher_name = db.Column(db.String(100))
    department = db.Column(db.String(100))
    
    # Language
    request_language = db.Column(db.String(10), default='en')
    
    # AI processing
    processed = db.Column(db.Boolean, default=False)
    processing_time_ms = db.Column(db.Integer)
    
    # Relationships
    recommended_formulations = db.relationship('RecommendedFormulation', backref='request', lazy='dynamic')
    
    def __repr__(self):
        return f''
    
    def to_dict(self):
        return {
            'id': self.id,
            'request_id': self.request_id,
            'request_title': self.request_title,
            'product_type': self.product_type,
            'target_properties': self.target_properties,
            'constraints': self.constraints,
            'researcher_name': self.researcher_name,
            'request_language': self.request_language,
            'processed': self.processed,
            'created_at': self.created_at.isoformat()
        }


class RecommendedFormulation(BaseModel, TimestampMixin):
    """AI-recommended formulations"""
    __tablename__ = 'recommended_formulations'
    
    request_id = db.Column(db.Integer, db.ForeignKey('formulation_requests.id'), nullable=False)
    
    # Formulation
    formulation_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Composition
    base_oil = db.Column(db.String(200), nullable=False)
    additive_package = db.Column(db.JSON, nullable=False)
    
    # Predictions
    predicted_viscosity_index = db.Column(db.Float)
    predicted_wear_resistance = db.Column(db.Float)
    predicted_oxidation_stability = db.Column(db.Float)
    predicted_performance_score = db.Column(db.Float)
    
    # Cost
    total_cost_per_liter = db.Column(db.Float)
    
    # AI reasoning
    reasoning_chain = db.Column(db.JSON)  # Step-by-step reasoning
    confidence_score = db.Column(db.Float)  # 0-1
    similar_trials = db.Column(db.JSON)  # References to similar past trials
    
    # Ranking
    recommendation_rank = db.Column(db.Integer)  # 1 = best recommendation
    
    # Pros & Cons
    pros = db.Column(db.JSON)
    cons = db.Column(db.JSON)
    
    # Status
    status = db.Column(SQLEnum(FormulationStatus), default=FormulationStatus.RECOMMENDED)
    tested = db.Column(db.Boolean, default=False)
    test_trial_id = db.Column(db.String(50))
    
    def __repr__(self):
        return f''
    
    def to_dict(self):
        return {
            'id': self.id,
            'formulation_id': self.formulation_id,
            'name': self.name,
            'description': self.description,
            'base_oil': self.base_oil,
            'additive_package': self.additive_package,
            'predicted_properties': {
                'viscosity_index': self.predicted_viscosity_index,
                'wear_resistance': self.predicted_wear_resistance,
                'oxidation_stability': self.predicted_oxidation_stability,
                'performance_score': self.predicted_performance_score
            },
            'total_cost_per_liter': self.total_cost_per_liter,
            'confidence_score': self.confidence_score,
            'recommendation_rank': self.recommendation_rank,
            'pros': self.pros,
            'cons': self.cons,
            'status': self.status.value,
            'created_at': self.created_at.isoformat()
        }


class TestProtocol(BaseModel, TimestampMixin):
    """Auto-generated test protocols"""
    __tablename__ = 'test_protocols'
    
    # Protocol info
    protocol_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    title = db.Column(db.String(300), nullable=False)
    formulation_id = db.Column(db.String(50))
    
    # Test details
    test_standards = db.Column(db.JSON)  # List of standards (ASTM, BIS, API)
    test_sequence = db.Column(db.JSON)  # Ordered test steps
    
    # Content
    objective = db.Column(db.Text)
    scope = db.Column(db.Text)
    equipment_required = db.Column(db.JSON)
    reagents_required = db.Column(db.JSON)
    safety_precautions = db.Column(db.Text)
    procedure_steps = db.Column(db.JSON)  # Detailed steps
    expected_results = db.Column(db.JSON)
    acceptance_criteria = db.Column(db.JSON)
    
    # Resources
    estimated_duration_hours = db.Column(db.Float)
    estimated_cost_inr = db.Column(db.Float)
    required_personnel = db.Column(db.Integer, default=1)
    
    # AI generation
    generated_by_agent = db.Column(db.String(100))
    generation_prompt = db.Column(db.Text)
    confidence_score = db.Column(db.Float)
    
    # Language
    language = db.Column(db.String(10), default='en')
    
    # Status
    status = db.Column(SQLEnum(ProtocolStatus), default=ProtocolStatus.DRAFT)
    reviewed_by_human = db.Column(db.Boolean, default=False)
    
    # Execution
    assigned_to = db.Column(db.String(100))
    start_date = db.Column(db.DateTime)
    completion_date = db.Column(db.DateTime)
    test_results = db.Column(db.JSON)
    
    def __repr__(self):
        return f''
    
    def to_dict(self):
        return {
            'id': self.id,
            'protocol_id': self.protocol_id,
            'title': self.title,
            'test_standards': self.test_standards,
            'objective': self.objective,
            'equipment_required': self.equipment_required,
            'procedure_steps': self.procedure_steps,
            'estimated_duration_hours': self.estimated_duration_hours,
            'estimated_cost_inr': self.estimated_cost_inr,
            'language': self.language,
            'status': self.status.value,
            'created_at': self.created_at.isoformat()
        }


class ChatMessage(BaseModel, TimestampMixin):
    """Chat conversation history"""
    __tablename__ = 'chat_messages'
    
    # Session
    session_id = db.Column(db.String(100), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Message
    role = db.Column(db.String(20), nullable=False)  # user, assistant, system
    content = db.Column(db.Text, nullable=False)
    
    # Context
    intent = db.Column(db.String(100))  # search, formulation, protocol, explain
    entities = db.Column(db.JSON)  # Extracted entities
    
    # Language
    language = db.Column(db.String(10), default='en')
    
    # AI metadata
    model_used = db.Column(db.String(50))
    tokens_used = db.Column(db.Integer)
    response_time_ms = db.Column(db.Integer)
    
    def __repr__(self):
        return f''
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'role': self.role,
            'content': self.content,
            'intent': self.intent,
            'language': self.language,
            'timestamp': self.created_at.isoformat()
        }