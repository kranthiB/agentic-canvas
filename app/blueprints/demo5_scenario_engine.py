"""
Dynamic Scenario Engine for Demo5
Uses persisted database data to create realistic scenarios
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required
from datetime import datetime
import random
from typing import Dict, List, Any

from app import db
from app.models.demo5_models import (
    TEProduct, TETechnicalDoc, TEFormulationTrial,
    TESAPInventory, TELIMSTest, TESupplier,
    TEQueryHistory, TEEventTrace, TEAgentActivity
)

# Create blueprint
scenario_bp = Blueprint('demo5_scenarios', __name__)


class ScenarioGenerator:
    """
    Generates realistic scenarios based on actual database data.
    No hardcoded redundancy - everything comes from persisted data!
    """
    
    def __init__(self):
        self.scenario_templates = {
            'formulation_query': self._generate_formulation_scenario,
            'supplier_availability': self._generate_supplier_scenario,
            'quality_investigation': self._generate_quality_scenario,
            'new_product_dev': self._generate_product_dev_scenario
        }
    
    def _generate_formulation_scenario(self) -> Dict[str, Any]:
        """Generate scenario from actual formulation trials"""
        trial = TEFormulationTrial.query.filter_by(status='approved').first()
        product = TEProduct.query.filter(TEProduct.product_name.contains('Quartz')).first()
        
        if not trial or not product:
            return None
        
        return {
            'id': 'DB_FORMULATION',
            'name': f'Formulation Query - {product.product_name}',
            'category': 'Single Agent',
            'query': f"What's the recommended formulation for {product.product_name}?",
            'agents': ['formulation-agent-001'],
            'systems': ['Vector_DB', 'PLM'],
            'flow': [
                {'from': 'UI', 'to': 'Unified Gateway', 'delay': 200, 'event': 'user_query', 
                 'description': 'Engineer requests formulation data'},
                {'from': 'Unified Gateway', 'to': 'Orchestrator', 'delay': 300, 'event': 'query_routing', 
                 'description': 'Routing to orchestrator'},
                {'from': 'Orchestrator', 'to': 'FormulationAgent', 'delay': 400, 'event': 'agent_invocation', 
                 'description': 'Formulation agent activated'},
                {'from': 'FormulationAgent', 'to': 'RAG_Engine', 'delay': 500, 'event': 'knowledge_search', 
                 'description': f'Searching for {product.product_name} formulations'},
                {'from': 'RAG_Engine', 'to': 'Vector_DB', 'delay': 400, 'event': 'vector_search', 
                 'description': 'Retrieving similar formulation trials'},
                {'from': 'FormulationAgent', 'to': 'MCP_Gateway', 'delay': 300, 'event': 'mcp_connection', 
                 'description': 'Connecting to PLM'},
                {'from': 'MCP_Gateway', 'to': 'PLM', 'delay': 600, 'event': 'plm_specification_query', 
                 'description': f'Querying PLM for {product.product_code} specs'},
                {'from': 'PLM', 'to': 'MCP_Gateway', 'delay': 500, 'event': 'plm_response', 
                 'description': 'Retrieved product specifications'},
                {'from': 'FormulationAgent', 'to': 'LLM_Models', 'delay': 1200, 'event': 'llm_inference', 
                 'description': 'AI analyzing formulation data'},
                {'from': 'LLM_Models', 'to': 'FormulationAgent', 'delay': 800, 'event': 'llm_response', 
                 'description': 'Generated formulation recommendation'},
                {'from': 'FormulationAgent', 'to': 'Orchestrator', 'delay': 300, 'event': 'agent_recommendation_ready', 
                 'description': 'Analysis complete'},
                {'from': 'Orchestrator', 'to': 'Unified Gateway', 'delay': 200, 'event': 'response_aggregation', 
                 'description': 'Preparing response'},
                {'from': 'Unified Gateway', 'to': 'UI', 'delay': 300, 'event': 'response_delivery', 
                 'description': 'Delivering recommendation'}
            ],
            'result': {
                'product': product.product_name,
                'trial_code': trial.trial_code,
                'formulation': trial.formulation,
                'test_results': trial.test_results,
                'status': trial.status,
                'engineer': trial.engineer_name
            }
        }
    
    def _generate_supplier_scenario(self) -> Dict[str, Any]:
        """Generate scenario from actual supplier and inventory data"""
        material = TESAPInventory.query.filter_by(material_category='base_oil').first()
        suppliers = TESupplier.query.filter(TESupplier.material_type.contains('Base Oil')).all()
        
        if not material or not suppliers:
            return None
        
        return {
            'id': 'DB_SUPPLIER',
            'name': f'Supplier Availability - {material.material_name}',
            'category': 'Single Agent',
            'query': f"We need {material.material_name}. Which suppliers can deliver quickly?",
            'agents': ['supply-chain-agent-001'],
            'systems': ['SAP_ERP', 'Supplier_Portal'],
            'flow': [
                {'from': 'UI', 'to': 'Unified Gateway', 'delay': 200, 'event': 'user_query', 
                 'description': 'Procurement request submitted'},
                {'from': 'Unified Gateway', 'to': 'Orchestrator', 'delay': 300, 'event': 'query_routing', 
                 'description': 'Routing to orchestrator'},
                {'from': 'Orchestrator', 'to': 'SupplyChainAgent', 'delay': 400, 'event': 'agent_invocation', 
                 'description': 'Supply chain agent activated'},
                {'from': 'SupplyChainAgent', 'to': 'MCP_Gateway', 'delay': 300, 'event': 'mcp_connection', 
                 'description': 'Connecting to SAP ERP'},
                {'from': 'MCP_Gateway', 'to': 'SAP_ERP', 'delay': 600, 'event': 'sap_inventory_check', 
                 'description': f'Checking stock for {material.material_code}'},
                {'from': 'SAP_ERP', 'to': 'MCP_Gateway', 'delay': 500, 'event': 'sap_response', 
                 'description': f'Current stock: {material.stock_quantity} {material.unit}'},
                {'from': 'MCP_Gateway', 'to': 'Supplier_Portal', 'delay': 700, 'event': 'supplier_availability_check', 
                 'description': f'Querying {len(suppliers)} approved suppliers'},
                {'from': 'Supplier_Portal', 'to': 'MCP_Gateway', 'delay': 600, 'event': 'supplier_response', 
                 'description': f'Found {len(suppliers)} suppliers with capacity'},
                {'from': 'SupplyChainAgent', 'to': 'LLM_Models', 'delay': 1000, 'event': 'llm_inference', 
                 'description': 'Analyzing supplier options and lead times'},
                {'from': 'LLM_Models', 'to': 'SupplyChainAgent', 'delay': 800, 'event': 'llm_response', 
                 'description': 'Generated supplier recommendation'},
                {'from': 'SupplyChainAgent', 'to': 'Orchestrator', 'delay': 300, 'event': 'agent_recommendation_ready', 
                 'description': 'Supply chain analysis complete'},
                {'from': 'Orchestrator', 'to': 'Unified Gateway', 'delay': 200, 'event': 'response_aggregation', 
                 'description': 'Aggregating supplier data'},
                {'from': 'Unified Gateway', 'to': 'UI', 'delay': 300, 'event': 'response_delivery', 
                 'description': 'Delivering supplier options'}
            ],
            'result': {
                'material': material.material_name,
                'current_stock': f"{material.stock_quantity} {material.unit}",
                'current_supplier': material.supplier,
                'price': f"₹{material.price}",
                'alternative_suppliers': [
                    {
                        'name': s.supplier_name,
                        'location': s.location,
                        'lead_time': f"{s.lead_time_days} days",
                        'quality_rating': s.quality_rating
                    } for s in suppliers[:3]
                ]
            }
        }
    
    def _generate_quality_scenario(self) -> Dict[str, Any]:
        """Generate scenario from actual LIMS test failures"""
        failed_test = TELIMSTest.query.filter_by(pass_fail='FAIL').first()
        
        if not failed_test:
            return None
        
        return {
            'id': 'DB_QUALITY',
            'name': f'Quality Investigation - {failed_test.batch_code}',
            'category': 'Two Agent',
            'query': f"LIMS flagged batch {failed_test.batch_code} as FAIL. What's the issue?",
            'agents': ['test-protocol-agent-001', 'supply-chain-agent-001'],
            'systems': ['LIMS', 'SAP_ERP'],
            'flow': [
                {'from': 'UI', 'to': 'Unified Gateway', 'delay': 200, 'event': 'user_query', 
                 'description': 'Quality incident reported'},
                {'from': 'Unified Gateway', 'to': 'Orchestrator', 'delay': 300, 'event': 'query_routing', 
                 'description': 'Urgent quality investigation'},
                {'from': 'Orchestrator', 'to': 'TestProtocolAgent', 'delay': 400, 'event': 'agent_invocation', 
                 'description': 'Protocol agent analyzing test data'},
                {'from': 'TestProtocolAgent', 'to': 'MCP_Gateway', 'delay': 300, 'event': 'mcp_connection', 
                 'description': 'Connecting to LIMS'},
                {'from': 'MCP_Gateway', 'to': 'LIMS', 'delay': 800, 'event': 'lims_test_query', 
                 'description': f'Retrieving test history for {failed_test.batch_code}'},
                {'from': 'LIMS', 'to': 'MCP_Gateway', 'delay': 600, 'event': 'lims_response', 
                 'description': f'Test FAILED: {failed_test.notes}'},
                {'from': 'Orchestrator', 'to': 'SupplyChainAgent', 'delay': 400, 'event': 'agent_invocation', 
                 'description': 'Supply chain tracing raw materials'},
                {'from': 'SupplyChainAgent', 'to': 'MCP_Gateway', 'delay': 300, 'event': 'mcp_connection', 
                 'description': 'Connecting to SAP for traceability'},
                {'from': 'MCP_Gateway', 'to': 'SAP_ERP', 'delay': 900, 'event': 'sap_material_query', 
                 'description': f'Tracing materials for batch {failed_test.batch_code}'},
                {'from': 'SAP_ERP', 'to': 'MCP_Gateway', 'delay': 700, 'event': 'sap_response', 
                 'description': 'Retrieved batch material traceability'},
                {'from': 'SupplyChainAgent', 'to': 'LLM_Models', 'delay': 1200, 'event': 'llm_inference', 
                 'description': 'AI analyzing contamination source'},
                {'from': 'TestProtocolAgent', 'to': 'Orchestrator', 'delay': 300, 'event': 'agent_recommendation_ready', 
                 'description': 'Root cause identified'},
                {'from': 'SupplyChainAgent', 'to': 'Orchestrator', 'delay': 300, 'event': 'agent_recommendation_ready', 
                 'description': 'Affected batches identified'},
                {'from': 'Orchestrator', 'to': 'Unified Gateway', 'delay': 400, 'event': 'response_aggregation', 
                 'description': 'Preparing corrective action plan'},
                {'from': 'Unified Gateway', 'to': 'UI', 'delay': 300, 'event': 'response_delivery', 
                 'description': 'Delivering investigation results'}
            ],
            'result': {
                'batch_code': failed_test.batch_code,
                'product': failed_test.product_code,
                'test_type': failed_test.test_type,
                'test_date': failed_test.test_date.isoformat(),
                'failure_reason': failed_test.notes,
                'test_results': failed_test.results,
                'analyst': failed_test.analyst,
                'status': 'QUARANTINED'
            }
        }
    
    def _generate_product_dev_scenario(self) -> Dict[str, Any]:
        """Generate new product development scenario"""
        product = TEProduct.query.filter_by(status='active').first()
        doc = TETechnicalDoc.query.filter_by(doc_type='test_protocol').first()
        
        if not product or not doc:
            return None
        
        return {
            'id': 'DB_PRODUCT_DEV',
            'name': f'New Product Development',
            'category': 'Three Agent',
            'query': f"Develop a new variant of {product.product_name} for heavy-duty applications",
            'agents': ['formulation-agent-001', 'test-protocol-agent-001', 'regulatory-agent-001'],
            'systems': ['Vector_DB', 'PLM', 'LIMS', 'Regulatory_DB'],
            'flow': [
                {'from': 'UI', 'to': 'Unified Gateway', 'delay': 200, 'event': 'user_query', 
                 'description': 'New product development request'},
                {'from': 'Unified Gateway', 'to': 'Orchestrator', 'delay': 300, 'event': 'query_routing', 
                 'description': 'Multi-agent coordination required'},
                {'from': 'Orchestrator', 'to': 'FormulationAgent', 'delay': 400, 'event': 'agent_invocation', 
                 'description': 'Formulation agent designing base formulation'},
                {'from': 'FormulationAgent', 'to': 'RAG_Engine', 'delay': 600, 'event': 'knowledge_search', 
                 'description': 'Researching heavy-duty formulations'},
                {'from': 'RAG_Engine', 'to': 'Vector_DB', 'delay': 500, 'event': 'vector_search', 
                 'description': 'Finding similar product formulations'},
                {'from': 'FormulationAgent', 'to': 'LLM_Models', 'delay': 1800, 'event': 'llm_inference', 
                 'description': 'AI designing optimized formulation'},
                {'from': 'Orchestrator', 'to': 'TestProtocolAgent', 'delay': 400, 'event': 'agent_invocation', 
                 'description': 'Protocol agent defining test requirements'},
                {'from': 'TestProtocolAgent', 'to': 'MCP_Gateway', 'delay': 300, 'event': 'mcp_connection', 
                 'description': 'Accessing LIMS test protocols'},
                {'from': 'MCP_Gateway', 'to': 'LIMS', 'delay': 800, 'event': 'lims_test_query', 
                 'description': 'Retrieving mandatory test protocols'},
                {'from': 'TestProtocolAgent', 'to': 'LLM_Models', 'delay': 1500, 'event': 'llm_inference', 
                 'description': 'Creating comprehensive test plan'},
                {'from': 'Orchestrator', 'to': 'RegulatoryAgent', 'delay': 400, 'event': 'agent_invocation', 
                 'description': 'Regulatory agent checking compliance'},
                {'from': 'RegulatoryAgent', 'to': 'MCP_Gateway', 'delay': 300, 'event': 'mcp_connection', 
                 'description': 'Querying regulatory database'},
                {'from': 'MCP_Gateway', 'to': 'Regulatory_DB', 'delay': 900, 'event': 'regulatory_standard_check', 
                 'description': 'Checking certification requirements'},
                {'from': 'RegulatoryAgent', 'to': 'LLM_Models', 'delay': 1600, 'event': 'llm_inference', 
                 'description': 'Analyzing compliance pathway'},
                {'from': 'FormulationAgent', 'to': 'Orchestrator', 'delay': 300, 'event': 'agent_recommendation_ready', 
                 'description': 'Formulation ready'},
                {'from': 'TestProtocolAgent', 'to': 'Orchestrator', 'delay': 300, 'event': 'agent_recommendation_ready', 
                 'description': 'Test protocol ready'},
                {'from': 'RegulatoryAgent', 'to': 'Orchestrator', 'delay': 300, 'event': 'agent_recommendation_ready', 
                 'description': 'Compliance roadmap ready'},
                {'from': 'Orchestrator', 'to': 'Unified Gateway', 'delay': 500, 'event': 'response_aggregation', 
                 'description': 'Synthesizing complete development plan'},
                {'from': 'Unified Gateway', 'to': 'UI', 'delay': 300, 'event': 'response_delivery', 
                 'description': 'Delivering development roadmap'}
            ],
            'result': {
                'product_base': product.product_name,
                'new_variant': f"{product.product_name} HD (Heavy Duty)",
                'formulation_approach': 'Enhanced additive package for extreme pressure',
                'test_protocol': doc.title,
                'estimated_timeline': '6-9 months',
                'certification_required': ['API CK-4', 'ACEA E9', 'BIS certification']
            }
        }
    
    def get_random_scenario(self) -> Dict[str, Any]:
        """Get a random scenario from available templates"""
        # Randomly pick a scenario type
        scenario_type = random.choice(list(self.scenario_templates.keys()))
        generator = self.scenario_templates[scenario_type]
        
        # Generate scenario from database
        scenario = generator()
        
        # If generation failed (no data), try another type
        if not scenario:
            for scenario_type in self.scenario_templates.keys():
                scenario = self.scenario_templates[scenario_type]()
                if scenario:
                    break
        
        return scenario


# Create global scenario generator
scenario_generator = ScenarioGenerator()


@scenario_bp.route('/api/scenarios/random', methods=['POST'])
@login_required
def simulate_random_scenario():
    """
    Pick a random scenario based on actual database data and simulate it
    """
    try:
        # Generate scenario from database
        scenario = scenario_generator.get_random_scenario()
        
        if not scenario:
            return jsonify({
                'success': False,
                'error': 'No data available to generate scenario. Please run: python scripts/seed_demo5.py'
            }), 500
        
        # Generate unique workflow ID
        workflow_id = f"WF-{scenario['id']}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Log the query
        query_history = TEQueryHistory(
            query_text=scenario['query'],
            query_text_hindi=scenario.get('query_hi', ''),
            query_category=scenario['category'],
            agents_involved=scenario['agents'],
            response=str(scenario['result']),
            language='english',
            session_id=workflow_id
        )
        db.session.add(query_history)
        
        # Create events for each step in the flow
        events = []
        cumulative_latency = 0
        
        for idx, step in enumerate(scenario['flow']):
            cumulative_latency += step['delay']
            
            event = TEEventTrace(
                correlation_id=workflow_id,
                event_type=step['event'],
                source_system=step['from'],
                target_system=step['to'],
                payload={
                    'scenario_id': scenario['id'],
                    'scenario_name': scenario['name'],
                    'step': idx + 1,
                    'total_steps': len(scenario['flow']),
                    'description': step['description'],
                    'delay_ms': step['delay']
                },
                processing_time_ms=cumulative_latency
            )
            db.session.add(event)
            events.append(event.to_dict())
        
        # Log agent activities
        for agent_name in scenario['agents']:
            activity = TEAgentActivity(
                agent_name=agent_name,
                action_type='scenario_execution',
                correlation_id=workflow_id,
                input_params={'scenario': scenario['id'], 'query': scenario['query']},
                output_data=scenario['result'],
                latency_ms=cumulative_latency,
                source_system='Orchestrator',
                target_system=agent_name
            )
            db.session.add(activity)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'workflow_id': workflow_id,
            'scenario': {
                'id': scenario['id'],
                'name': scenario['name'],
                'category': scenario['category'],
                'query': scenario['query'],
                'query_hi': scenario.get('query_hi', ''),
                'agents': scenario['agents'],
                'systems': scenario['systems'],
                'flow': scenario['flow'],
                'agents_count': len(scenario['agents']),
                'systems_count': len(scenario['systems']),
                'total_latency_ms': cumulative_latency
            },
            'events_count': len(events),
            'result': scenario['result']
        })
    
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"Error in simulate_random_scenario: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@scenario_bp.route('/api/scenarios/list', methods=['GET'])
@login_required
def list_scenarios():
    """Get all available scenario types"""
    return jsonify({
        'success': True,
        'scenarios': [
            {
                'id': 'formulation_query',
                'name': 'Formulation Query',
                'description': 'Query product formulations from database'
            },
            {
                'id': 'supplier_availability',
                'name': 'Supplier Availability',
                'description': 'Check supplier and inventory data'
            },
            {
                'id': 'quality_investigation',
                'name': 'Quality Investigation',
                'description': 'Investigate failed LIMS tests'
            },
            {
                'id': 'new_product_dev',
                'name': 'New Product Development',
                'description': 'Multi-agent product development'
            }
        ],
        'total': 4
    })
