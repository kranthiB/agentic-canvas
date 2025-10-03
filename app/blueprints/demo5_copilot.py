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
        TEQueryHistory, TEGreetingResponse
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
        language = data.get('language', 'english')  # Default to 'english'
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
            # Handle specific queries based on content with improved pattern matching
            query_lower = query.lower()
            
            # Check for greetings and capability queries FIRST - highest priority
            if _is_greeting_query(query_lower, language):
                result = _handle_greeting_query(query, language, correlation_id)
            
            # Hindi language patterns - add common Hindi terms
            elif language == 'hindi' or language == 'hi':
                # Convert some common Hindi terms for pattern matching
                hindi_patterns = {
                    'कम स्टॉक': 'low stock',
                    'स्टॉक स्तर': 'stock levels', 
                    'सामग्री': 'materials',
                    'आपूर्तिकर्ता': 'suppliers',
                    'आपूर्तिकर्ताओं': 'suppliers',
                    'बैच': 'batch',
                    'असफल': 'fail',
                    'विस्कोसिटी': 'viscosity',
                    'फॉर्मूलेशन': 'formulation',
                    'परीक्षण': 'testing',
                    'गुजरात': 'gujarat',
                    'प्रमाणन': 'certifications',
                    'प्रमाणपत्र': 'certifications',
                    'नमी': 'moisture',
                    'एलपीजी': 'lpg',
                    'सिलेंडर': 'cylinders',
                    'सफेद जमाव': 'white deposits',
                    'ऑटोमोटिव': 'automotive',
                    'आवश्यकताएं': 'requirements',
                    'इन्वेंट्री': 'inventory',
                    'स्तर': 'levels',
                    'ट्रायल': 'trial',
                    'दिखाएं': 'show',
                    'भारी शुल्क': 'heavy duty',
                    'भारी': 'heavy',
                    'वेरिएंट': 'variant',
                    'विकसित': 'develop',
                    'हमें': 'we need',
                    'चाहिए': 'need',
                    'सप्ताह': 'weeks',
                    'डिलीवर': 'deliver',
                    'मुंबई': 'mumbai',
                    'अनुशंसित': 'recommended',
                    'मात्रा': 'dosage',
                    'अनुप्रयोगों': 'applications',
                    'बेस ऑयल': 'base oil'
                }
                
                # Replace Hindi terms with English equivalents for pattern matching
                for hindi, english in hindi_patterns.items():
                    if hindi in query_lower:
                        query_lower = query_lower.replace(hindi, english)
            
            # ZDDP reduction for BS VI compliance
            elif ('zddp' in query_lower and 'bs vi' in query_lower) or \
               ('zddp' in query_lower and 'phosphorus' in query_lower and 'compliance' in query_lower) or \
               ('reduce zddp' in query_lower and ('bs vi' in query_lower or 'compliance' in query_lower)):
                result = _simulate_zddp_bs_vi_compliance_query(query, language, correlation_id)
            
            # Group III base oil supplier queries
            elif ('group iii' in query_lower and 'base oil' in query_lower and 'suppliers' in query_lower) or \
                 ('suppliers' in query_lower and 'group iii' in query_lower and ('deliver' in query_lower or 'mumbai' in query_lower)) or \
                 ('need' in query_lower and 'group iii' in query_lower and ('mt' in query_lower or 'suppliers' in query_lower)):
                result = _simulate_group_iii_supplier_query(query, language, correlation_id)
            
            # LPG white deposits investigation
            elif ('white deposits' in query_lower and 'lpg' in query_lower) or \
                 ('customer complaints' in query_lower and 'lpg cylinders' in query_lower) or \
                 ('investigate' in query_lower and 'lpg' in query_lower and 'deposits' in query_lower):
                result = _simulate_lpg_white_deposits_investigation(query, language, correlation_id)
            
            # Automotive LPG test requirements
            elif ('test requirements' in query_lower or 'requirements' in query_lower) and ('automotive lpg' in query_lower or 'lpg' in query_lower):
                result = _simulate_automotive_lpg_test_requirements(query, language, correlation_id)
            
            # VI Improver dosage for Quartz 9000
            elif (('viscosity index improver' in query_lower or 'vi improver' in query_lower) and 'dosage' in query_lower) or \
                 ('recommended' in query_lower and 'viscosity index improver' in query_lower and 'quartz 9000' in query_lower):
                result = _simulate_vi_improver_dosage_query(query, language, correlation_id)
            
            # Complete Quartz 9000 formulation
            elif ('recommended formulation' in query_lower or ('formulation' in query_lower and 'quartz 9000' in query_lower and 'recommended' in query_lower)):
                result = _simulate_quartz_9000_formulation(query, language, correlation_id)
            
            # Heavy-duty variant development
            elif ('develop' in query_lower and 'variant' in query_lower and 'heavy' in query_lower) or \
                 ('new variant' in query_lower and 'heavy-duty' in query_lower) or \
                 ('heavy-duty' in query_lower and 'quartz 9000' in query_lower):
                result = _simulate_heavy_duty_variant_development(query, language, correlation_id)
            
            # ZDDP inventory
            elif ('inventory levels' in query_lower or 'inventory' in query_lower or 'stock' in query_lower) and 'zddp' in query_lower:
                result = _simulate_zddp_inventory_query(query, language, correlation_id)
            
            # Gujarat suppliers
            elif ('approved suppliers' in query_lower or 'suppliers' in query_lower) and 'gujarat' in query_lower:
                result = _simulate_gujarat_suppliers_query(query, language, correlation_id)
            
            # LPG moisture specification
            elif ('moisture content specification' in query_lower or 'moisture' in query_lower) and 'lpg' in query_lower:
                result = _simulate_lpg_moisture_spec_query(query, language, correlation_id)
            
            # Supplier certifications
            elif 'certifications' in query_lower and 'suppliers' in query_lower:
                result = _simulate_supplier_certifications_query(query, language, correlation_id)
            
            # Quartz 7000 viscosity
            elif ('viscosity' in query_lower and 'quartz 7000' in query_lower) or \
                 ('100°c' in query_lower and 'quartz 7000' in query_lower):
                result = _simulate_quartz_7000_viscosity_query(query, language, correlation_id)
            
            # Existing handlers
            elif 'lims' in query_lower and 'batch' in query_lower and 'fail' in query_lower:
                result = _simulate_batch_failure_query(query, language, correlation_id)
            elif 'pao content' in query_lower or 'pao' in query_lower:
                result = _simulate_pao_content_query(query, language, correlation_id)
            elif 'testing phase' in query_lower or ('batch' in query_lower and 'testing' in query_lower):
                result = _simulate_testing_batches_query(query, language, correlation_id)
            elif 'formulation' in query_lower and 'trial' in query_lower:
                result = _simulate_formulation_trial_query(query, language, correlation_id)
            elif 'low stock' in query_lower or 'stock levels' in query_lower:
                result = _simulate_low_stock_query(query, language, correlation_id)
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


def _simulate_batch_failure_query(query, language, correlation_id):
    """Handle LIMS batch failure queries"""
    
    response_en = """**LIMS Batch QTZ-2025-0234 Investigation:**

**Batch Details:**
- Product: Quartz 9000 5W-30
- Test Date: March 15, 2025
- Analyst: Sneha Reddy

**Failed Parameters:**
- Viscosity @ 100°C: 11.3 cSt (Spec: 11.2-11.8 cSt) ✓
- Copper Content: 28 ppm (Spec: <25 ppm) ❌

**Root Cause:** Copper contamination from production line

**Immediate Actions:**
1. Batch quarantined - DO NOT SHIP
2. Production line cleaning required
3. Re-test after line clearance

**Impact:** 2,500L batch affected

**Source:** LIMS Test Database + Production Records"""

    response_hi = """**LIMS बैच QTZ-2025-0234 जांच:**

**बैच विवरण:**
- उत्पाद: Quartz 9000 5W-30
- परीक्षण दिनांक: 15 मार्च, 2025

**असफल पैरामीटर:**
- कॉपर सामग्री: 28 ppm (विनिर्देश: <25 ppm) ❌

**मूल कारण:** उत्पादन लाइन से कॉपर संदूषण

**तत्काल कार्य:**
1. बैच अलग किया गया
2. उत्पादन लाइन सफाई आवश्यक

**स्रोत:** LIMS परीक्षण डेटाबेस"""

    return {
        'category': 'quality_investigation',
        'agents': ['TestProtocolAgent', 'SupplyChainAgent'],
        'response': response_hi if language == 'hindi' else response_en,
        'sources': [
            {'type': 'LIMS', 'document': 'Batch Test Results QTZ-2025-0234'},
            {'type': 'Production', 'document': 'Line Contamination Report'}
        ],
        'processing_time_ms': random.randint(2500, 3500)
    }


def _simulate_pao_content_query(query, language, correlation_id):
    """Handle PAO content queries"""
    
    response_en = """**PAO Content in TotalEnergies Synthetic Lubricants:**

**Quartz 9000 5W-30 (Fully Synthetic):**
- PAO 4 cSt: 30% w/w
- Group III Base Oil: 50% w/w
- Total Synthetic Content: 80%

**PAO Specifications:**
- Viscosity Index: 130+ 
- Pour Point: -60°C
- Oxidation Stability: Excellent

**Supplier:** ExxonMobil SpectraSyn PAO
**Current Stock:** 150L (LOW STOCK ALERT)

**Benefits:**
- Superior low-temperature performance
- Extended drain intervals
- Reduced volatility

**Source:** Formulation Database + PLM Specs"""

    response_hi = """**TotalEnergies सिंथेटिक स्नेहन में PAO सामग्री:**

**Quartz 9000 5W-30 (पूर्ण सिंथेटिक):**
- PAO 4 cSt: 30% w/w
- Group III बेस ऑयल: 50% w/w
- कुल सिंथेटिक सामग्री: 80%

**आपूर्तिकर्ता:** ExxonMobil SpectraSyn PAO
**वर्तमान स्टॉक:** 150L (कम स्टॉक चेतावनी)

**लाभ:**
- बेहतर कम तापमान प्रदर्शन
- विस्तारित ड्रेन अंतराल

**स्रोत:** फॉर्मूलेशन डेटाबेस + PLM"""

    return {
        'category': 'formulation',
        'agents': ['FormulationAgent'],
        'response': response_hi if language == 'hindi' else response_en,
        'sources': [
            {'type': 'PLM', 'document': 'Quartz 9000 Formulation Spec'},
            {'type': 'SAP_ERP', 'document': 'PAO Inventory Status'}
        ],
        'processing_time_ms': random.randint(1800, 2800)
    }


def _simulate_testing_batches_query(query, language, correlation_id):
    """Handle testing phase batches query"""
    
    response_en = """**Batches Currently in Testing Phase:**

**Active Testing Trials:**

1. **HIPERF-T2025-005**
   - Product: Hi-Perf Moto 4T
   - Engineer: Amit Patel
   - Status: JASO MA2 testing
   - Expected: 2 weeks

2. **QTZ-7000-T2025-003** 
   - Product: Quartz 7000 10W-40
   - Engineer: Ravi Kumar
   - Status: Viscosity validation
   - Expected: 1 week

3. **LPG-T2025-008**
   - Product: LPG Domestic
   - Engineer: Meera Singh  
   - Status: Moisture content testing
   - Expected: 3 days

**Total Active Trials:** 3
**Average Testing Time:** 1-2 weeks

**Source:** Trial Management System + LIMS Queue"""

    response_hi = """**वर्तमान में परीक्षण चरण में बैच:**

**सक्रिय परीक्षण ट्रायल:**

1. **HIPERF-T2025-005**
   - उत्पाद: Hi-Perf Moto 4T
   - इंजीनियर: अमित पटेल
   - स्थिति: JASO MA2 परीक्षण

2. **QTZ-7000-T2025-003**
   - उत्पाद: Quartz 7000 10W-40
   - इंजीनियर: रवि कुमार

3. **LPG-T2025-008**
   - उत्पाद: LPG घरेलू
   - इंजीनियर: मीरा सिंह

**कुल सक्रिय ट्रायल:** 3

**स्रोत:** ट्रायल प्रबंधन सिस्टम"""

    return {
        'category': 'production_planning',
        'agents': ['TestProtocolAgent'],
        'response': response_hi if language == 'hindi' else response_en,
        'sources': [
            {'type': 'Trial_DB', 'document': 'Active Formulation Trials'},
            {'type': 'LIMS', 'document': 'Testing Queue Status'}
        ],
        'processing_time_ms': random.randint(1500, 2500)
    }


def _simulate_formulation_trial_query(query, language, correlation_id):
    """Handle specific formulation trial queries"""
    
    response_en = """**Complete Formulation - Trial QTZ-9000-T2025-001:**

**Trial Details:**
- Product Family: Quartz 9000
- Status: APPROVED ✅
- Engineer: Priya Sharma

**Base Oil Composition:**
- PAO 4 cSt: 30.0% w/w
- Group III 4 cSt: 50.0% w/w

**Additive Package:**
- ZDDP Anti-wear: 1.2% w/w
- PMA VI Improver: 9.0% w/w
- Dispersant Package: 8.5% w/w
- Anti-oxidant: 1.3% w/w

**Test Results:**
- Viscosity @ 100°C: 11.4 cSt ✅
- Viscosity Index: 168 ✅
- HTHS @ 150°C: 3.52 cP ✅

**Status:** Ready for production scale-up

**Source:** Formulation Trial Database + Lab Results"""

    response_hi = """**पूरा फॉर्मूलेशन - ट्रायल QTZ-9000-T2025-001:**

**ट्रायल विवरण:**
- उत्पाद परिवार: Quartz 9000
- स्थिति: अनुमोदित ✅
- इंजीनियर: प्रिया शर्मा

**बेस ऑयल संरचना:**
- PAO 4 cSt: 30.0% w/w
- Group III 4 cSt: 50.0% w/w

**एडिटिव पैकेज:**
- ZDDP एंटी-वियर: 1.2% w/w
- PMA VI सुधारक: 9.0% w/w

**परीक्षण परिणाम:**
- Viscosity @ 100°C: 11.4 cSt ✅

**स्थिति:** उत्पादन स्केल-अप के लिए तैयार

**स्रोत:** फॉर्मूलेशन ट्रायल डेटाबेस"""

    return {
        'category': 'process_development',
        'agents': ['FormulationAgent'],
        'response': response_hi if language == 'hindi' else response_en,
        'sources': [
            {'type': 'Trial_DB', 'document': 'QTZ-9000-T2025-001 Complete Record'},
            {'type': 'LIMS', 'document': 'Trial Test Results'}
        ],
        'processing_time_ms': random.randint(2000, 3000)
    }


def _simulate_low_stock_query(query, language, correlation_id):
    """Handle low stock level queries"""
    
    response_en = """**Materials with Low Stock Levels:**

**CRITICAL (< 50 units):**
1. **Anti-Wear Booster** 
   - Current Stock: 8 KG
   - Supplier: Afton Chemical
   - Lead Time: 21 days
   - **ACTION REQUIRED: Emergency procurement**

2. **Dispersant Package 8%**
   - Current Stock: 25 KG  
   - Supplier: Lubrizol India
   - Lead Time: 15 days

**LOW (< 200 units):**
3. **PAO 4 cSt Synthetic Base**
   - Current Stock: 150 L
   - Supplier: ExxonMobil
   - Price: ₹320/L

**Recommended Actions:**
1. Place emergency orders for critical items
2. Review safety stock levels
3. Consider alternative suppliers

**Source:** SAP ERP Inventory Management"""

    response_hi = """**कम स्टॉक स्तर वाली सामग्री:**

**महत्वपूर्ण (< 50 इकाइयां):**
1. **एंटी-वियर बूस्टर**
   - वर्तमान स्टॉक: 8 KG
   - आपूर्तिकर्ता: Afton Chemical
   - **कार्य आवश्यक: आपातकालीन खरीद**

2. **डिस्पर्सेंट पैकेज 8%**
   - वर्तमान स्टॉक: 25 KG
   - आपूर्तिकर्ता: Lubrizol India

**कम (< 200 इकाइयां):**
3. **PAO 4 cSt सिंथेटिक बेस**
   - वर्तमान स्टॉक: 150 L
   - मूल्य: ₹320/L

**अनुशंसित कार्य:**
1. महत्वपूर्ण वस्तुओं के लिए आपातकालीन ऑर्डर
2. सुरक्षा स्टॉक स्तरों की समीक्षा

**स्रोत:** SAP ERP इन्वेंट्री प्रबंधन"""

    return {
        'category': 'inventory_management',
        'agents': ['SupplyChainAgent'],
        'response': response_hi if language == 'hindi' else response_en,
        'sources': [
            {'type': 'SAP_ERP', 'document': 'Low Stock Alert Report'},
            {'type': 'Supplier_Portal', 'document': 'Lead Time Matrix'}
        ],
        'processing_time_ms': random.randint(1200, 2200)
    }


def _simulate_automotive_lpg_test_requirements(query, language, correlation_id):
    """Handle automotive LPG test requirements query"""
    
    response_en = """**Automotive LPG Test Requirements (PESO Standards):**

**Mandatory Tests:**
1. **Vapor Pressure Test**
   - Method: ASTM D6897
   - Requirement: 6-8 bar @ 20°C
   - Frequency: Every batch

2. **Propane Content Analysis**
   - Method: IS 4576 (GC Analysis)
   - Requirement: Minimum 95%
   - Frequency: Every batch

3. **Moisture Content**
   - Method: BIS 14861 (Karl Fischer)
   - Requirement: Maximum 30 ppm
   - Frequency: Every batch

4. **Sulfur Content**
   - Method: ASTM D5623
   - Requirement: < 120 ppm
   - Frequency: Weekly

**Additional QC Tests:**
- Evaporation residue: < 0.05 mL/100mL
- Free water: Nil
- Corrosive sulfur: Non-corrosive

**Compliance:** PESO 2016 Standards

**Source:** PESO LPG Quality Control Protocol"""

    response_hi = """**ऑटोमोटिव LPG परीक्षण आवश्यकताएं (PESO मानक):**

**अनिवार्य परीक्षण:**
1. **वाष्प दबाव परीक्षण**
   - विधि: ASTM D6897
   - आवश्यकता: 6-8 बार @ 20°C
   - आवृत्ति: प्रत्येक बैच

2. **प्रोपेन सामग्री विश्लेषण**
   - विधि: IS 4576 (GC विश्लेषण)
   - आवश्यकता: न्यूनतम 95%
   - आवृत्ति: प्रत्येक बैच

3. **नमी सामग्री**
   - विधि: BIS 14861 (Karl Fischer)
   - आवश्यकता: अधिकतम 30 ppm
   - आवृत्ति: प्रत्येक बैच

**अतिरिक्त QC परीक्षण:**
- वाष्पीकरण अवशेष: < 0.05 mL/100mL
- मुक्त पानी: शून्य

**अनुपालन:** PESO 2016 मानक

**स्रोत:** PESO LPG गुणवत्ता नियंत्रण प्रोटोकॉल"""

    return {
        'category': 'test_protocol',
        'agents': ['TestProtocolAgent'],
        'response': response_hi if language == 'hindi' else response_en,
        'sources': [
            {'type': 'Regulatory_DB', 'document': 'PESO LPG Quality Control Protocol'},
            {'type': 'Test_Methods', 'document': 'ASTM D6897, IS 4576, BIS 14861'}
        ],
        'processing_time_ms': random.randint(1800, 2500)
    }


def _simulate_vi_improver_dosage_query(query, language, correlation_id):
    """Handle VI improver dosage query for Quartz 9000 5W-30"""
    
    response_en = """**VI Improver Dosage for Quartz 9000 5W-30:**

**Recommended Dosage:** 8.5-9.2% w/w PMA (Polymethacrylate)

**Technical Specifications:**
- Target Viscosity: 11.2-11.8 cSt @ 100°C
- Viscosity Index: 168 (minimum)
- HTHS @ 150°C: 3.5 cP
- Shear Stability: SSI < 30

**Formulation Details:**
- PMA VI Improver: 9.0% w/w (optimal)
- Base Oil Blend: PAO 4 cSt (30%) + Group III 4 cSt (50%)
- Other Additives: 11% w/w

**API SP Requirements Met:**
✓ LSPI prevention capability
✓ Timing chain wear protection
✓ Extended drain interval performance

**Quality Control:**
- Monitor shear stability during mixing
- Verify viscosity targets before packaging

**Source:** Quartz 9000 5W-30 Formulation Spec Rev 3.2"""

    response_hi = """**Quartz 9000 5W-30 के लिए VI Improver मात्रा:**

**अनुशंसित मात्रा:** 8.5-9.2% w/w PMA (Polymethacrylate)

**तकनीकी विनिर्देश:**
- लक्ष्य Viscosity: 11.2-11.8 cSt @ 100°C
- Viscosity Index: 168 (न्यूनतम)
- HTHS @ 150°C: 3.5 cP

**फॉर्मूलेशन विवरण:**
- PMA VI Improver: 9.0% w/w (इष्टतम)
- बेस ऑयल ब्लेंड: PAO 4 cSt (30%) + Group III 4 cSt (50%)

**API SP आवश्यकताएं:**
✓ LSPI रोकथाम क्षमता
✓ Timing chain wear सुरक्षा
✓ विस्तारित ड्रेन अंतराल प्रदर्शन

**गुणवत्ता नियंत्रण:**
- मिश्रण के दौरान shear stability की निगरानी
- पैकेजिंग से पहले viscosity लक्ष्यों की पुष्टि

**स्रोत:** Quartz 9000 5W-30 फॉर्मूलेशन स्पेक Rev 3.2"""

    return {
        'category': 'formulation',
        'agents': ['FormulationAgent'],
        'response': response_hi if language == 'hindi' else response_en,
        'sources': [
            {'type': 'PLM', 'document': 'Quartz 9000 5W-30 Formulation Spec Rev 3.2'},
            {'type': 'Trial_DB', 'document': 'QTZ-9000-T2025-001 Results'}
        ],
        'processing_time_ms': random.randint(1500, 2200)
    }


def _simulate_quartz_9000_formulation(query, language, correlation_id):
    """Handle Quartz 9000 5W-30 formulation query"""
    
    response_en = """**Recommended Formulation - Quartz 9000 5W-30:**

**Base Oil Composition (80.0%):**
- PAO 4 cSt: 30.0% w/w (Synthetic base oil)
- Group III 4 cSt: 50.0% w/w (High VI base oil)

**Additive Package (20.0%):**
- PMA VI Improver: 9.0% w/w
- ZDDP Anti-wear: 1.2% w/w
- Dispersant/Detergent: 6.5% w/w
- Anti-oxidant: 1.3% w/w
- Pour Point Depressant: 0.8% w/w
- Anti-foam: 1.2% w/w

**Target Properties:**
- Kinematic Viscosity @ 100°C: 11.2-11.8 cSt
- Kinematic Viscosity @ 40°C: 61-67 cSt
- Viscosity Index: 168 min
- HTHS @ 150°C: 3.5 cP min
- Flash Point: 230°C min
- Pour Point: -42°C max

**Performance Standards:**
✓ API SP, ILSAC GF-6A
✓ ACEA A3/B4
✓ OEM approvals: GM dexos1 Gen 3

**Manufacturing Notes:**
- Mix temperature: 60-80°C
- Homogenization time: 45 minutes
- Filter to 10 microns

**Source:** Formulation Database QTZ-9000-FORM-Rev3.2"""

    response_hi = """**अनुशंसित फॉर्मूलेशन - Quartz 9000 5W-30:**

**बेस ऑयल संरचना (80.0%):**
- PAO 4 cSt: 30.0% w/w (सिंथेटिक बेस ऑयल)
- Group III 4 cSt: 50.0% w/w (उच्च VI बेस ऑयल)

**एडिटिव पैकेज (20.0%):**
- PMA VI सुधारक: 9.0% w/w
- ZDDP एंटी-वियर: 1.2% w/w
- डिस्पर्सेंट/डिटर्जेंट: 6.5% w/w
- एंटी-ऑक्सीडेंट: 1.3% w/w

**लक्ष्य गुण:**
- Kinematic Viscosity @ 100°C: 11.2-11.8 cSt
- Viscosity Index: 168 न्यूनतम
- HTHS @ 150°C: 3.5 cP न्यूनतम
- Flash Point: 230°C न्यूनतम

**प्रदर्शन मानक:**
✓ API SP, ILSAC GF-6A
✓ ACEA A3/B4
✓ OEM अनुमोदन: GM dexos1 Gen 3

**निर्माण नोट्स:**
- मिश्रण तापमान: 60-80°C
- समरूपीकरण समय: 45 मिनट

**स्रोत:** फॉर्मूलेशन डेटाबेस QTZ-9000-FORM-Rev3.2"""

    return {
        'category': 'formulation',
        'agents': ['FormulationAgent'],
        'response': response_hi if language == 'hindi' else response_en,
        'sources': [
            {'type': 'PLM', 'document': 'Quartz 9000 5W-30 Formulation Spec Rev 3.2'},
            {'type': 'Standards_DB', 'document': 'API SP, ILSAC GF-6A Requirements'}
        ],
        'processing_time_ms': random.randint(2000, 3000)
    }


def _simulate_heavy_duty_variant_development(query, language, correlation_id):
    """Handle heavy-duty variant development query"""
    
    response_en = """**Development Plan: Quartz 9000 5W-30 Heavy-Duty Variant**

**Proposed Product:** Quartz 9000 HD 5W-30

**Enhanced Requirements for Heavy-Duty:**
- Extended drain intervals: 25,000 km
- Higher soot handling capability
- Enhanced wear protection for commercial engines
- Superior oxidation resistance

**Modified Formulation:**
- Base oils: Same as standard (PAO + Group III)
- **Enhanced Additives:**
  - ZDDP Anti-wear: 1.8% w/w (vs 1.2% standard)
  - Dispersant Package: 12.0% w/w (vs 6.5% standard)
  - Anti-oxidant: 2.1% w/w (vs 1.3% standard)
  - TBN Booster: 1.5% w/w (new addition)

**Target Performance Standards:**
✓ API CK-4 (Heavy-Duty Diesel)
✓ ACEA E9 (European Heavy-Duty)
✓ Volvo VDS-4.5, Mack EOS-4.5
✓ Caterpillar ECF-3, Cummins CES 20086

**Development Timeline:**
- Week 1-2: Formulation trials (3 variants)
- Week 3-4: Engine testing (Mack T-13, Volvo D13)
- Week 5-6: Field trials with fleet customers
- Week 7-8: OEM approval submissions

**Investment Required:**
- R&D: ₹15 lakhs
- Engine testing: ₹25 lakhs
- Field trials: ₹8 lakhs

**Market Potential:**
- Commercial vehicle segment: 15% premium pricing
- Expected volume: 2,000 MT/year

**Next Steps:**
1. Prepare detailed project proposal
2. Get management approval for budget
3. Schedule lab trials with enhanced additive packages

**Source:** Heavy-Duty Engine Oil Development Guide"""

    response_hi = """**विकास योजना: Quartz 9000 5W-30 हेवी-ड्यूटी वेरिएंट**

**प्रस्तावित उत्पाद:** Quartz 9000 HD 5W-30

**हेवी-ड्यूटी के लिए संवर्धित आवश्यकताएं:**
- विस्तारित ड्रेन अंतराल: 25,000 किमी
- उच्च soot हैंडलिंग क्षमता
- वाणिज्यिक इंजनों के लिए बेहतर wear सुरक्षा
- श्रेष्ठ ऑक्सीकरण प्रतिरोध

**संशोधित फॉर्मूलेशन:**
- बेस ऑयल: मानक के समान (PAO + Group III)
- **संवर्धित एडिटिव्स:**
  - ZDDP एंटी-वियर: 1.8% w/w (मानक 1.2% बनाम)
  - डिस्पर्सेंट पैकेज: 12.0% w/w (मानक 6.5% बनाम)
  - एंटी-ऑक्सीडेंट: 2.1% w/w (मानक 1.3% बनाम)
  - TBN बूस्टर: 1.5% w/w (नया अतिरिक्त)

**लक्ष्य प्रदर्शन मानक:**
✓ API CK-4 (हेवी-ड्यूटी डीजल)
✓ ACEA E9 (यूरोपीय हेवी-ड्यूटी)
✓ Volvo VDS-4.5, Mack EOS-4.5

**विकास समयरेखा:**
- सप्ताह 1-2: फॉर्मूलेशन ट्रायल (3 वेरिएंट)
- सप्ताह 3-4: इंजन परीक्षण
- सप्ताह 5-6: ग्राहकों के साथ फील्ड ट्रायल
- सप्ताह 7-8: OEM अनुमोदन सबमिशन

**आवश्यक निवेश:**
- R&D: ₹15 लाख
- इंजन परीक्षण: ₹25 लाख
- फील्ड ट्रायल: ₹8 लाख

**बाजार क्षमता:**
- वाणिज्यिक वाहन खंड: 15% प्रीमियम मूल्य निर्धारण
- अपेक्षित मात्रा: 2,000 MT/वर्ष

**अगले कदम:**
1. विस्तृत प्रोजेक्ट प्रस्ताव तैयार करें
2. बजट के लिए प्रबंधन की अनुमति लें
3. संवर्धित एडिटिव पैकेज के साथ लैब ट्रायल शेड्यूल करें

**स्रोत:** हेवी-ड्यूटी इंजन ऑयल डेवलपमेंट गाइड"""

    return {
        'category': 'product_development',
        'agents': ['FormulationAgent', 'ProductDevelopmentAgent'],
        'response': response_hi if language == 'hindi' else response_en,
        'sources': [
            {'type': 'Product_Guide', 'document': 'Heavy-Duty Engine Oil Development Guide'},
            {'type': 'Market_Analysis', 'document': 'Commercial Vehicle Lubricants Market Report'}
        ],
        'processing_time_ms': random.randint(3000, 4000)
    }


def _simulate_zddp_inventory_query(query, language, correlation_id):
    """Handle ZDDP inventory query"""
    
    response_en = """**ZDDP Anti-wear Package Inventory Status:**

**Current Stock Level:**
- Material Code: ADDPKG-ZDDP-SP
- Material Name: ZDDP Anti-wear Package
- Current Quantity: 1,200 KG
- Location: Mumbai Plant Warehouse

**Stock Analysis:**
- Monthly Consumption: 800 KG
- Current Stock Days: 45 days supply
- Safety Stock Level: 400 KG
- **Status:** ADEQUATE ✅

**Supplier Information:**
- Primary Supplier: Lubrizol India
- Lead Time: 15 days
- Unit Price: ₹450.00/KG
- Last Purchase: March 2025

**Usage Breakdown:**
- Quartz 9000 5W-30: 60% (480 KG/month)
- Quartz 7000 10W-40: 25% (200 KG/month)
- Other products: 15% (120 KG/month)

**Procurement Recommendation:**
- Next order due: April 15, 2025
- Recommended quantity: 1,000 KG
- Total value: ₹4,50,000

**Quality Status:**
- Last QC check: March 10, 2025
- Certificate: Valid until Dec 2025
- Purity: 98.5% (meets spec)

**Source:** SAP ERP Inventory Management System"""

    response_hi = """**ZDDP एंटी-वियर पैकेज इन्वेंट्री स्थिति:**

**वर्तमान स्टॉक स्तर:**
- मैटेरियल कोड: ADDPKG-ZDDP-SP
- मैटेरियल नाम: ZDDP एंटी-वियर पैकेज
- वर्तमान मात्रा: 1,200 KG
- स्थान: मुंबई प्लांट वेयरहाउस

**स्टॉक विश्लेषण:**
- मासिक खपत: 800 KG
- वर्तमान स्टॉक दिन: 45 दिन की आपूर्ति
- सुरक्षा स्टॉक स्तर: 400 KG
- **स्थिति:** पर्याप्त ✅

**आपूर्तिकर्ता जानकारी:**
- प्राथमिक आपूर्तिकर्ता: Lubrizol India
- लीड टाइम: 15 दिन
- यूनिट मूल्य: ₹450.00/KG
- अंतिम खरीदारी: मार्च 2025

**उपयोग विवरण:**
- Quartz 9000 5W-30: 60% (480 KG/महीना)
- Quartz 7000 10W-40: 25% (200 KG/महीना)
- अन्य उत्पाद: 15% (120 KG/महीना)

**खरीद सिफारिश:**
- अगला ऑर्डर देय: 15 अप्रैल, 2025
- अनुशंसित मात्रा: 1,000 KG
- कुल मूल्य: ₹4,50,000

**गुणवत्ता स्थिति:**
- अंतिम QC जांच: 10 मार्च, 2025
- प्रमाणपत्र: दिसंबर 2025 तक वैध
- शुद्धता: 98.5% (स्पेक के अनुकूल)

**स्रोत:** SAP ERP इन्वेंट्री प्रबंधन सिस्टम"""

    return {
        'category': 'inventory_management',
        'agents': ['SupplyChainAgent'],
        'response': response_hi if language == 'hindi' else response_en,
        'sources': [
            {'type': 'SAP_ERP', 'document': 'Material Master ADDPKG-ZDDP-SP'},
            {'type': 'Consumption_Report', 'document': 'Monthly Usage Analysis'}
        ],
        'processing_time_ms': random.randint(1200, 1800)
    }


def _simulate_gujarat_suppliers_query(query, language, correlation_id):
    """Handle Gujarat suppliers query"""
    
    response_en = """**Approved Suppliers in Gujarat Region:**

**1. Nayara Energy (Vadinar)**
- Materials: Group III Base Oil
- Quality Rating: 4.5/5.0 ⭐⭐⭐⭐⭐
- Lead Time: 10 days
- Certifications: ISO 9001, API Group III
- Monthly Capacity: 5,000 MT
- **Status:** ACTIVE ✅

**2. Reliance Industries (Jamnagar)**
- Materials: Group III Base Oil, Group II Base Oil
- Quality Rating: 4.7/5.0 ⭐⭐⭐⭐⭐
- Lead Time: 8 days
- Certifications: ISO 9001, API Group III, REACH
- Monthly Capacity: 12,000 MT
- **Status:** ACTIVE ✅

**3. Indian Oil Corporation (Gujarat Refinery)**
- Materials: Group III Base Oil, LPG
- Quality Rating: 4.6/5.0 ⭐⭐⭐⭐⭐
- Lead Time: 12 days
- Certifications: ISO 9001, BIS
- Monthly Capacity: 8,000 MT
- **Status:** ACTIVE ✅

**4. Gujarat State Petronet Ltd**
- Materials: LPG, Industrial Gas
- Quality Rating: 4.4/5.0 ⭐⭐⭐⭐
- Lead Time: 5 days
- Certifications: ISO 9001, PESO, BIS
- Monthly Capacity: 3,000 MT
- **Status:** ACTIVE ✅

**Total Gujarat Suppliers:** 4 approved
**Combined Monthly Capacity:** 28,000 MT
**Average Lead Time:** 8.75 days
**Average Quality Rating:** 4.55/5.0

**Logistics Advantage:**
- Proximity to major ports (Kandla, JNPT)
- Well-developed road/rail connectivity
- Lower transportation costs
- Strategic location for Western India distribution

**Source:** Supplier Master Database + Vendor Portal"""

    response_hi = """**गुजरात क्षेत्र में अनुमोदित आपूर्तिकर्ता:**

**1. नयारा एनर्जी (वाडिनार)**
- सामग्री: Group III बेस ऑयल
- गुणवत्ता रेटिंग: 4.5/5.0 ⭐⭐⭐⭐⭐
- लीड टाइम: 10 दिन
- प्रमाणन: ISO 9001, API Group III
- मासिक क्षमता: 5,000 MT
- **स्थिति:** सक्रिय ✅

**2. रिलायंस इंडस्ट्रीज (जामनगर)**
- सामग्री: Group III बेस ऑयल, Group II बेस ऑयल
- गुणवत्ता रेटिंग: 4.7/5.0 ⭐⭐⭐⭐⭐
- लीड टाइम: 8 दिन
- प्रमाणन: ISO 9001, API Group III, REACH
- मासिक क्षमता: 12,000 MT
- **स्थिति:** सक्रिय ✅

**3. इंडियन ऑयल कॉर्पोरेशन (गुजरात रिफाइनरी)**
- सामग्री: Group III बेस ऑयल, LPG
- गुणवत्ता रेटिंग: 4.6/5.0 ⭐⭐⭐⭐⭐
- लीड टाइम: 12 दिन
- प्रमाणन: ISO 9001, BIS
- मासिक क्षमता: 8,000 MT
- **स्थिति:** सक्रिय ✅

**4. गुजरात स्टेट पेट्रोनेट लिमिटेड**
- सामग्री: LPG, औद्योगिक गैस
- गुणवत्ता रेटिंग: 4.4/5.0 ⭐⭐⭐⭐
- लीड टाइम: 5 दिन
- प्रमाणन: ISO 9001, PESO, BIS
- मासिक क्षमता: 3,000 MT
- **स्थिति:** सक्रिय ✅

**कुल गुजरात आपूर्तिकर्ता:** 4 अनुमोदित
**संयुक्त मासिक क्षमता:** 28,000 MT
**औसत लीड टाइम:** 8.75 दिन
**औसत गुणवत्ता रेटिंग:** 4.55/5.0

**लॉजिस्टिक्स लाभ:**
- प्रमुख बंदरगाहों से निकटता (कांडला, JNPT)
- अच्छी तरह से विकसित सड़क/रेल कनेक्टिविटी
- कम परिवहन लागत
- पश्चिमी भारत वितरण के लिए रणनीतिक स्थान

**स्रोत:** आपूर्तिकर्ता मास्टर डेटाबेस + वेंडर पोर्टल"""

    return {
        'category': 'supplier_management',
        'agents': ['SupplyChainAgent'],
        'response': response_hi if language == 'hindi' else response_en,
        'sources': [
            {'type': 'Supplier_DB', 'document': 'Gujarat Region Approved Vendor List'},
            {'type': 'Quality_System', 'document': 'Supplier Quality Ratings'}
        ],
        'processing_time_ms': random.randint(1500, 2200)
    }


def _simulate_lpg_moisture_spec_query(query, language, correlation_id):
    """Handle LPG moisture content specification query"""
    
    response_en = """**LPG Moisture Content Specifications:**

**Domestic LPG (Cooking Gas):**
- Maximum Moisture: 50 ppm
- Test Method: BIS 14861 (Karl Fischer Titration)
- Frequency: Every batch
- Typical Range: 15-35 ppm
- **Current Status:** All batches compliant ✅

**Automotive LPG:**
- Maximum Moisture: 30 ppm (stricter requirement)
- Test Method: ASTM D2713 / BIS 14861
- Frequency: Every batch
- Typical Range: 10-25 ppm
- **Current Status:** All batches compliant ✅

**Industrial LPG:**
- Maximum Moisture: 40 ppm
- Test Method: BIS 14861
- Frequency: Every batch

**Why Moisture Control is Critical:**
1. **Corrosion Prevention:** Prevents internal corrosion of cylinders and pipelines
2. **Flow Assurance:** Prevents ice formation in regulators at low temperatures
3. **Quality Consistency:** Ensures consistent combustion characteristics
4. **Regulatory Compliance:** Meets PESO and BIS standards

**Quality Control Process:**
- Incoming raw material testing
- In-process monitoring during filling
- Final batch release testing
- Monthly trending analysis

**Recent Test Results (March 2025):**
- Batch LPG-DOM-2025-0312: **180 ppm FAILED** ❌
  - Root cause: Moisture ingress during storage
  - Corrective action: Enhanced nitrogen blanketing
  - Status: Corrected in subsequent batches

**Specification References:**
- BIS 14861: Moisture determination in LPG by Karl Fischer method
- PESO Order: LPG quality standards for domestic use
- IS 4576: LPG composition and quality requirements

**Source:** LPG Moisture Content Specification Document"""

    response_hi = """**LPG नमी सामग्री विनिर्देश:**

**घरेलू LPG (खाना पकाने की गैस):**
- अधिकतम नमी: 50 ppm
- परीक्षण विधि: BIS 14861 (Karl Fischer Titration)
- आवृत्ति: प्रत्येक बैच
- सामान्य रेंज: 15-35 ppm
- **वर्तमान स्थिति:** सभी बैच अनुपालित ✅

**ऑटोमोटिव LPG:**
- अधिकतम नमी: 30 ppm (सख्त आवश्यकता)
- परीक्षण विधि: ASTM D2713 / BIS 14861
- आवृत्ति: प्रत्येक बैच
- सामान्य रेंज: 10-25 ppm
- **वर्तमान स्थिति:** सभी बैच अनुपालित ✅

**औद्योगिक LPG:**
- अधिकतम नमी: 40 ppm
- परीक्षण विधि: BIS 14861
- आवृत्ति: प्रत्येक बैच

**नमी नियंत्रण क्यों महत्वपूर्ण है:**
1. **संक्षारण रोकथाम:** सिलेंडर और पाइपलाइन के आंतरिक संक्षारण को रोकता है
2. **प्रवाह आश्वासन:** कम तापमान पर नियामकों में बर्फ बनने से रोकता है
3. **गुणवत्ता स्थिरता:** लगातार दहन विशेषताओं को सुनिश्चित करता है
4. **नियामक अनुपालन:** PESO और BIS मानकों को पूरा करता है

**गुणवत्ता नियंत्रण प्रक्रिया:**
- आने वाली कच्ची सामग्री परीक्षण
- भरने के दौरान इन-प्रोसेस निगरानी
- अंतिम बैच रिलीज परीक्षण
- मासिक ट्रेंडिंग विश्लेषण

**हाल के परीक्षण परिणाम (मार्च 2025):**
- बैच LPG-DOM-2025-0312: **180 ppm असफल** ❌
  - मूल कारण: भंडारण के दौरान नमी प्रवेश
  - सुधारात्मक कार्य: संवर्धित नाइट्रोजन ब्लैंकेटिंग
  - स्थिति: बाद के बैचों में सुधारा गया

**विनिर्देश संदर्भ:**
- BIS 14861: Karl Fischer विधि द्वारा LPG में नमी निर्धारण
- PESO आदेश: घरेलू उपयोग के लिए LPG गुणवत्ता मानक
- IS 4576: LPG संरचना और गुणवत्ता आवश्यकताएं

**स्रोत:** LPG नमी सामग्री विनिर्देश दस्तावेज"""

    return {
        'category': 'product_specification',
        'agents': ['QualityControlAgent'],
        'response': response_hi if language == 'hindi' else response_en,
        'sources': [
            {'type': 'Product_Spec', 'document': 'LPG Moisture Content Specification'},
            {'type': 'LIMS', 'document': 'Recent Moisture Test Results'},
            {'type': 'Standards_DB', 'document': 'BIS 14861, PESO Standards'}
        ],
        'processing_time_ms': random.randint(1800, 2500)
    }


def _simulate_supplier_certifications_query(query, language, correlation_id):
    """Handle supplier certifications query"""
    
    response_en = """**Supplier Certifications Overview:**

**Quality Management Systems:**
- **ISO 9001:2015** - 7 suppliers (100% coverage)
  - Latest audits: Q4 2024
  - All certificates valid until 2026-2027
  - No major non-conformances

**Environmental & Safety:**
- **ISO 14001** (Environmental) - 5 suppliers
- **ISO 45001** (Safety) - 4 suppliers
- **REACH Compliance** - 3 suppliers (EU regulations)

**Industry-Specific Certifications:**

**Base Oil Suppliers:**
- **API Group III Certification**
  - Nayara Energy ✅
  - Reliance Industries ✅
  - Indian Oil Corporation ❌ (Group II only)

**Additive Suppliers:**
- **REACH Registration** (Lubrizol India, Evonik India)
- **FDA Approval** (Evonik India - food grade additives)
- **OEM Approvals** (Lubrizol - GM, Ford, VW specifications)

**LPG Suppliers:**
- **PESO License** (Gujarat State Petronet)
- **BIS Certification** (All LPG suppliers)
- **SMPV License** (Storage & handling certification)

**Regulatory Compliance:**
- **BIS Certification** - 6 suppliers
- **PESO Approval** - 2 suppliers (LPG related)
- **Customs AEO Status** - 3 suppliers (trade facilitation)

**Supplier Audit Status:**
- Last comprehensive audit: Jan-Feb 2025
- Next audit cycle: Jan-Feb 2026
- Risk rating: All suppliers rated "Low" or "Medium"
- No suppliers in "High" risk category

**Certificate Validity Tracking:**
- All certificates monitored in Supplier Portal
- Automated alerts 90 days before expiry
- 100% certificate validity maintained

**Compliance Score:**
- Overall compliance: 98.5%
- Quality systems: 100%
- Safety compliance: 95%
- Environmental compliance: 96%

**Recent Updates:**
- Afton Chemical renewed ISO 9001 (Feb 2025)
- Evonik India added ISO 45001 (March 2025)
- Lubrizol India updated REACH registration (March 2025)

**Source:** Supplier Management System + Quality Portal"""

    response_hi = """**आपूर्तिकर्ता प्रमाणन अवलोकन:**

**गुणवत्ता प्रबंधन प्रणाली:**
- **ISO 9001:2015** - 7 आपूर्तिकर्ता (100% कवरेज)
  - नवीनतम ऑडिट: Q4 2024
  - सभी प्रमाणपत्र 2026-2027 तक वैध
  - कोई प्रमुख गैर-अनुपालन नहीं

**पर्यावरण और सुरक्षा:**
- **ISO 14001** (पर्यावरणीय) - 5 आपूर्तिकर्ता
- **ISO 45001** (सुरक्षा) - 4 आपूर्तिकर्ता
- **REACH अनुपालन** - 3 आपूर्तिकर्ता (EU नियम)

**उद्योग-विशिष्ट प्रमाणन:**

**बेस ऑयल आपूर्तिकर्ता:**
- **API Group III प्रमाणन**
  - नयारा एनर्जी ✅
  - रिलायंस इंडस्ट्रीज ✅
  - इंडियन ऑयल कॉर्पोरेशन ❌ (केवल Group II)

**एडिटिव आपूर्तिकर्ता:**
- **REACH पंजीकरण** (Lubrizol India, Evonik India)
- **FDA अनुमोदन** (Evonik India - खाद्य ग्रेड additives)
- **OEM अनुमोदन** (Lubrizol - GM, Ford, VW विनिर्देश)

**LPG आपूर्तिकर्ता:**
- **PESO लाइसेंस** (Gujarat State Petronet)
- **BIS प्रमाणन** (सभी LPG आपूर्तिकर्ता)
- **SMPV लाइसेंस** (भंडारण और हैंडलिंग प्रमाणन)

**नियामक अनुपालन:**
- **BIS प्रमाणन** - 6 आपूर्तिकर्ता
- **PESO अनुमोदन** - 2 आपूर्तिकर्ता (LPG संबंधित)
- **कस्टम्स AEO स्टेटस** - 3 आपूर्तिकर्ता (व्यापार सुविधा)

**आपूर्तिकर्ता ऑडिट स्थिति:**
- अंतिम व्यापक ऑडिट: जन-फरवरी 2025
- अगला ऑडिट चक्र: जन-फरवरी 2026
- जोखिम रेटिंग: सभी आपूर्तिकर्ता "कम" या "मध्यम" रेटेड
- कोई आपूर्तिकर्ता "उच्च" जोखिम श्रेणी में नहीं

**प्रमाणपत्र वैधता ट्रैकिंग:**
- सभी प्रमाणपत्रों की निगरानी आपूर्तिकर्ता पोर्टल में
- समाप्ति से 90 दिन पहले स्वचालित अलर्ट
- 100% प्रमाणपत्र वैधता बनाए रखी गई

**अनुपालन स्कोर:**
- समग्र अनुपालन: 98.5%
- गुणवत्ता प्रणाली: 100%
- सुरक्षा अनुपालन: 95%
- पर्यावरणीय अनुपालन: 96%

**हाल के अपडेट:**
- Afton Chemical ने ISO 9001 नवीनीकृत किया (फरवरी 2025)
- Evonik India ने ISO 45001 जोड़ा (मार्च 2025)
- Lubrizol India ने REACH पंजीकरण अपडेट किया (मार्च 2025)

**स्रोत:** आपूर्तिकर्ता प्रबंधन सिस्टम + गुणवत्ता पोर्टल"""

    return {
        'category': 'supplier_management',
        'agents': ['SupplyChainAgent', 'QualityControlAgent'],
        'response': response_hi if language == 'hindi' else response_en,
        'sources': [
            {'type': 'Supplier_Portal', 'document': 'Certification Status Dashboard'},
            {'type': 'Quality_System', 'document': 'Audit Reports & Compliance Matrix'}
        ],
        'processing_time_ms': random.randint(2000, 2800)
    }


def _simulate_quartz_7000_viscosity_query(query, language, correlation_id):
    """Handle Quartz 7000 10W-40 viscosity query"""
    
    response_en = """**Quartz 7000 10W-40 Viscosity at 100°C:**

**Specification:** 14.2 cSt @ 100°C

**Target Range:** 14.0 - 15.5 cSt @ 100°C
**Typical Value:** 14.2 cSt @ 100°C
**SAE Grade:** 10W-40 (meets SAE J300 requirements)

**Product Details:**
- Product Code: QTZ-7000-10W40
- Grade: Semi-Synthetic Engine Oil
- Market Segment: Mid-tier passenger cars

**Base Oil Composition:**
- Group II Base Oil: 60% w/w
- Group III Base Oil: 25% w/w
- VI Improver: 8% w/w
- Additives: 7% w/w

**Viscosity Profile:**
- Kinematic Viscosity @ 40°C: 95-105 cSt
- Kinematic Viscosity @ 100°C: 14.0-15.5 cSt
- Viscosity Index: 155 (minimum)
- HTHS @ 150°C: 3.7 cP (minimum)

**Quality Control:**
- Test Method: ASTM D445 (Kinematic Viscosity)
- Test Frequency: Every batch
- Last Batch Result: 14.1 cSt ✅ (within specification)

**Performance Standards:**
✓ API SN Plus
✓ ACEA A3/B4
✓ Meets major OEM requirements

**Manufacturing Location:** Mumbai Blending Plant
**Batch Size:** 50,000 liters typical
**Monthly Production:** 800,000 liters

**Recent Quality Trends:**
- Average viscosity (last 10 batches): 14.18 cSt
- Standard deviation: 0.08 cSt
- All batches within specification ✅
- Process capability: Cpk = 2.1 (excellent)

**Source:** Quartz 7000 10W-40 Technical Specification Rev 2.1"""

    response_hi = """**Quartz 7000 10W-40 का 100°C पर Viscosity:**

**विनिर्देश:** 14.2 cSt @ 100°C

**लक्ष्य रेंज:** 14.0 - 15.5 cSt @ 100°C
**सामान्य मान:** 14.2 cSt @ 100°C
**SAE ग्रेड:** 10W-40 (SAE J300 आवश्यकताओं को पूरा करता है)

**उत्पाद विवरण:**
- उत्पाद कोड: QTZ-7000-10W40
- ग्रेड: सेमी-सिंथेटिक इंजन ऑयल
- बाजार खंड: मध्यम स्तरीय यात्री कारें

**बेस ऑयल संरचना:**
- Group II बेस ऑयल: 60% w/w
- Group III बेस ऑयल: 25% w/w
- VI इम्प्रूवर: 8% w/w
- एडिटिव्स: 7% w/w

**Viscosity प्रोफाइल:**
- Kinematic Viscosity @ 40°C: 95-105 cSt  
- Kinematic Viscosity @ 100°C: 14.0-15.5 cSt
- Viscosity Index: 155 (न्यूनतम)
- HTHS @ 150°C: 3.7 cP (न्यूनतम)

**गुणवत्ता नियंत्रण:**
- परीक्षण विधि: ASTM D445 (Kinematic Viscosity)
- परीक्षण आवृत्ति: प्रत्येक बैच
- अंतिम बैच परिणाम: 14.1 cSt ✅ (विनिर्देश के भीतर)

**प्रदर्शन मानक:**
✓ API SN Plus
✓ ACEA A3/B4
✓ प्रमुख OEM आवश्यकताओं को पूरा करता है

**निर्माण स्थान:** मुंबई ब्लेंडिंग प्लांट
**बैच आकार:** सामान्यतः 50,000 लीटर
**मासिक उत्पादन:** 800,000 लीटर

**हालिया गुणवत्ता रुझान:**
- औसत viscosity (अंतिम 10 बैच): 14.18 cSt
- मानक विचलन: 0.08 cSt
- सभी बैच विनिर्देश के भीतर ✅
- प्रक्रिया क्षमता: Cpk = 2.1 (उत्कृष्ट)

**स्रोत:** Quartz 7000 10W-40 तकनीकी विनिर्देश Rev 2.1"""

    return {
        'category': 'product_specification',
        'agents': ['QualityControlAgent'],
        'response': response_hi if language == 'hindi' else response_en,
        'sources': [
            {'type': 'Product_Spec', 'document': 'Quartz 7000 10W-40 Technical Specification Rev 2.1'},
            {'type': 'LIMS', 'document': 'Recent Batch Test Results'},
            {'type': 'Quality_Trends', 'document': 'Viscosity Control Chart Analysis'}
        ],
        'processing_time_ms': random.randint(1500, 2200)
    }


def _simulate_zddp_bs_vi_compliance_query(query, language, correlation_id):
    """Handle ZDDP reduction for BS VI compliance query"""
    
    response_en = """**ZDDP Reduction for BS VI Compliance Analysis:**

**Current ZDDP Levels:**
- Standard Engine Oil: 1.2% w/w ZDDP (0.12% phosphorus)
- BS VI Requirement: ≤0.08% phosphorus maximum

**Technical Assessment:**
**✅ FEASIBLE - Conditional Reduction to 0.08% P**

**Formulation Strategy:**
1. **Reduce Primary ZDDP:** 0.8% w/w (0.08% phosphorus)
2. **Compensate with Alternative Anti-wear:**
   - Organic Molybdenum: 0.1% w/w
   - Titanium Dioxide nanoparticles: 0.05% w/w
   - Boron compounds: 0.08% w/w

**Performance Impact Analysis:**
- **Wear Protection:** 92% retention (vs 100% baseline)
- **Scuffing Protection:** 95% retention
- **Valve Train Wear:** Requires enhanced base oil (Group III+)

**Validation Requirements:**
- Sequence IIIG (LSPI test)
- Sequence IVB (cam/tappet wear)
- Engine dynamometer testing (200 hours)

**Cost Impact:**
- Raw material cost increase: +₹12/liter
- Testing validation: ₹35 lakhs
- Timeline: 6 months development

**Risk Mitigation:**
- Field trials with OEM partners
- Enhanced monitoring during initial production
- Alternative additive backup formulations

**Recommendation:** 
✅ **PROCEED** with phased implementation
- Phase 1: Premium grades (Quartz 9000)
- Phase 2: Mid-tier grades (Quartz 7000)

**Regulatory Status:**
- BS VI Phase 2 effective: April 2025
- Current formulations compliant until April 2026

**Source:** R&D Formulation Lab + Regulatory Affairs + OEM Technical Centers"""

    response_hi = """**BS VI अनुपालन के लिए ZDDP कमी विश्लेषण:**

**वर्तमान ZDDP स्तर:**
- मानक इंजन ऑयल: 1.2% w/w ZDDP (0.12% फास्फोरस)
- BS VI आवश्यकता: ≤0.08% फास्फोरस अधिकतम

**तकनीकी मूल्यांकन:**
**✅ संभव - शर्तों के साथ 0.08% P तक कमी**

**फॉर्मूलेशन रणनीति:**
1. **प्राथमिक ZDDP कम करें:** 0.8% w/w (0.08% फास्फोरस)
2. **वैकल्पिक एंटी-वियर से क्षतिपूर्ति:**
   - ऑर्गेनिक मोलिब्डेनम: 0.1% w/w
   - टाइटेनियम डाइऑक्साइड नैनोकण: 0.05% w/w
   - बोरॉन यौगिक: 0.08% w/w

**प्रदर्शन प्रभाव विश्लेषण:**
- **घिसाव सुरक्षा:** 92% बनाए रखना (बेसलाइन 100% बनाम)
- **स्कफिंग सुरक्षा:** 95% बनाए रखना
- **वाल्व ट्रेन घिसाव:** संवर्धित बेस ऑयल (Group III+) आवश्यक

**सत्यापन आवश्यकताएं:**
- Sequence IIIG (LSPI परीक्षण)
- Sequence IVB (कैम/टैप्पेट घिसाव)
- इंजन डायनामोमीटर परीक्षण (200 घंटे)

**लागत प्रभाव:**
- कच्चे माल की लागत वृद्धि: +₹12/लीटर
- परीक्षण सत्यापन: ₹35 लाख
- समयसीमा: 6 महीने विकास

**जोखिम न्यूनीकरण:**
- OEM भागीदारों के साथ फील्ड ट्रायल
- प्रारंभिक उत्पादन के दौरान संवर्धित निगरानी
- वैकल्पिक एडिटिव बैकअप फॉर्मूलेशन

**सिफारिश:**
✅ **आगे बढ़ें** चरणबद्ध कार्यान्वयन के साथ
- चरण 1: प्रीमियम ग्रेड (Quartz 9000)
- चरण 2: मध्यम स्तरीय ग्रेड (Quartz 7000)

**नियामक स्थिति:**
- BS VI चरण 2 प्रभावी: अप्रैल 2025
- वर्तमान फॉर्मूलेशन अप्रैल 2026 तक अनुपालित

**स्रोत:** R&D फॉर्मूलेशन लैब + नियामक मामले + OEM तकनीकी केंद्र"""

    return {
        'category': 'regulatory_compliance',
        'agents': ['RegulatoryAgent', 'FormulationAgent'],
        'response': response_hi if language == 'hindi' else response_en,
        'sources': [
            {'type': 'Regulatory_DB', 'document': 'BS VI Phase 2 Requirements'},
            {'type': 'R&D_Lab', 'document': 'ZDDP Alternative Study Report'},
            {'type': 'OEM_Technical', 'document': 'Engine Testing Validation Protocols'}
        ],
        'processing_time_ms': random.randint(2500, 3500)
    }


def _simulate_group_iii_supplier_query(query, language, correlation_id):
    """Handle Group III base oil supplier delivery query"""
    
    response_en = """**Group III Base Oil Suppliers - Mumbai Delivery (500 MT within 2 weeks):**

**✅ CONFIRMED DELIVERY CAPABILITY TO MUMBAI:**

**1. Reliance Industries (Jamnagar to Mumbai)** ⭐ **BEST OPTION**
- **Mumbai Delivery:** 8-10 days via dedicated rail tankers
- **Available:** 2,500 MT (can easily fulfill 500 MT)
- **Price:** ₹94,800/MT (includes Mumbai delivery)
- **Quality:** Group III+ 4 cSt (VI 128) - Premium grade
- **Logistics:** Direct rail line Jamnagar→Kalamboli terminal
- **Track Record:** 99.2% on-time delivery to Mumbai

**2. Nayara Energy (Vadinar to Mumbai)** ⭐ **RELIABLE OPTION**
- **Mumbai Delivery:** 10-12 days via ONGC pipeline + rail
- **Available:** 1,800 MT (sufficient for 500 MT order)
- **Price:** ₹95,200/MT (Mumbai delivered)
- **Quality:** Group III 4 cSt (VI 125) - Standard grade
- **Logistics:** Pipeline to Uran, then truck to your facility
- **Track Record:** Established Mumbai supply chain

**3. Indian Oil Corporation (Gujarat to Mumbai)** 
- **Mumbai Delivery:** 12-14 days via rail tanker
- **Available:** 1,200 MT (limited availability)
- **Price:** ₹94,500/MT (Mumbai delivered)
- **Quality:** Group III 4 cSt (VI 126)
- **Logistics:** Western Railway freight corridor
- **Note:** May face scheduling delays due to limited slots

**RECOMMENDED MUMBAI PROCUREMENT STRATEGY:**
✅ **Single Source - Reliance Industries (Jamnagar)**
- **Order:** 500 MT complete order
- **Delivery:** 8-10 days to Mumbai (fastest option)
- **Price:** ₹94,800/MT (most competitive)
- **Quality:** Premium Group III+ grade
- **Reliability:** Established Mumbai supply route

**MUMBAI LOGISTICS INFRASTRUCTURE:**
- **Receiving Terminal:** Kalamboli Rail Terminal (TotalEnergies facility)
- **Unloading Capacity:** 150 MT/day (500 MT in 4 days)
- **Storage:** 1,500 MT capacity available at Mumbai terminal
- **Quality Lab:** On-site testing facility (8-hour turnaround)
- **Road Transport:** 25 km to main Mumbai blending facility

**MUMBAI DELIVERY TIMELINE:**
- **Day 1-2:** Purchase order processing & rail booking
- **Day 3-8:** Rail transport Jamnagar → Mumbai Kalamboli
- **Day 9-10:** Terminal unloading & quality verification
- **Day 11:** Material available for production

**MUMBAI-SPECIFIC ADVANTAGES:**
- No port delays (direct rail delivery)
- Established supply chain relationships
- Local quality control and storage
- Immediate availability for blending operations

**NEXT STEPS FOR MUMBAI DELIVERY:**
1. **Immediate:** Confirm rail slot availability with Reliance
2. **Today:** Issue purchase order for 500 MT
3. **Tomorrow:** Coordinate with Mumbai terminal operations
4. **Day 3:** Track rail shipment departure from Jamnagar

**Source:** Supplier Portal + Logistics Management + Procurement Database"""

    response_hi = """**Group III बेस ऑयल - मुंबई डिलीवरी (500 MT, 2 सप्ताह में):**

**✅ मुंबई डिलीवरी सत्यापित आपूर्तिकर्ता:**

**1. रिलायंस इंडस्ट्रीज (जामनगर→मुंबई)** ⭐ **प्राथमिक विकल्प**
- **मुंबई डिलीवरी समय:** 8-10 दिन (समर्पित रेल)
- **उपलब्ध:** 2,500 MT (500 MT पूर्ण आपूर्ति गारंटी)
- **मूल्य:** ₹94,800/MT (मुंबई डिलीवरी शुल्क शामिल)
- **गुणवत्ता:** Group III+ 4 cSt (VI 128) - प्रीमियम ग्रेड
- **मुंबई रूट:** जामनगर→कलंबोली टर्मिनल (डायरेक्ट रेल)
- **ट्रैक रिकॉर्ड:** मुंबई में 99.2% समय पर डिलीवरी

**2. नयारा एनर्जी (वाडिनार→मुंबई)** ⭐ **बैकअप विकल्प**
- **मुंबई डिलीवरी समय:** 10-12 दिन (पाइपलाइन+रेल)
- **उपलब्ध:** 1,800 MT (500 MT के लिए पर्याप्त स्टॉक)
- **मूल्य:** ₹95,200/MT (मुंबई पोर्ट तक)
- **गुणवत्ता:** Group III 4 cSt (VI 125) - स्टैंडर्ड ग्रेड
- **मुंबई रूट:** उरान पाइपलाइन + ट्रक ट्रांसफर
- **विशेषता:** स्थापित मुंबई आपूर्ति श्रृंखला

**3. इंडियन ऑयल कॉर्पोरेशन (गुजरात→मुंबई)**
- **मुंबई डिलीवरी समय:** 12-14 दिन (रेल टैंकर)
- **उपलब्ध:** 1,200 MT (सीमित स्लॉट)
- **मूल्य:** ₹94,500/MT (मुंबई टर्मिनल तक)
- **गुणवत्ता:** Group III 4 cSt (VI 126)
- **मुंबई रूट:** वेस्टर्न रेलवे फ्रेट कॉरिडोर
- **सीमा:** रेल स्लॉट की उपलब्धता पर निर्भर

**मुंबई डिलीवरी रणनीति:**
✅ **अनुशंसित दृष्टिकोण:**
- **प्राथमिक:** रिलायंस 400 MT (सबसे तेज़ मुंबई डिलीवरी)
- **बैकअप:** नयारा 100 MT (रिस्क मिटिगेशन)

**मुंबई लॉजिस्टिक्स इंफ्रास्ट्रक्चर:**
- **कलंबोली टर्मिनल:** 24/7 रिसेप्शन
- **भंडारण:** तलोजा में 1,500 MT कैपेसिटी
- **क्वालिटी चेक:** 12 घंटे टर्नअराउंड
- **ट्रक डिस्पैच:** मुंबई के भीतर तुरंत डिलीवरी

**मुंबई-विशिष्ट लाभ:**
- पोर्ट एरिया प्रोक्सिमिटी (5 किमी)
- डेडिकेटेड रेल टर्मिनल एक्सेस
- 24x7 कस्टम क्लियरेंस
- एक्सपीडाइटेड डॉक्यूमेंटेशन

**तत्काल क्रियान्वयन:**
1. **आज:** मुंबई-फोकस्ड PO जारी करें
2. **कल:** कलंबोली टर्मिनल कोऑर्डिनेशन
3. **दिन 3:** मुंबई रेल शिपमेंट ट्रैकिंग शुरू करें

**स्रोत:** मुंबई लॉजिस्टिक्स हब + सप्लायर पोर्टल + प्रोक्योरमेंट सिस्टम"""

    return {
        'category': 'supply_chain',
        'agents': ['SupplyChainAgent', 'ProcurementAgent'],
        'response': response_hi if language == 'hindi' else response_en,
        'sources': [
            {'type': 'Supplier_Portal', 'document': 'Real-time Inventory & Lead Times'},
            {'type': 'Logistics_System', 'document': 'Transportation Capacity Matrix'},
            {'type': 'Procurement_DB', 'document': 'Approved Vendor Contracts & Pricing'}
        ],
        'processing_time_ms': random.randint(2000, 3000)
    }


def _simulate_lpg_white_deposits_investigation(query, language, correlation_id):
    """Handle LPG white deposits investigation query"""
    
    response_en = """**LPG White Deposits Investigation - Root Cause Analysis:**

**INCIDENT SUMMARY:**
- **Customer Reports:** 47 complaints (Mumbai, Pune, Ahmedabad)
- **Affected Batches:** LPG-DOM-2025-0312, LPG-DOM-2025-0315
- **Issue:** White crystalline deposits inside cylinders

**ROOT CAUSE ANALYSIS:**

**Primary Cause: Moisture Contamination + Low Temperature**
- **Moisture Content:** 180 ppm (Spec: <50 ppm) ❌
- **Formation Mechanism:** H₂O + C₃H₈ + Low temp → Gas hydrates
- **Conditions:** Winter temperatures (5-12°C) triggered formation

**CONTRIBUTING FACTORS:**
1. **Storage Tank Issue:**
   - Atmospheric moisture ingress during maintenance
   - Faulty nitrogen blanketing system
   - Inadequate dehydration before filling

2. **Quality Control Gap:**
   - LIMS moisture test delayed by 18 hours
   - Batch released before complete analysis
   - Override procedure used incorrectly

3. **Transportation:**
   - Cylinder exposure to temperature cycling
   - Condensation in delivery trucks

**IMMEDIATE CORRECTIVE ACTIONS:**

**✅ COMPLETED:**
1. **Product Recall:** 8,500 cylinders quarantined
2. **Customer Support:** Free replacement program launched
3. **Quality Hold:** All LPG production suspended (24 hours)

**🔄 IN PROGRESS:**
4. **Enhanced Testing:** Moisture analysis now mandatory before release
5. **Storage Upgrade:** New nitrogen blanketing system installation
6. **Staff Training:** Quality control procedures reinforcement

**PREVENTIVE MEASURES:**

**SHORT-TERM (1-4 weeks):**
- Install continuous moisture analyzers (₹16 lakh investment)
- Implement mandatory 48-hour quality hold
- Enhanced cylinder pre-cleaning protocols

**LONG-TERM (3-6 months):**
- LPG dehydration unit installation (₹65 lakh investment)
- Automated quality release system
- Customer complaint tracking system

**REGULATORY COMPLIANCE:**
- **PESO Notification:** Filed within 48 hours ✅
- **Voluntary Recall:** Approved by management ✅
- **Investigation Report:** Due within 30 days

**COST IMPACT:**
- **Immediate:** ₹48 lakh (recall + replacement)
- **Infrastructure:** ₹81 lakh (equipment + systems)
- **Total:** ₹1.29 crore

**CUSTOMER COMMUNICATION:**
- Public notice in newspapers (completed)
- Direct SMS to affected customers (completed)
- Toll-free helpline: 1800-XXX-XXXX (operational)

**LESSONS LEARNED:**
1. **Never override quality procedures** during production pressure
2. **Moisture control is critical** for LPG quality
3. **Proactive communication** reduces customer dissatisfaction

**NEXT REVIEW:** Weekly monitoring for 3 months

**Source:** LIMS Investigation Report + Customer Service + Regulatory Affairs + Engineering"""

    response_hi = """**LPG सफेद जमाव जांच - मूल कारण विश्लेषण:**

**घटना सारांश:**
- **ग्राहक रिपोर्ट:** 47 शिकायतें (मुंबई, पुणे, अहमदाबाद)
- **प्रभावित बैच:** LPG-DOM-2025-0312, LPG-DOM-2025-0315
- **समस्या:** सिलेंडरों के अंदर सफेद क्रिस्टलीय जमाव

**मूल कारण विश्लेषण:**

**प्राथमिक कारण: नमी संदूषण + कम तापमान**
- **नमी सामग्री:** 180 ppm (स्पेक: <50 ppm) ❌
- **निर्माण तंत्र:** H₂O + C₃H₈ + कम तापमान → गैस हाइड्रेट्स
- **स्थितियां:** सर्दियों का तापमान (5-12°C) ने निर्माण को ट्रिगर किया

**योगदान कारक:**
1. **भंडारण टैंक समस्या:**
   - रखरखाव के दौरान वायुमंडलीय नमी प्रवेश
   - दोषपूर्ण नाइट्रोजन ब्लैंकेटिंग सिस्टम
   - भरने से पहले अपर्याप्त निर्जलीकरण

2. **गुणवत्ता नियंत्रण अंतर:**
   - LIMS नमी परीक्षण 18 घंटे देर से
   - पूर्ण विश्लेषण से पहले बैच रिलीज़
   - ओवरराइड प्रक्रिया का गलत उपयोग

3. **परिवहन:**
   - तापमान चक्रण के लिए सिलेंडर एक्सपोज़र
   - डिलीवरी ट्रकों में संघनन

**तत्काल सुधारात्मक कार्य:**

**✅ पूर्ण:**
1. **उत्पाद वापसी:** 8,500 सिलेंडर क्वारंटाइन
2. **ग्राहक सहायता:** मुफ्त प्रतिस्थापन कार्यक्रम शुरू
3. **गुणवत्ता होल्ड:** सभी LPG उत्पादन निलंबित (24 घंटे)

**🔄 प्रगति में:**
4. **संवर्धित परीक्षण:** रिलीज़ से पहले नमी विश्लेषण अब अनिवार्य
5. **भंडारण अपग्रेड:** नई नाइट्रोजन ब्लैंकेटिंग सिस्टम स्थापना
6. **स्टाफ प्रशिक्षण:** गुणवत्ता नियंत्रण प्रक्रियाओं को मजबूत बनाना

**निवारक उपाय:**

**अल्पकालिक (1-4 सप्ताह):**
- निरंतर नमी विश्लेषक स्थापित करें (₹16 लाख निवेश)
- अनिवार्य 48-घंटे गुणवत्ता होल्ड लागू करें
- संवर्धित सिलेंडर प्री-क्लीनिंग प्रोटोकॉल

**दीर्घकालिक (3-6 महीने):**
- LPG निर्जलीकरण यूनिट स्थापना (₹65 लाख निवेश)
- स्वचालित गुणवत्ता रिलीज़ सिस्टम
- ग्राहक शिकायत ट्रैकिंग सिस्टम

**नियामक अनुपालन:**
- **PESO अधिसूचना:** 48 घंटों के भीतर दाखिल ✅
- **स्वैच्छिक वापसी:** प्रबंधन द्वारा अनुमोदित ✅
- **जांच रिपोर्ट:** 30 दिनों के भीतर देय

**लागत प्रभाव:**
- **तत्काल:** ₹48 लाख (वापसी + प्रतिस्थापन)
- **इन्फ्रास्ट्रक्चर:** ₹81 लाख (उपकरण + सिस्टम)
- **कुल:** ₹1.29 करोड़

**ग्राहक संचार:**
- अखबारों में सार्वजनिक सूचना (पूर्ण)
- प्रभावित ग्राहकों को प्रत्यक्ष SMS (पूर्ण)
- टोल-फ्री हेल्पलाइन: 1800-XXX-XXXX (परिचालन)

**सीखे गए सबक:**
1. **उत्पादन दबाव के दौरान गुणवत्ता प्रक्रियाओं को कभी ओवरराइड न करें**
2. **LPG गुणवत्ता के लिए नमी नियंत्रण महत्वपूर्ण है**
3. **सक्रिय संचार** ग्राहक असंतुष्टि को कम करता है

**अगली समीक्षा:** 3 महीने के लिए साप्ताहिक निगरानी

**स्रोत:** LIMS जांच रिपोर्ट + ग्राहक सेवा + नियामक मामले + इंजीनियरिंग"""

    return {
        'category': 'quality_investigation',
        'agents': ['QualityControlAgent', 'CustomerServiceAgent', 'RegulatoryAgent'],
        'response': response_hi if language == 'hindi' else response_en,
        'sources': [
            {'type': 'LIMS', 'document': 'Batch Quality Investigation Report'},
            {'type': 'Customer_Service', 'document': 'Complaint Analysis & Response'},
            {'type': 'Regulatory_DB', 'document': 'PESO Notification & Compliance Status'}
        ],
        'processing_time_ms': random.randint(3000, 4000)
    }


def _is_greeting_query(query_lower, language):
    """Check if the query is a greeting or capability inquiry"""
    greeting_patterns = {
        'en': ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening',
               'what can you do', 'what are your capabilities', 'help', 'who are you',
               'what is this', 'how can you help', 'what do you know'],
        'hi': ['नमस्ते', 'हैलो', 'हाय', 'आप कैसे हैं', 'आप क्या कर सकते हैं',
               'आपकी क्षमताएं क्या हैं', 'मदद', 'आप कौन हैं', 'यह क्या है',
               'आप कैसे मदद कर सकते हैं', 'आप क्या जानते हैं']
    }
    
    lang_code = 'hi' if language in ['hindi', 'hi'] else 'en'
    patterns = greeting_patterns.get(lang_code, greeting_patterns['en'])
    
    return any(pattern in query_lower for pattern in patterns)


def _handle_greeting_query(query, language, correlation_id):
    """Handle greeting queries with database-stored responses"""
    
    # Determine query type
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['capabilities', 'can you do', 'help', 'know']):
        greeting_type = 'capabilities'
    elif any(word in query_lower for word in ['who are you', 'what is this']):
        greeting_type = 'introduction'
    else:
        greeting_type = 'greeting'
    
    lang_code = 'hi' if language in ['hindi', 'hi'] else 'en'
    
    try:
        # Try to get response from database
        greeting_response = TEGreetingResponse.query.filter_by(
            greeting_type=greeting_type,
            language=lang_code,
            active=True
        ).order_by(db.func.random()).first()
        
        if greeting_response:
            response_text = greeting_response.response_text
        else:
            # Fallback responses if database is empty
            response_text = _get_fallback_greeting_response(greeting_type, lang_code)
        
    except Exception:
        # Fallback if database query fails
        response_text = _get_fallback_greeting_response(greeting_type, lang_code)
    
    return {
        'category': 'greeting',
        'agents': ['knowledge_orchestrator'],
        'response': response_text,
        'sources': [
            {'type': 'Greeting_DB', 'document': 'Dynamic Greeting Responses'},
            {'type': 'Capabilities_DB', 'document': 'Engineer Copilot Capabilities'}
        ],
        'processing_time_ms': random.randint(800, 1200)
    }


def _get_fallback_greeting_response(greeting_type, language):
    """Fallback greeting responses when database is not available"""
    
    fallback_responses = {
        'greeting': {
            'en': """Hello! 👋 I'm your TotalEnergies Engineer's Copilot.

I'm here to assist you with:
• **Formulation Development** - Lubricant formulations, additives, base oils
• **Supply Chain Intelligence** - Supplier information, inventory levels, lead times  
• **Quality Control** - Test results, batch analysis, compliance checks
• **Technical Documentation** - Specifications, protocols, regulatory requirements
• **Process Optimization** - Production insights, cost analysis, efficiency improvements

I can answer questions in both **English** and **हिंदी**.

How can I help you today?""",
            
            'hi': """नमस्ते! 👋 मैं आपका TotalEnergies Engineer's Copilot हूं।

मैं आपकी सहायता कर सकता हूं:
• **फॉर्मूलेशन विकास** - स्नेहक फॉर्मूलेशन, एडिटिव्स, बेस ऑयल
• **आपूर्ति श्रृंखला बुद्धिमत्ता** - आपूर्तिकर्ता जानकारी, इन्वेंट्री स्तर, लीड टाइम
• **गुणवत्ता नियंत्रण** - परीक्षण परिणाम, बैच विश्लेषण, अनुपालन जांच
• **तकनीकी दस्तावेज** - विनिर्देश, प्रोटोकॉल, नियामक आवश्यकताएं
• **प्रक्रिया अनुकूलन** - उत्पादन अंतर्दृष्टि, लागत विश्लेषण, दक्षता सुधार

मैं **अंग्रेजी** और **हिंदी** दोनों भाषाओं में प्रश्नों का उत्तर दे सकता हूं।

आज मैं आपकी कैसे सहायता कर सकता हूं?"""
        },
        
        'capabilities': {
            'en': """🤖 **Engineer's Copilot Capabilities:**

**🔬 Formulation Intelligence:**
• Lubricant formulation recommendations (Engine oils, Gear oils, Hydraulic fluids)
• Additive package optimization (ZDDP, VI improvers, Dispersants)
• Base oil selection guidance (Group I/II/III, PAO, Ester)
• Performance prediction and cost optimization

**🏭 Supply Chain & Inventory:**
• Real-time supplier information and lead times
• Inventory level monitoring and low-stock alerts
• Procurement recommendations and supplier comparisons
• Material availability across multiple locations

**🧪 Quality & Testing:**
• LIMS data analysis and batch investigation
• Test protocol generation and standard compliance
• Quality failure root cause analysis
• Regulatory requirement validation (API, ACEA, BIS, PESO)

**📊 Technical Documentation:**
• Access to 1000+ technical documents and specifications
• Formulation trial history and performance data
• Industry standards and regulatory compliance guides
• Best practices and troubleshooting guides

**🌐 Multi-Language Support:**
• Full functionality in English and Hindi
• Technical terminology translation
• Localized responses for Indian market requirements

**⚡ Real-Time Processing:**
• Average response time: 2.3 seconds
• Multi-agent collaboration for complex queries
• Source citation and confidence scoring

Try asking me about specific products, suppliers, test results, or formulation challenges!""",
            
            'hi': """🤖 **Engineer's Copilot की क्षमताएं:**

**🔬 फॉर्मूलेशन बुद्धिमत्ता:**
• स्नेहक फॉर्मूलेशन सिफारिशें (इंजन ऑयल, गियर ऑयल, हाइड्रोलिक तरल पदार्थ)
• एडिटिव पैकेज अनुकूलन (ZDDP, VI सुधारक, डिस्पर्सेंट)
• बेस ऑयल चयन मार्गदर्शन (Group I/II/III, PAO, Ester)
• प्रदर्शन भविष्यवाणी और लागत अनुकूलन

**🏭 आपूर्ति श्रृंखला और इन्वेंट्री:**
• वास्तविक समय आपूर्तिकर्ता जानकारी और लीड टाइम
• इन्वेंट्री स्तर निगरानी और कम-स्टॉक अलर्ट
• खरीद सिफारिशें और आपूर्तिकर्ता तुलना
• कई स्थानों पर सामग्री उपलब्धता

**🧪 गुणवत्ता और परीक्षण:**
• LIMS डेटा विश्लेषण और बैच जांच
• परीक्षण प्रोटोकॉल जनरेशन और मानक अनुपालन
• गुणवत्ता असफलता मूल कारण विश्लेषण
• नियामक आवश्यकता सत्यापन (API, ACEA, BIS, PESO)

**📊 तकनीकी दस्तावेज:**
• 1000+ तकनीकी दस्तावेजों और विनिर्देशों तक पहुंच
• फॉर्मूलेशन ट्रायल इतिहास और प्रदर्शन डेटा
• उद्योग मानक और नियामक अनुपालन गाइड
• सर्वोत्तम प्रथाओं और समस्या निवारण गाइड

**🌐 बहु-भाषा समर्थन:**
• अंग्रेजी और हिंदी में पूर्ण कार्यक्षमता
• तकनीकी शब्दावली अनुवाद
• भारतीय बाजार आवश्यकताओं के लिए स्थानीयकृत प्रतिक्रियाएं

**⚡ वास्तविक समय प्रसंस्करण:**
• औसत प्रतिक्रिया समय: 2.3 सेकंड
• जटिल प्रश्नों के लिए बहु-एजेंट सहयोग
• स्रोत उद्धरण और विश्वास स्कोरिंग

मुझसे विशिष्ट उत्पादों, आपूर्तिकर्ताओं, परीक्षण परिणामों या फॉर्मूलेशन चुनौतियों के बारे में पूछने का प्रयास करें!"""
        },
        
        'introduction': {
            'en': """I'm the **TotalEnergies Engineer's Copilot** - your AI-powered technical assistant for lubricant R&D and manufacturing.

**What I Am:**
• Advanced AI system specialized in petroleum products and lubricants
• Connected to TotalEnergies technical databases and knowledge systems
• Multi-agent architecture with specialized expertise areas

**My Core Functions:**
• Formulation development and optimization
• Supply chain and procurement intelligence  
• Quality control and batch analysis
• Technical documentation and compliance
• Real-time data analysis and insights

**How I Work:**
• Natural language processing in English and Hindi
• Access to live inventory, supplier, and quality data
• Multi-source information synthesis
• Evidence-based recommendations with source citations

I'm designed specifically for TotalEnergies engineers, chemists, and technical staff to accelerate R&D processes and improve operational efficiency.

What technical challenge can I help you solve today?""",
            
            'hi': """मैं **TotalEnergies Engineer's Copilot** हूं - स्नेहक R&D और निर्माण के लिए आपका AI-संचालित तकनीकी सहायक।

**मैं क्या हूं:**
• पेट्रोलियम उत्पादों और स्नेहकों में विशेषज्ञता वाला उन्नत AI सिस्टम
• TotalEnergies तकनीकी डेटाबेस और ज्ञान प्रणालियों से जुड़ा हुआ
• विशेषज्ञता क्षेत्रों के साथ बहु-एजेंट आर्किटेक्चर

**मेरे मुख्य कार्य:**
• फॉर्मूलेशन विकास और अनुकूलन
• आपूर्ति श्रृंखला और खरीद बुद्धिमत्ता
• गुणवत्ता नियंत्रण और बैच विश्लेषण
• तकनीकी दस्तावेज और अनुपालन
• वास्तविक समय डेटा विश्लेषण और अंतर्दृष्टि

**मैं कैसे काम करता हूं:**
• अंग्रेजी और हिंदी में प्राकृतिक भाषा प्रसंस्करण
• लाइव इन्वेंट्री, आपूर्तिकर्ता और गुणवत्ता डेटा तक पहुंच
• बहु-स्रोत जानकारी संश्लेषण
• स्रोत उद्धरण के साथ साक्ष्य-आधारित सिफारिशें

मैं विशेष रूप से TotalEnergies इंजीनियरों, रसायनज्ञों और तकनीकी कर्मचारियों के लिए R&D प्रक्रियाओं को तेज करने और परिचालन दक्षता में सुधार के लिए डिज़ाइन किया गया हूं।

आज मैं आपकी किस तकनीकी चुनौती को हल करने में मदद कर सकता हूं?"""
        }
    }
    
    return fallback_responses.get(greeting_type, {}).get(language, 
           fallback_responses['greeting']['en'])


# Only dashboard and query processing routes are used
# All other routes removed as their templates don't exist
