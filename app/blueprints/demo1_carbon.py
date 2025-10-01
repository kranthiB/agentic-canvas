"""
Demo 1: Carbon Compass Blueprint
T3 Cognitive Autonomous Agent routes
"""
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import random

from app import db
from app.models.demo1_models import (
    CarbonBudget, EmissionReading, CarbonAction, 
    CounterfactualScenario, ActionType, EmissionStatus
)
from app.agents.demo1_agent import CarbonOptimizationAgent
from app.core.simulator import simulator

demo1_bp = Blueprint('demo1', __name__)

# Initialize agent
carbon_agent = CarbonOptimizationAgent()


@demo1_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    # Get or create current year budget
    current_year = datetime.now().year
    budget = CarbonBudget.query.filter_by(year=current_year).first()
    
    if not budget:
        budget = CarbonBudget(
            year=current_year,
            total_budget_mt=100000,
            consumed_mt=45.2,
            remaining_mt=54.8,
            status=EmissionStatus.NORMAL
        )
        budget.save()
    
    # Get recent readings
    recent_readings = EmissionReading.query.filter_by(
        budget_id=budget.id
    ).order_by(EmissionReading.created_at.desc()).limit(20).all()
    
    # Get recent actions
    recent_actions = CarbonAction.query.filter_by(
        budget_id=budget.id
    ).order_by(CarbonAction.created_at.desc()).limit(10).all()
    
    return render_template(
        'demo1/dashboard.html',
        budget=budget,
        recent_readings=recent_readings,
        recent_actions=recent_actions,
        agent_status=carbon_agent.get_status()
    )


@demo1_bp.route('/api/current-state')
def api_current_state():
    """Get current emissions state"""
    state = simulator.get_state(demo_id=1)
    
    current_year = datetime.now().year
    budget = CarbonBudget.query.filter_by(year=current_year).first()
    
    if budget:
        state['budget_total'] = budget.total_budget_mt
        state['budget_consumed'] = budget.consumed_mt
        state['budget_remaining'] = budget.remaining_mt
        state['budget_status'] = budget.status.value
    
    return jsonify(state)


@demo1_bp.route('/api/get-recommendation', methods=['POST'])
@login_required
def api_get_recommendation():
    """Get AI recommendation"""
    data = request.get_json()
    
    # Get current state
    environment = simulator.get_state(demo_id=1)
    environment['budget_remaining_mt'] = data.get('budget_remaining', 50)
    
    # Run agent cycle
    result = carbon_agent.run_cycle(environment)
    
    if result['success']:
        # Save action to database
        current_year = datetime.now().year
        budget = CarbonBudget.query.filter_by(year=current_year).first()
        
        if budget:
            action_data = result['result']
            action = CarbonAction(
                budget_id=budget.id,
                action_type=ActionType[action_data['action_type'].upper()],
                description=action_data['description'],
                expected_reduction_kg_hr=action_data['expected_reduction_kg_hr'],
                expected_cost=action_data['expected_cost'],
                reasoning=action_data['reasoning'],
                confidence_score=action_data['confidence_score'],
                agent_id=carbon_agent.agent_id,
                priority=action_data['priority']
            )
            action.save()
            
            return jsonify({
                'success': True,
                'action': action.to_dict(),
                'explanation': carbon_agent.explain(result['decision'])
            })
    
    return jsonify({'success': False, 'error': result.get('error', 'Unknown error')}), 500


@demo1_bp.route('/api/implement-action/', methods=['POST'])
@login_required
def api_implement_action(action_id):
    """Mark action as implemented"""
    action = CarbonAction.query.get_or_404(action_id)
    action.implement()
    
    # Simulate actual reduction (for demo)
    action.actual_reduction_kg_hr = action.expected_reduction_kg_hr * random.uniform(0.85, 1.05)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'action': action.to_dict()
    })


@demo1_bp.route('/counterfactual')
@login_required
def counterfactual():
    """Counterfactual analysis page"""
    scenarios = CounterfactualScenario.query.order_by(
        CounterfactualScenario.created_at.desc()
    ).limit(10).all()
    
    return render_template('demo1/counterfactual.html', scenarios=scenarios)


@demo1_bp.route('/api/generate-scenario', methods=['POST'])
@login_required
def api_generate_scenario():
    """Generate counterfactual scenario"""
    data = request.get_json()
    
    scenario_params = {
        'name': data.get('name', 'New Scenario'),
        'baseline_emissions_mt': data.get('baseline_emissions', 100),
        'actions': data.get('actions', [])
    }
    
    # Generate scenario using agent
    scenario_data = carbon_agent.generate_counterfactual(scenario_params)
    
    # Save to database
    current_year = datetime.now().year
    budget = CarbonBudget.query.filter_by(year=current_year).first()
    
    if budget:
        scenario = CounterfactualScenario(
            budget_id=budget.id,
            name=scenario_params['name'],
            description=data.get('description', ''),
            parameters=scenario_params,
            projected_emissions_mt=scenario_data['projected_emissions_mt'],
            projected_savings_mt=scenario_data['projected_savings_mt'],
            projected_cost=data.get('estimated_cost', 500000),
            feasibility_score=scenario_data['feasibility_score'],
            risk_level=scenario_data['risk_level']
        )
        scenario.save()
        
        return jsonify({
            'success': True,
            'scenario': scenario.to_dict()
        })
    
    return jsonify({'success': False, 'error': 'Budget not found'}), 404


@demo1_bp.route('/analytics')
@login_required
def analytics():
    """Analytics and reporting page"""
    current_year = datetime.now().year
    budget = CarbonBudget.query.filter_by(year=current_year).first()
    
    # Get historical data
    readings = EmissionReading.query.filter_by(
        budget_id=budget.id
    ).order_by(EmissionReading.created_at.desc()).limit(100).all()
    
    actions = CarbonAction.query.filter_by(
        budget_id=budget.id,
        implemented=True
    ).all()
    
    return render_template(
        'demo1/analytics.html',
        budget=budget,
        readings=readings,
        actions=actions
    )