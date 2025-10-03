"""
Specialized Agents - Domain experts for formulation, testing, compliance, supply chain, and knowledge mining.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
import random
from .mock_systems import mock_sap, mock_lims, mock_plm, mock_regulatory, mock_supplier
from .event_simulator import SystemEvent, EventType, event_simulator


class FormulationAgent:
    """
    The Formulation Agent is our AI chemist. It analyzes requirements and
    recommends lubricant formulations by considering:
    - Performance requirements (viscosity, wear protection, etc.)
    - Cost constraints
    - Historical test data
    - Material availability
    - Regulatory compliance
    
    In a production system, this would use machine learning models trained on
    decades of R&D data. Our simulation uses realistic heuristics that mirror
    how experienced formulators think about the problem.
    """
    
    def __init__(self):
        self.agent_id = "formulation-agent-001"
        self.capabilities = ['formulation_optimization', 'cost_analysis', 'performance_prediction']
    
    async def analyze_requirements(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze formulation requirements and gather data from multiple sources.
        This is the "research" phase where we collect all the information needed
        to make good recommendations.
        """
        # Emit event for tracking
        analysis_start = SystemEvent(
            event_type=EventType.AGENT_ANALYSIS_START,
            source_system=self.agent_id,
            payload={'phase': 'requirements_analysis', 'requirements': requirements}
        )
        event_simulator.emit_event(analysis_start)
        
        # Query SAP for available materials and costs
        sap_materials = await mock_sap.query_materials({'material_type': 'all'})
        sap_costs = await mock_sap.get_material_costs([
            'BO-GRP2-001', 'BO-GRP3-002', 'BO-PAO4-003',
            'ADD-ZDDP-001', 'ADD-CASUL-002', 'ADD-PIB-003'
        ])
        
        # Query LIMS for historical performance data
        product_type = requirements.get('product_type', '5W-30')
        lims_history = await mock_lims.query_historical_tests({
            'product_type': product_type,
            'min_viscosity_index': requirements.get('min_viscosity_index', 140)
        })
        
        # Query PLM for product specifications
        plm_specs = await mock_plm.get_product_specification(product_type)
        
        # Check regulatory requirements
        standards = requirements.get('standards', ['API SN Plus', 'ACEA C3'])
        regulatory_check = await mock_regulatory.check_compliance({}, standards)
        
        # Compile analysis results
        analysis_results = {
            'requirements': requirements,
            'available_materials': sap_materials,
            'cost_data': sap_costs,
            'historical_performance': lims_history,
            'product_specifications': plm_specs,
            'regulatory_requirements': regulatory_check,
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        # Emit completion event
        analysis_complete = SystemEvent(
            event_type=EventType.AGENT_ANALYSIS_COMPLETE,
            source_system=self.agent_id,
            payload={'phase': 'requirements_analysis', 'data_sources': 5}
        )
        event_simulator.emit_event(analysis_complete)
        
        return analysis_results
    
    async def generate_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate multiple formulation recommendations based on the analysis.
        
        In production, this would use ML models to predict performance. Here,
        we use intelligent simulation that considers trade-offs between cost,
        performance, and availability - just like a real formulation chemist.
        
        We typically generate 3 options:
        1. Best Performance (premium materials, higher cost)
        2. Balanced (good performance, moderate cost)
        3. Cost-Optimized (meets specs at lowest cost)
        """
        requirements = analysis['requirements']
        product_type = requirements.get('product_type', '5W-30')
        
        # Simulate ML model inference time
        await asyncio.sleep(random.uniform(0.2, 0.4))
        
        recommendations = []
        
        # Option 1: Premium formulation using PAO base
        premium = {
            'formulation_id': f'FORM-PREM-{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'name': f'{product_type} - Premium Synthetic',
            'recommendation_rank': 1,
            'strategy': 'best_performance',
            'composition': {
                'base_oil': {
                    'type': 'PAO 4 + PAO 6 Blend',
                    'percentage': 72.5,
                    'cost_per_liter': 175.0
                },
                'additives': [
                    {'name': 'ZDDP Anti-wear', 'percentage': 1.2, 'cost_per_liter': 5.40},
                    {'name': 'Calcium Sulfonate', 'percentage': 2.5, 'cost_per_liter': 8.00},
                    {'name': 'PIB Viscosity Modifier', 'percentage': 8.0, 'cost_per_liter': 22.40},
                    {'name': 'Antifoam', 'percentage': 0.01, 'cost_per_liter': 0.09},
                    {'name': 'Rust Preventative', 'percentage': 0.5, 'cost_per_liter': 1.90}
                ]
            },
            'predicted_properties': {
                'viscosity_40c': 62.5,
                'viscosity_100c': 11.5,
                'viscosity_index': 158,
                'pour_point_c': -42,
                'wear_scar_mm': 0.35,
                'performance_score': 94.5
            },
            'total_cost_per_liter_inr': 212.79,
            'confidence_score': 0.92,
            'pros': [
                'Excellent low-temperature performance',
                'Superior wear protection',
                'Extended drain intervals possible',
                'Thermal stability at high temperatures'
            ],
            'cons': [
                'Higher material cost',
                'Longer lead time for PAO sourcing',
                'Premium positioning required'
            ],
            'estimated_success_probability': 0.95,
            'development_time_weeks': 8
        }
        recommendations.append(premium)
        
        # Option 2: Balanced formulation using Group III base
        balanced = {
            'formulation_id': f'FORM-BAL-{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'name': f'{product_type} - Advanced Synthetic',
            'recommendation_rank': 2,
            'strategy': 'balanced',
            'composition': {
                'base_oil': {
                    'type': 'Group III Syn150',
                    'percentage': 75.0,
                    'cost_per_liter': 78.0
                },
                'additives': [
                    {'name': 'ZDDP Anti-wear', 'percentage': 1.2, 'cost_per_liter': 5.40},
                    {'name': 'Calcium Sulfonate', 'percentage': 2.5, 'cost_per_liter': 8.00},
                    {'name': 'PIB Viscosity Modifier', 'percentage': 7.5, 'cost_per_liter': 21.00},
                    {'name': 'Antifoam', 'percentage': 0.01, 'cost_per_liter': 0.09},
                    {'name': 'Rust Preventative', 'percentage': 0.5, 'cost_per_liter': 1.90}
                ]
            },
            'predicted_properties': {
                'viscosity_40c': 64.0,
                'viscosity_100c': 11.2,
                'viscosity_index': 152,
                'pour_point_c': -38,
                'wear_scar_mm': 0.42,
                'performance_score': 88.5
            },
            'total_cost_per_liter_inr': 114.39,
            'confidence_score': 0.88,
            'pros': [
                'Good balance of cost and performance',
                'Readily available materials',
                'Meets all major specifications',
                'Competitive pricing possible'
            ],
            'cons': [
                'Moderate wear protection vs. PAO',
                'Standard low-temperature performance'
            ],
            'estimated_success_probability': 0.91,
            'development_time_weeks': 6
        }
        recommendations.append(balanced)
        
        # Option 3: Cost-optimized formulation using Group II base
        economy = {
            'formulation_id': f'FORM-ECO-{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'name': f'{product_type} - Value Formulation',
            'recommendation_rank': 3,
            'strategy': 'cost_optimized',
            'composition': {
                'base_oil': {
                    'type': 'Group II 150N',
                    'percentage': 76.0,
                    'cost_per_liter': 52.5
                },
                'additives': [
                    {'name': 'ZDDP Anti-wear', 'percentage': 1.2, 'cost_per_liter': 5.40},
                    {'name': 'Calcium Sulfonate', 'percentage': 2.5, 'cost_per_liter': 8.00},
                    {'name': 'PIB Viscosity Modifier', 'percentage': 7.0, 'cost_per_liter': 19.60},
                    {'name': 'Antifoam', 'percentage': 0.01, 'cost_per_liter': 0.09},
                    {'name': 'Rust Preventative', 'percentage': 0.5, 'cost_per_liter': 1.90}
                ]
            },
            'predicted_properties': {
                'viscosity_40c': 66.0,
                'viscosity_100c': 10.9,
                'viscosity_index': 148,
                'pour_point_c': -35,
                'wear_scar_mm': 0.48,
                'performance_score': 82.0
            },
            'total_cost_per_liter_inr': 87.49,
            'confidence_score': 0.85,
            'pros': [
                'Lowest material cost',
                'Immediate material availability',
                'Meets minimum specifications',
                'Fast to market'
            ],
            'cons': [
                'Lower viscosity index',
                'Basic performance level',
                'May require more frequent changes'
            ],
            'estimated_success_probability': 0.87,
            'development_time_weeks': 4
        }
        recommendations.append(economy)
        
        # Emit recommendation event
        rec_event = SystemEvent(
            event_type=EventType.AGENT_RECOMMENDATION_READY,
            source_system=self.agent_id,
            payload={
                'recommendations_count': len(recommendations),
                'product_type': product_type
            }
        )
        event_simulator.emit_event(rec_event)
        
        return recommendations


class TestProtocolAgent:
    """
    The Test Protocol Agent automates the generation of laboratory test procedures.
    
    Testing lubricants is a complex, multi-step process that must follow strict
    standards like ASTM (American Society for Testing and Materials) or BIS
    (Bureau of Indian Standards). This agent knows all these standards and can
    generate complete test protocols automatically.
    
    Think of this as an automated technical writer that knows all the lab procedures.
    """
    
    def __init__(self):
        self.agent_id = "test-protocol-agent-001"
        self.capabilities = ['protocol_generation', 'resource_planning', 'standards_mapping']
    
    async def generate_protocol(self, formulation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a complete test protocol for a formulation. This includes:
        - Which tests to run based on product type and claims
        - Step-by-step procedures
        - Equipment and resource requirements
        - Time and cost estimates
        """
        # Simulate protocol generation time
        await asyncio.sleep(random.uniform(0.15, 0.30))
        
        product_type = formulation.get('name', 'Unknown')
        
        # Get test protocols from LIMS
        viscosity_protocol = await mock_lims.get_test_protocols('viscosity')
        wear_protocol = await mock_lims.get_test_protocols('wear')
        
        protocol = {
            'protocol_id': f'PROT-{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'title': f'Test Protocol for {product_type}',
            'formulation_id': formulation.get('formulation_id'),
            'version': '1.0',
            'created_date': datetime.now().isoformat(),
            'test_sequence': [
                {
                    'test_number': 1,
                    'test_name': 'Kinematic Viscosity',
                    'standard': 'ASTM D445',
                    'temperature_points': ['40°C', '100°C'],
                    'equipment': 'Automated Viscosity Bath',
                    'duration_minutes': 45,
                    'cost_inr': 800,
                    'acceptance_criteria': viscosity_protocol['protocol'].get(
                        'precision', '±0.5%')
                },
                {
                    'test_number': 2,
                    'test_name': 'Viscosity Index',
                    'standard': 'ASTM D2270',
                    'calculation': 'From viscosity data',
                    'duration_minutes': 5,
                    'cost_inr': 0,
                    'acceptance_criteria': 'VI ≥ 140'
                },
                {
                    'test_number': 3,
                    'test_name': 'Pour Point',
                    'standard': 'ASTM D97',
                    'equipment': 'Pour Point Bath',
                    'duration_minutes': 120,
                    'cost_inr': 600,
                    'acceptance_criteria': '≤ -30°C'
                },
                {
                    'test_number': 4,
                    'test_name': 'Flash Point',
                    'standard': 'ASTM D92',
                    'equipment': 'Cleveland Open Cup',
                    'duration_minutes': 30,
                    'cost_inr': 500,
                    'acceptance_criteria': '≥ 200°C'
                },
                {
                    'test_number': 5,
                    'test_name': 'Four-Ball Wear Test',
                    'standard': 'ASTM D4172',
                    'conditions': '1200 rpm, 75°C, 1 hour, 40 kg load',
                    'equipment': 'Four-Ball Wear Tester',
                    'duration_minutes': 90,
                    'cost_inr': 2500,
                    'acceptance_criteria': wear_protocol['protocol'].get(
                        'acceptance_criteria', 'Wear scar < 0.6mm')
                },
                {
                    'test_number': 6,
                    'test_name': 'NOACK Volatility',
                    'standard': 'ASTM D5800',
                    'equipment': 'NOACK Apparatus',
                    'duration_minutes': 90,
                    'cost_inr': 3000,
                    'acceptance_criteria': '≤ 13% mass loss'
                }
            ],
            'total_duration_hours': 6.5,
            'total_cost_inr': 7400,
            'required_personnel': 2,
            'lab_space_required': 'Standard petrochemical lab',
            'safety_requirements': [
                'Fire extinguisher access',
                'Fume hood for volatile samples',
                'PPE: Lab coat, safety glasses, gloves',
                'Emergency shower and eyewash'
            ],
            'approval_workflow': {
                'created_by': self.agent_id,
                'requires_approval': True,
                'approvers': ['Lab Manager', 'QC Manager'],
                'estimated_approval_days': 2
            }
        }
        
        # Emit protocol generation event
        event = SystemEvent(
            event_type=EventType.PROTOCOL_REQUEST,
            source_system=self.agent_id,
            payload={'protocol_id': protocol['protocol_id']}
        )
        event_simulator.emit_event(event)
        
        return protocol


class RegulatoryComplianceAgent:
    """
    The Regulatory Compliance Agent ensures all formulations meet legal requirements.
    
    In the lubricants industry, there are hundreds of regulations, standards, and
    certifications that must be tracked. This agent monitors changes, checks compliance,
    and manages the certification process.
    
    Think of this as your regulatory affairs department automated.
    """
    
    def __init__(self):
        self.agent_id = "regulatory-agent-001"
        self.capabilities = ['compliance_checking', 'permit_tracking', 'standards_monitoring']
    
    async def check_compliance(
        self, 
        formulation: Dict[str, Any], 
        target_markets: List[str]
    ) -> Dict[str, Any]:
        """
        Check if a formulation complies with all regulatory requirements for
        the target markets. This is critical before starting production.
        """
        # Simulate compliance checking
        await asyncio.sleep(random.uniform(0.10, 0.20))
        
        # Check against regulatory databases
        standards = ['API SN Plus', 'ACEA C3', 'BIS IS 13656']
        regulatory_results = await mock_regulatory.check_compliance(formulation, standards)
        
        compliance_report = {
            'report_id': f'COMP-{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'formulation_id': formulation.get('formulation_id'),
            'check_date': datetime.now().isoformat(),
            'target_markets': target_markets,
            'regulatory_results': regulatory_results,
            'permits_required': [
                {
                    'permit_type': 'BIS Certification',
                    'issuing_authority': 'Bureau of Indian Standards',
                    'estimated_time_days': 45,
                    'cost_inr': 25000,
                    'status': 'pending_application'
                },
                {
                    'permit_type': 'PESO Petroleum License',
                    'issuing_authority': 'Petroleum and Explosives Safety Organisation',
                    'estimated_time_days': 30,
                    'cost_inr': 15000,
                    'status': 'pending_application'
                }
            ],
            'compliance_summary': {
                'overall_status': 'compliant_pending_certification',
                'critical_issues': 0,
                'warnings': 1,
                'recommended_actions': [
                    'Initiate BIS certification process',
                    'Submit PESO license application',
                    'Schedule API licensing review'
                ]
            }
        }
        
        # Emit compliance check event
        event = SystemEvent(
            event_type=EventType.COMPLIANCE_CHECK,
            source_system=self.agent_id,
            payload={'report_id': compliance_report['report_id']}
        )
        event_simulator.emit_event(event)
        
        return compliance_report


class SupplyChainAgent:
    """
    The Supply Chain Agent optimizes material sourcing and availability.
    
    Even the best formulation is useless if you can't get the materials to make it.
    This agent tracks supplier availability, pricing trends, lead times, and quality
    ratings to ensure recommendations are practical.
    
    Think of this as your procurement department working in real-time.
    """
    
    def __init__(self):
        self.agent_id = "supply-chain-agent-001"
        self.capabilities = ['availability_checking', 'price_optimization', 'supplier_rating']
    
    async def analyze_supply_chain(self, formulation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the supply chain feasibility of a formulation. This checks
        if all materials are available, assesses pricing, and identifies risks.
        """
        # Simulate supply chain analysis
        await asyncio.sleep(random.uniform(0.15, 0.30))
        
        # Extract materials from formulation
        materials = []
        composition = formulation.get('composition', {})
        if 'base_oil' in composition:
            materials.append(composition['base_oil']['type'])
        if 'additives' in composition:
            materials.extend([add['name'] for add in composition['additives']])
        
        # Check supplier availability
        supplier_data = await mock_supplier.check_availability(materials)
        
        # Get SAP availability data
        sap_availability = await mock_sap.check_supplier_availability([
            'BO-GRP2-001', 'ADD-ZDDP-001', 'ADD-CASUL-002'
        ])
        
        analysis = {
            'analysis_id': f'SC-{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'formulation_id': formulation.get('formulation_id'),
            'analysis_date': datetime.now().isoformat(),
            'materials_required': len(materials),
            'supplier_data': supplier_data,
            'sap_inventory': sap_availability,
            'supply_chain_score': random.uniform(0.75, 0.95),
            'risk_assessment': {
                'overall_risk': 'low',
                'risk_factors': [
                    {
                        'factor': 'Material Availability',
                        'risk_level': 'low',
                        'details': 'All materials in stock or short lead time'
                    },
                    {
                        'factor': 'Price Volatility',
                        'risk_level': 'medium',
                        'details': 'PAO prices showing upward trend'
                    },
                    {
                        'factor': 'Supplier Reliability',
                        'risk_level': 'low',
                        'details': 'All preferred suppliers rated > 90%'
                    }
                ]
            },
            'recommendations': [
                'Consider dual sourcing for PAO to mitigate price risk',
                'Negotiate volume discounts for PIB additive',
                'Monitor Group III pricing for potential savings'
            ]
        }
        
        # Emit supply chain analysis event
        event = SystemEvent(
            event_type=EventType.SUPPLIER_AVAILABILITY_CHECK,
            source_system=self.agent_id,
            payload={'analysis_id': analysis['analysis_id']}
        )
        event_simulator.emit_event(event)
        
        return analysis


class KnowledgeMiningAgent:
    """
    The Knowledge Mining Agent searches through research literature and historical
    data to provide insights.
    
    With 30+ years of R&D data, there's immense value in past research. This agent
    can find relevant papers, extract insights, and identify patterns that inform
    new formulations.
    
    Think of this as your research librarian who has read everything and can
    instantly find relevant information.
    """
    
    def __init__(self):
        self.agent_id = "knowledge-mining-agent-001"
        self.capabilities = ['literature_search', 'pattern_recognition', 'insight_extraction']
    
    async def search_research_literature(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search through research papers and historical data to find relevant
        insights for the current formulation challenge.
        """
        # Simulate research search
        await asyncio.sleep(random.uniform(0.10, 0.25))
        
        # Query LIMS for historical data
        product_type = query.get('product_type', '5W-30')
        lims_results = await mock_lims.query_historical_tests({
            'product_type': product_type
        })
        
        research_results = {
            'search_id': f'RES-{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'query': query,
            'search_date': datetime.now().isoformat(),
            'historical_tests': lims_results,
            'relevant_papers': [
                {
                    'paper_id': 'TCAP-1998-042',
                    'title': 'Optimization of 5W-30 Formulations Using Group III Base Stocks',
                    'authors': ['Dr. R. Sharma', 'Dr. P. Kumar'],
                    'year': 1998,
                    'relevance_score': 0.92,
                    'key_findings': [
                        'Group III at 75% provides optimal VI/cost balance',
                        'ZDDP at 1.2% sufficient for wear protection',
                        'PIB must be >7% for shear stability'
                    ]
                },
                {
                    'paper_id': 'TCAP-2015-128',
                    'title': 'Impact of PAO Blends on Low Temperature Performance',
                    'authors': ['Dr. S. Patel', 'Dr. M. Singh'],
                    'year': 2015,
                    'relevance_score': 0.88,
                    'key_findings': [
                        'PAO4/PAO6 blend superior to single grade',
                        'Pour point improves by 5-7°C with PAO',
                        'Cost premium justified for premium segment'
                    ]
                }
            ],
            'insights': {
                'patterns_identified': 3,
                'success_factors': [
                    'Historical success rate increases with VI > 150',
                    'Group III formulations show 85% first-time success',
                    'Cost target of ₹90-120/L achieves market acceptance'
                ],
                'failure_modes': [
                    'Insufficient VM leads to shear instability',
                    'Low-quality Group II causes oxidation issues',
                    'Inadequate detergency causes deposit formation'
                ]
            }
        }
        
        return research_results


# Create singleton instances
formulation_agent = FormulationAgent()
test_protocol_agent = TestProtocolAgent()
regulatory_agent = RegulatoryComplianceAgent()
supply_chain_agent = SupplyChainAgent()
knowledge_mining_agent = KnowledgeMiningAgent()
