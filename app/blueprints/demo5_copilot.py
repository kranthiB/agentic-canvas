"""
Demo 5: Engineer's Copilot Blueprint
T2 Procedural Workflow + Generative Agent routes + TotalEnergies Enhanced APIs
"""
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from datetime import datetime, date
import uuid
import random

from app import db

# Import TotalEnergies models
try:
    from app.models.demo5_models import (
        TEProduct, TETechnicalDoc, TEFormulationTrial,
        TEQueryHistory
    )
    TE_MODELS_AVAILABLE = True
except ImportError:
    TE_MODELS_AVAILABLE = False

demo5_bp = Blueprint('demo5', __name__)


@demo5_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard with TotalEnergies stats"""
    
    # Try to get TotalEnergies stats first
    if TE_MODELS_AVAILABLE:
        try:
            active_products = TEProduct.query.filter_by(status='active').count()
            trials_in_progress = TEFormulationTrial.query.filter_by(status='in_progress').count()
            trials_testing = TEFormulationTrial.query.filter_by(status='testing').count()
            trials_approved = TEFormulationTrial.query.filter_by(status='approved').count()
            
            today = datetime.now().date()
            queries_today = TEQueryHistory.query.filter(
                db.func.date(TEQueryHistory.created_at) == today
            ).count()
            
            total_docs = TETechnicalDoc.query.count()
            
            stats = {
                'active_products': active_products or 20,
                'formulation_trials': {
                    'in_progress': trials_in_progress or 4,
                    'testing': trials_testing or 4,
                    'approved': trials_approved or 12
                },
                'queries_today': queries_today,
                'avg_response_time': "2.3s",
                'knowledge_base': {
                    'technical_docs': total_docs or 50,
                    'formulations': 20,
                    'test_protocols': 15
                }
            }
        except Exception:
            # Fallback stats if database query fails
            stats = {
                'active_products': 20,
                'formulation_trials': {
                    'in_progress': 4,
                    'testing': 4,
                    'approved': 12
                },
                'queries_today': 0,
                'avg_response_time': "2.3s",
                'knowledge_base': {
                    'technical_docs': 50,
                    'formulations': 20,
                    'test_protocols': 15
                }
            }
    else:
        # Fallback stats when TE models not available
        stats = {
            'active_products': 20,
            'formulation_trials': {
                'in_progress': 4,
                'testing': 4,
                'approved': 12
            },
            'queries_today': 0,
            'avg_response_time': "2.3s",
            'knowledge_base': {
                'technical_docs': 50,
                'formulations': 20,
                'test_protocols': 15
            }
        }
    
    return render_template('demo5/dashboard.html', stats=stats)


# =====================================================
# TOTALENERGIES ENHANCED API ROUTES
# =====================================================

# Dashboard stats are provided by the main dashboard() route


@demo5_bp.route('/api/demo/scenarios', methods=['GET'])
@login_required
def api_demo_scenarios():
    """Get pre-configured demo scenarios"""
    scenarios = {
        'scenario1': {
            'name': 'VI Improver Dosage Query',
            'category': 'formulation',
            'query_en': "What's the recommended viscosity index improver dosage for Quartz 9000 5W-30?",
            'query_hi': "Quartz 9000 5W-30 के लिए अनुशंसित viscosity index improver की मात्रा क्या है?",
            'agents': ['formulation_agent'],
            'systems': ['PLM', 'Vector_DB']
        },
        'scenario2': {
            'name': 'Supplier Availability',
            'category': 'supply_chain',
            'query_en': "We need 500 MT of Group III base oil. Which approved suppliers can deliver to Mumbai within 2 weeks?",
            'query_hi': "हमें 500 MT Group III बेस ऑयल चाहिए। कौन से आपूर्तिकर्ता 2 सप्ताह में मुंबई में डिलीवर कर सकते हैं?",
            'agents': ['supply_chain_agent'],
            'systems': ['SAP_ERP', 'Supplier_Portal']
        },
        'scenario3': {
            'name': 'ZDDP Reduction for BS VI',
            'category': 'formulation_regulatory',
            'query_en': "Can we reduce ZDDP to 0.08% phosphorus for BS VI compliance without affecting wear protection?",
            'query_hi': "क्या हम BS VI के लिए ZDDP को 0.08% फॉस्फोरस तक कम कर सकते हैं?",
            'agents': ['formulation_agent', 'regulatory_agent'],
            'systems': ['PLM', 'Regulatory_DB']
        },
        'scenario4': {
            'name': 'LPG Contamination Crisis',
            'category': 'crisis_management',
            'query_en': "Customer complaints about white deposits in LPG cylinders. Investigate root cause and corrective actions.",
            'query_hi': "LPG सिलेंडरों में सफेद जमाव की शिकायतें। मूल कारण और सुधारात्मक कार्य की जांच करें।",
            'agents': ['formulation_agent', 'protocol_agent', 'regulatory_agent', 'supply_chain_agent'],
            'systems': ['LIMS', 'SAP_ERP', 'Regulatory_DB', 'Supplier_Portal']
        }
    }
    
    scenario_id = request.args.get('id')
    if scenario_id:
        return jsonify({'success': True, 'scenario': scenarios.get(scenario_id)})
    
    return jsonify({'success': True, 'scenarios': scenarios})


@demo5_bp.route('/api/query/process', methods=['POST'])
@login_required
def api_process_query():
    """Process engineer query with simulated multi-agent response"""
    if not TE_MODELS_AVAILABLE:
        return jsonify({'success': False, 'error': 'TotalEnergies models not available'}), 500
    
    try:
        data = request.json
        query = data.get('query')
        language = data.get('language', 'english')
        scenario_id = data.get('scenario_id')
        
        correlation_id = str(uuid.uuid4())
        
        # Simulate based on scenario
        if scenario_id == 'scenario1':
            result = _simulate_scenario1(query, language, correlation_id)
        elif scenario_id == 'scenario2':
            result = _simulate_scenario2(query, language, correlation_id)
        elif scenario_id == 'scenario3':
            result = _simulate_scenario3(query, language, correlation_id)
        elif scenario_id == 'scenario4':
            result = _simulate_scenario4(query, language, correlation_id)
        else:
            result = {
                'category': 'general',
                'agents': ['knowledge_orchestrator'],
                'response': f"Processing query: {query}",
                'sources': [],
                'processing_time_ms': 2000
            }
        
        # Save to query history
        try:
            query_history = TEQueryHistory(
                query_text=query,
                query_category=result.get('category'),
                agents_involved=result.get('agents'),
                response=result.get('response'),
                sources_cited=result.get('sources'),
                processing_time_ms=result.get('processing_time_ms'),
                language=language,
                session_id=correlation_id
            )
            db.session.add(query_history)
            db.session.commit()
        except Exception:
            pass  # Don't fail if logging fails
        
        return jsonify({
            'success': True,
            'correlation_id': correlation_id,
            **result
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def _simulate_scenario1(query, language, correlation_id):
    """Scenario 1: Formulation - VI Improver Dosage"""
    
    response_en = """**VI Improver Dosage for Quartz 9000 5W-30:**

**Recommended Dosage:** 8.5-9.2% w/w Polymethacrylate (PMA)

**Technical Specifications:**
- Target Viscosity: 11.2-11.8 cSt @ 100°C
- Viscosity Index: 168 (minimum)
- HTHS @ 150°C: 3.5 cP
- Shear Stability: SSI <30

**API SP Requirements Met:**
✓ LSPI prevention  
✓ Timing chain wear protection

**Reference:** QTZ9000-5W30-FORM-2024-Rev3.2

**Source:** TCAP Mumbai PLM System"""

    response_hi = """**Quartz 9000 5W-30 के लिए VI Improver मात्रा:**

**अनुशंसित मात्रा:** 8.5-9.2% w/w Polymethacrylate (PMA)

**तकनीकी विनिर्देश:**
- लक्ष्य Viscosity: 11.2-11.8 cSt @ 100°C
- Viscosity Index: 168 (न्यूनतम)

**API SP आवश्यकताएं:**
✓ LSPI रोकथाम  
✓ Timing chain wear सुरक्षा

**संदर्भ:** QTZ9000-5W30-FORM-2024-Rev3.2"""

    return {
        'category': 'formulation',
        'agents': ['formulation_agent'],
        'response': response_hi if language == 'hindi' else response_en,
        'sources': [
            {'type': 'PLM', 'document': 'Quartz 9000 Formulation Spec Rev 3.2'},
            {'type': 'Vector_DB', 'document': 'TCAP PMA VI Improver Research'}
        ],
        'processing_time_ms': random.randint(2000, 3000)
    }


def _simulate_scenario2(query, language, correlation_id):
    """Scenario 2: Supply Chain - Supplier Availability"""
    
    response_en = """**Group III Base Oil Suppliers (500 MT to Mumbai, ≤14 days):**

**Option 1: Indian Oil Corporation (IOCL)** ⭐ RECOMMENDED
- Quantity: 1,200 MT available
- Lead Time: 10-12 days
- Price: ₹94,200/MT
- Quality: Group III+ 4 cSt (VI 125+)

**Option 2: Nayara Energy (Vadinar)**
- Quantity: 800 MT available  
- Lead Time: 7-10 days
- Price: ₹95,500/MT

**Option 3: Reliance Industries**
- Quantity: 600 MT available
- Lead Time: 8-10 days
- Price: ₹96,800/MT

**Recommendation:** IOCL offers best price-availability balance

**Source:** SAP ERP Inventory + Supplier Portal"""

    response_hi = """**Group III बेस ऑयल आपूर्तिकर्ता (500 MT मुंबई, ≤14 दिन):**

**विकल्प 1: Indian Oil Corporation (IOCL)** ⭐ अनुशंसित
- मात्रा: 1,200 MT उपलब्ध
- लीड टाइम: 10-12 दिन  
- मूल्य: ₹94,200/MT

**विकल्प 2: Nayara Energy**
- मात्रा: 800 MT उपलब्ध
- मूल्य: ₹95,500/MT

**सिफारिश:** IOCL सर्वोत्तम मूल्य-उपलब्धता संतुलन

**स्रोत:** SAP ERP + आपूर्तिकर्ता पोर्टल"""

    return {
        'category': 'supply_chain',
        'agents': ['supply_chain_agent'],
        'response': response_hi if language == 'hindi' else response_en,
        'sources': [
            {'type': 'SAP_ERP', 'document': 'Material Master BASEOLL-GRP3'},
            {'type': 'Supplier_Portal', 'document': 'Supplier Availability Matrix'}
        ],
        'processing_time_ms': random.randint(2200, 3200)
    }


def _simulate_scenario3(query, language, correlation_id):
    """Scenario 3: Formulation + Regulatory"""
    
    response_en = """**ZDDP Reduction Analysis for BS VI Compliance:**

**Regulatory Context:**
- BS VI allows max 0.12% phosphorus
- Lower content preferred for DPF protection

**Formulation Strategy:**
1. Reduce ZDDP to 0.08% phosphorus
2. Add molybdenum dithiocarbamate (MoDTC) 600-800 ppm
3. Add boron anti-wear 500 ppm

**Performance Validation Required:**
- Sequence IVA (wear test)
- Sequence IIIH (oxidation test)

**Risk Assessment:** Medium - may affect older engines

**Timeline:** 8-12 months with field trials

**Source:** PLM Formulation Database + Regulatory DB"""

    response_hi = """**BS VI के लिए ZDDP कमी विश्लेषण:**

**नियामक संदर्भ:**
- BS VI अधिकतम 0.12% फॉस्फोरस की अनुमति देता है

**फॉर्मूलेशन रणनीति:**
1. ZDDP को 0.08% फॉस्फोरस तक कम करें
2. MoDTC 600-800 ppm जोड़ें
3. Boron anti-wear 500 ppm जोड़ें

**आवश्यक परीक्षण:**
- Sequence IVA (wear test)
- Sequence IIIH (oxidation test)

**स्रोत:** PLM + Regulatory DB"""

    return {
        'category': 'formulation_regulatory',
        'agents': ['formulation_agent', 'regulatory_agent'],
        'response': response_hi if language == 'hindi' else response_en,
        'sources': [
            {'type': 'PLM', 'document': 'Diesel Oil Formulation Guidelines'},
            {'type': 'Regulatory_DB', 'document': 'BS VI Emission Standards'}
        ],
        'processing_time_ms': random.randint(3500, 4500)
    }


def _simulate_scenario4(query, language, correlation_id):
    """Scenario 4: Multi-Agent Crisis Investigation"""
    
    response_en = """**LPG Cylinder Contamination Investigation:**

**Root Cause Analysis (Protocol Agent + LIMS):**
- Batch: LPG-DOM-2025-0312
- Moisture content: 180 ppm (Spec: <50 ppm) ❌
- Root Cause: Atmospheric moisture ingress during tank maintenance

**Formulation Impact (Formulation Agent):**
- Water + LPG + Low temp → Gas hydrates (white crystalline deposits)

**Affected Inventory (Supply Chain Agent + SAP):**
- 8,500 cylinders affected
- 3,200 already distributed
- Estimated cost: ₹48 lakh recall

**Regulatory Impact (Regulatory Agent):**
- PESO reporting mandatory within 48 hours
- Voluntary product recall recommended

**Corrective Actions:**
1. Immediate: Quarantine all affected batches
2. Short-term: Install moisture analyzers (₹16 lakh)
3. Long-term: LPG dehydration unit (₹65 lakh)

**Timeline:** 30 days for complete recall

**Source:** LIMS + SAP + Regulatory DB + Supplier Portal"""

    response_hi = """**LPG सिलेंडर संदूषण जांच:**

**मूल कारण (Protocol Agent + LIMS):**
- बैच: LPG-DOM-2025-0312
- नमी: 180 ppm (विनिर्देश: <50 ppm) ❌
- कारण: रखरखाव के दौरान नमी प्रवेश

**प्रभावित स्टॉक (Supply Chain + SAP):**
- 8,500 सिलेंडर प्रभावित
- 3,200 वितरित
- लागत: ₹48 लाख

**नियामक (Regulatory Agent):**
- 48 घंटे में PESO रिपोर्ट आवश्यक
- उत्पाद वापसी अनुशंसित

**सुधारात्मक कार्य:**
1. तत्काल: सभी बैच अलग करें
2. अल्पकालिक: नमी विश्लेषक (₹16 लाख)
3. दीर्घकालिक: निर्जलीकरण इकाई (₹65 लाख)

**स्रोत:** LIMS + SAP + Regulatory DB"""

    return {
        'category': 'crisis_management',
        'agents': ['formulation_agent', 'protocol_agent', 'regulatory_agent', 'supply_chain_agent'],
        'response': response_hi if language == 'hindi' else response_en,
        'sources': [
            {'type': 'LIMS', 'document': 'Batch Test Results LPG-DOM-2025-0312'},
            {'type': 'SAP_ERP', 'document': 'Affected Batch Traceability'},
            {'type': 'Regulatory_DB', 'document': 'PESO Reporting Requirements'},
            {'type': 'Supplier_Portal', 'document': 'LPG Source Quality Data'}
        ],
        'processing_time_ms': random.randint(5000, 7000)
    }


# Only dashboard and query processing routes are used
# All other routes removed as their templates don't exist
