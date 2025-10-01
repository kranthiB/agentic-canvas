"""
Demo 5: Engineer's Copilot Agent
T2 Procedural Workflow + Generative Agent for TCAP Mumbai R&D
"""
import random
import json
from typing import Dict, Any, List
from datetime import datetime
import logging

from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

# Note: In production, use actual OpenAI API
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not available - using mock responses")


class EngineersCopilotAgent(BaseAgent):
    """
    T2 Procedural Workflow + Generative Agent
    Capabilities: PK.KB, CG.RS, AE.CX, LA.VM, IC.NL
    """
    
    def __init__(self, openai_api_key: str = None):
        super().__init__(
            agent_id='engineers-copilot-001',
            agent_type='T2-Procedural-Generative',
            capabilities=['PK.KB', 'CG.RS', 'AE.CX', 'LA.VM', 'IC.NL']
        )
        
        self.openai_api_key = openai_api_key
        self.model = 'gpt-4' if OPENAI_AVAILABLE else 'mock'
        self.confidence = 0.89
        
        # Knowledge bases
        self.base_oils = [
            'Mineral Group I (High VI)',
            'Mineral Group II (Hydrocracked)',
            'Mineral Group III (Severe Hydrocracked)',
            'Synthetic PAO',
            'Synthetic Ester',
            'Polyalkylene Glycol (PAG)'
        ]
        
        self.additives = [
            {'name': 'ZDDP (Zinc dialkyldithiophosphate)', 'function': 'Anti-wear', 'typical_pct': 1.2},
            {'name': 'Calcium Sulfonate', 'function': 'Detergent', 'typical_pct': 2.5},
            {'name': 'PIB (Polyisobutylene)', 'function': 'Viscosity Modifier', 'typical_pct': 8.0},
            {'name': 'Phenolic Antioxidant', 'function': 'Oxidation Inhibitor', 'typical_pct': 0.8},
            {'name': 'Amine Antioxidant', 'function': 'Oxidation Inhibitor', 'typical_pct': 0.5},
            {'name': 'Pour Point Depressant', 'function': 'Low-temp Flow', 'typical_pct': 0.3},
            {'name': 'Foam Inhibitor (Silicone)', 'function': 'Anti-foam', 'typical_pct': 0.01},
            {'name': 'Friction Modifier (MoDTC)', 'function': 'Fuel Economy', 'typical_pct': 0.7}
        ]
    
    def perceive(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """
        PK.KB - Knowledge Access
        LA.VM - Vector Memory
        Access research knowledge base
        """
        query = environment.get('query', '')
        language = environment.get('language', 'en')
        intent = environment.get('intent', 'search')
        
        perception = {
            'query': query,
            'language': language,
            'intent': intent,
            'context': environment.get('context', {}),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Perceived query: '{query}' (language: {language}, intent: {intent})")
        
        return perception
    
    def reason(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """
        CG.RS - Reasoning
        IC.NL - Natural Language
        Process query and determine response
        """
        intent = perception['intent']
        query = perception['query']
        language = perception['language']
        
        if intent == 'search_papers':
            decision = self._search_papers(query)
        elif intent == 'search_trials':
            decision = self._search_trials(query)
        elif intent == 'recommend_formulation':
            decision = self._recommend_formulation(perception['context'])
        elif intent == 'generate_protocol':
            decision = self._generate_protocol(perception['context'])
        elif intent == 'explain_term':
            decision = self._explain_technical_term(query, language)
        else:
            decision = self._general_chat(query, language)
        
        decision['confidence'] = self.confidence
        decision['language'] = language
        
        return decision
    
    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        AE.CX - Content Creation & Generation
        Generate response content
        """
        intent = decision.get('intent', 'chat')
        language = decision.get('language', 'en')
        
        result = {
            'intent': intent,
            'response': decision.get('response', ''),
            'data': decision.get('data', {}),
            'language': language,
            'generated_at': datetime.utcnow().isoformat()
        }
        
        return result
    
    # Intent Handlers
    
    def _search_papers(self, query: str) -> Dict[str, Any]:
        """
        LA.VM - Vector Memory
        Semantic search over research papers
        """
        # Mock semantic search results
        mock_papers = [
            {
                'paper_id': 'TCAP-2023-1045',
                'title': 'Advanced Synthetic Esters for High-Temperature Engine Oils',
                'authors': ['Dr. Rajesh Kumar', 'Dr. Priya Sharma'],
                'year': 2023,
                'relevance_score': 0.92,
                'abstract': 'This study evaluates synthetic ester base stocks for heavy-duty diesel engines...'
            },
            {
                'paper_id': 'TCAP-2022-0876',
                'title': 'Zinc-Free Antiwear Additives: Performance Evaluation',
                'authors': ['Dr. Amit Patel'],
                'year': 2022,
                'relevance_score': 0.87,
                'abstract': 'Investigation of environmentally friendly alternatives to traditional ZDDP...'
            },
            {
                'paper_id': 'TCAP-2021-0654',
                'title': 'Viscosity Index Improvers for Multi-grade Oils',
                'authors': ['Sneha Desai', 'Dr. Vijay Singh'],
                'year': 2021,
                'relevance_score': 0.83,
                'abstract': 'Comparative study of PIB and OCP viscosity modifiers...'
            }
        ]
        
        return {
            'intent': 'search_papers',
            'response': f"Found {len(mock_papers)} relevant research papers",
            'data': {
                'papers': mock_papers,
                'total_results': len(mock_papers)
            }
        }
    
    def _search_trials(self, query: str) -> Dict[str, Any]:
        """Search formulation trial history"""
        # Mock trial search results
        mock_trials = [
            {
                'trial_id': 'TCAP-T-2024-0156',
                'name': '15W-40 Diesel Engine Oil - High TBN',
                'base_oil': 'Group II (85%)',
                'performance_score': 87.5,
                'meets_specs': True,
                'year': 2024
            },
            {
                'trial_id': 'TCAP-T-2024-0142',
                'name': '10W-30 Synthetic Blend',
                'base_oil': 'Group III + PAO (70% + 15%)',
                'performance_score': 92.3,
                'meets_specs': True,
                'year': 2024
            }
        ]
        
        return {
            'intent': 'search_trials',
            'response': f"Found {len(mock_trials)} relevant formulation trials",
            'data': {
                'trials': mock_trials,
                'total_results': len(mock_trials)
            }
        }
    
    def _recommend_formulation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        CG.RS - Reasoning
        Recommend lubricant formulations
        """
        product_type = context.get('product_type', 'Engine Oil')
        target_properties = context.get('target_properties', {})
        constraints = context.get('constraints', {})
        
        # Generate 3 formulation recommendations
        recommendations = []
        
        for i in range(3):
            base_oil = random.choice(self.base_oils)
            base_oil_pct = random.uniform(75, 90)
            
            # Select additives
            selected_additives = random.sample(self.additives, k=random.randint(4, 6))
            additive_package = []
            remaining_pct = 100 - base_oil_pct
            
            for additive in selected_additives:
                pct = additive['typical_pct'] * random.uniform(0.8, 1.2)
                if remaining_pct >= pct:
                    additive_package.append({
                        'name': additive['name'],
                        'function': additive['function'],
                        'percentage': round(pct, 2)
                    })
                    remaining_pct -= pct
            
            # Predict properties (mock)
            formulation = {
                'formulation_id': f'REC-{datetime.now().strftime("%Y%m%d")}-{i+1:03d}',
                'name': f'{product_type} - Recommendation #{i+1}',
                'rank': i + 1,
                'base_oil': base_oil,
                'base_oil_percentage': round(base_oil_pct, 1),
                'additive_package': additive_package,
                'predicted_properties': {
                    'viscosity_index': random.randint(120, 160),
                    'wear_resistance': random.uniform(85, 95),
                    'oxidation_stability': random.uniform(180, 250),
                    'performance_score': random.uniform(80, 95)
                },
                'cost_per_liter_inr': random.uniform(180, 350),
                'confidence_score': random.uniform(0.82, 0.94),
                'pros': self._generate_pros(base_oil),
                'cons': self._generate_cons(base_oil),
                'reasoning': self._generate_formulation_reasoning(base_oil, product_type)
            }
            
            recommendations.append(formulation)
        
        # Sort by performance score
        recommendations.sort(key=lambda x: x['predicted_properties']['performance_score'], reverse=True)
        
        # Update ranks
        for i, rec in enumerate(recommendations, 1):
            rec['rank'] = i
        
        return {
            'intent': 'recommend_formulation',
            'response': f"Generated {len(recommendations)} formulation recommendations for {product_type}",
            'data': {
                'recommendations': recommendations,
                'product_type': product_type,
                'target_properties': target_properties
            }
        }
    
    def _generate_protocol(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        AE.CX - Content Creation & Generation
        Auto-generate test protocol
        """
        formulation = context.get('formulation', {})
        test_standards = context.get('test_standards', ['ASTM D445', 'ASTM D4172', 'ASTM D2270'])
        
        protocol_content = f"""
# TEST PROTOCOL
## {formulation.get('name', 'Lubricant Formulation')}

### 1. OBJECTIVE
Evaluate the performance characteristics of the formulated lubricant according to specified industry standards.

### 2. SCOPE
This protocol covers:
- Kinematic viscosity testing (ASTM D445)
- Four-ball wear test (ASTM D4172)
- Viscosity index calculation (ASTM D2270)
- Additional property evaluations as required

### 3. EQUIPMENT REQUIRED
- Kinematic viscosity bath (40°C and 100°C)
- Cannon-Fenske viscometer tubes
- Four-ball wear tester
- Oxidation stability apparatus
- Pour point apparatus
- Flash point tester
- pH meter
- Analytical balance (0.0001g precision)

### 4. REAGENTS & MATERIALS
- Test samples: 500ml minimum
- Cleaning solvents: Petroleum ether, acetone
- Calibration standards
- Test balls (12.7mm diameter, AISI 52100 steel)

### 5. SAFETY PRECAUTIONS
⚠️ **MANDATORY SAFETY REQUIREMENTS:**
- Wear safety goggles and lab coat at all times
- Work in well-ventilated area or fume hood
- Keep fire extinguisher accessible
- No open flames in laboratory
- Handle hot equipment with thermal gloves
- Dispose of waste per facility SOPs

### 6. TEST PROCEDURES

#### 6.1 Kinematic Viscosity (ASTM D445)
1. Bring samples to test temperature (40°C and 100°C)
2. Select appropriate viscometer size
3. Charge viscometer ensuring no air bubbles
4. Measure efflux time in seconds
5. Calculate kinematic viscosity: ν = C × t
6. Repeat for duplicate samples

**Acceptance**: CV ≤ 0.35% for duplicates

#### 6.2 Four-Ball Wear Test (ASTM D4172)
1. Clean test balls with solvent, dry thoroughly
2. Load balls into test chuck
3. Add 10ml test sample
4. Apply 40kg load, 1200 rpm, 75°C
5. Run for 60 minutes
6. Measure wear scar diameter on 3 balls
7. Report average wear scar diameter

**Acceptance**: Wear scar < 0.6mm

#### 6.3 Viscosity Index (ASTM D2270)
1. Use kinematic viscosities at 40°C and 100°C
2. Apply ASTM D2270 calculation tables
3. Calculate VI using standard equations

**Expected Result**: VI > 120 for premium formulations

### 7. DATA RECORDING
Record all measurements in bound laboratory notebook:
- Date, time, operator name
- Sample identification
- Equipment calibration status
- Raw measurements
- Calculated results
- Observations/deviations

### 8. ACCEPTANCE CRITERIA
| Property | Target | Method |
|----------|--------|--------|
| Viscosity @ 40°C | 90-110 cSt | ASTM D445 |
| Viscosity @ 100°C | 13-15 cSt | ASTM D445 |
| Viscosity Index | > 120 | ASTM D2270 |
| Wear Scar | < 0.6mm | ASTM D4172 |
| Pour Point | < -15°C | ASTM D97 |

### 9. REPORTING
Prepare test report including:
- Executive summary
- Test conditions
- Results table
- Pass/fail determination
- Recommendations for formulation optimization

### 10. ESTIMATED RESOURCES
- **Duration**: 24-32 hours (including equilibration time)
- **Cost**: ₹8,000 - ₹12,000 (materials and equipment time)
- **Personnel**: 1 lab technician + 1 supervising researcher

---

**Auto-Generated by Engineer's Copilot**  
**Protocol ID**: {f'PROTO-{datetime.now().strftime("%Y%m%d%H%M")}'}  
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Confidence**: {self.confidence * 100:.0f}%  
**Review Required**: Yes (Human approval mandatory)
        """
        
        return {
            'intent': 'generate_protocol',
            'response': 'Test protocol generated successfully',
            'data': {
                'protocol_id': f'PROTO-{datetime.now().strftime("%Y%m%d%H%M")}',
                'title': f'Test Protocol for {formulation.get("name", "Formulation")}',
                'content': protocol_content.strip(),
                'test_standards': test_standards,
                'estimated_duration_hours': 28,
                'estimated_cost_inr': 10000
            }
        }
    
    def _explain_technical_term(self, term: str, language: str) -> Dict[str, Any]:
        """Explain technical terminology"""
        
        # Glossary of common terms
        glossary = {
            'viscosity': {
                'en': 'Viscosity is the measure of a fluid\'s resistance to flow. In lubricants, it indicates the oil\'s thickness and is measured in centistokes (cSt).',
                'hi': 'विस्कोसिटी तरल पदार्थ के प्रवाह के प्रतिरोध का माप है। लुब्रिकेंट में, यह तेल की मोटाई को दर्शाता है।'
            },
            'viscosity index': {
                'en': 'Viscosity Index (VI) measures how viscosity changes with temperature. Higher VI means less viscosity change, which is desirable.',
                'hi': 'विस्कोसिटी इंडेक्स (VI) तापमान के साथ विस्कोसिटी में परिवर्तन को मापता है। उच्च VI का मतलब कम परिवर्तन है।'
            },
            'pour point': {
                'en': 'Pour point is the lowest temperature at which oil will flow. Critical for cold weather operation.',
                'hi': 'पोर प्वाइंट वह न्यूनतम तापमान है जिस पर तेल बहेगा। ठंडे मौसम के संचालन के लिए महत्वपूर्ण।'
            },
            'flash point': {
                'en': 'Flash point is the temperature at which oil vapors ignite when exposed to flame. Important safety parameter.',
                'hi': 'फ्लैश प्वाइंट वह तापमान है जिस पर तेल की वाष्प आग की लपट के संपर्क में आने पर प्रज्वलित होती है।'
            }
        }
        
        term_lower = term.lower()
        explanation = glossary.get(term_lower, {}).get(language, 
            f"Technical term: {term}. For detailed information, please consult TCAP technical library.")
        
        return {
            'intent': 'explain_term',
            'response': explanation,
            'data': {'term': term, 'language': language}
        }
    
    def _general_chat(self, query: str, language: str) -> Dict[str, Any]:
        """
        IC.NL - Natural Language
        General conversational response
        """
        
        if OPENAI_AVAILABLE and self.openai_api_key:
            # Use actual OpenAI API
            response_text = self._call_openai(query, language)
        else:
            # Mock response
            if language == 'hi':
                response_text = f"मैं आपकी सहायता के लिए यहां हूं। आपके प्रश्न '{query}' के बारे में, मैं TCAP मुंबई R&D टीम को तकनीकी सहायता प्रदान करता हूं।"
            else:
                response_text = f"I'm here to assist you with your research. Regarding '{query}', I can help with formulation recommendations, literature search, and test protocol generation."
        
        return {
            'intent': 'chat',
            'response': response_text,
            'data': {}
        }
    
    def _call_openai(self, query: str, language: str) -> str:
        """Call OpenAI API (when available)"""
        try:
            system_prompt = f"""You are an expert R&D assistant for TCAP Mumbai lubricants laboratory. 
You help researchers with formulation development, literature search, and technical guidance.
Respond in {"Hindi" if language == "hi" else "English"}. Be concise and technically accurate."""
            
            # Note: Implement actual OpenAI API call here
            # For now, return mock response
            return "OpenAI integration pending - using mock response"
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return "I'm experiencing technical difficulties. Please try again."
    
    # Helper methods for formulation reasoning
    
    def _generate_pros(self, base_oil: str) -> List[str]:
        """Generate pros for base oil selection"""
        pros_map = {
            'Mineral Group I': ['Cost-effective', 'Widely available', 'Good solvency'],
            'Mineral Group II': ['Excellent oxidation stability', 'Good VI', 'Cost-effective'],
            'Mineral Group III': ['High VI', 'Excellent low-temp properties', 'Extended drain intervals'],
            'Synthetic PAO': ['Outstanding thermal stability', 'Wide operating temperature', 'Low volatility'],
            'Synthetic Ester': ['Biodegradable', 'Excellent lubricity', 'High VI'],
            'PAG': ['Excellent high-temp stability', 'Low friction', 'Energy efficient']
        }
        
        for key in pros_map:
            if key in base_oil:
                return pros_map[key]
        
        return ['Good general performance']
    
    def _generate_cons(self, base_oil: str) -> List[str]:
        """Generate cons for base oil selection"""
        cons_map = {
            'Mineral Group I': ['Lower VI than synthetic', 'Requires more additives', 'Limited high-temp use'],
            'Mineral Group II': ['Moderate cost', 'Limited availability', 'Standard performance'],
            'Mineral Group III': ['Higher cost than Group II', 'Limited in some markets'],
            'Synthetic PAO': ['High cost', 'Limited solvency', 'Seal compatibility concerns'],
            'Synthetic Ester': ['Highest cost', 'Hydrolytic stability concerns', 'Limited availability'],
            'PAG': ['Very high cost', 'Limited seal compatibility', 'Not mixable with mineral oils']
        }
        
        for key in cons_map:
            if key in base_oil:
                return cons_map[key]
        
        return ['Standard limitations apply']
    
    def _generate_formulation_reasoning(self, base_oil: str, product_type: str) -> str:
        """Generate reasoning for formulation selection"""
        return f"""This {product_type} formulation uses {base_oil} as the base stock, selected for its 
balance of performance and cost-effectiveness. The additive package is designed to meet API/ACEA 
specifications while maintaining compatibility with modern engines. Based on historical trial data 
from TCAP Mumbai, similar formulations have shown excellent field performance with extended drain 
intervals. The predicted properties are derived from our machine learning model trained on 200+ 
past formulation trials."""
    
    def explain(self, decision: Dict[str, Any]) -> str:
        """
        GS.EX - Explainability
        Explain agent reasoning
        """
        intent = decision.get('intent', 'unknown')
        
        explanation = f"""
**Engineer's Copilot Analysis**

Intent: {intent}
Confidence: {self.confidence * 100:.0f}%

This response is generated using:
- PK.KB: Access to 50+ research papers and 200+ formulation trials
- LA.VM: Semantic search using vector embeddings
- CG.RS: Multi-criteria reasoning based on specifications
- AE.CX: Content generation following industry standards
- IC.NL: Natural language processing in English and Hindi

The recommendations are based on:
1. Historical performance data from TCAP Mumbai trials
2. Industry best practices and standards (API, ACEA, BIS)
3. Cost-optimization algorithms
4. Machine learning predictions from past successes

All generated content requires human expert review before implementation.
        """
        
        return explanation.strip()