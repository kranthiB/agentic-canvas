"""
Demo 2: GridMind AI Blueprint
T4 Multi-Agent Generative System routes
"""
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from datetime import datetime

from app import db
from app.models.demo2_models import (
    PlantState, AgentDecision, AgentCommunication,
    ConsensusRound, MaintenanceSchedule, PlantStatus
)
from app.agents.demo2_agents import MultiAgentCoordinator
from app.core.simulator import simulator

demo2_bp = Blueprint('demo2', __name__)

# Initialize multi-agent system
coordinator = MultiAgentCoordinator()


@demo2_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    # Get latest plant state
    latest_state = PlantState.query.order_by(
        PlantState.created_at.desc()
    ).first()
    
    # Get recent agent decisions
    recent_decisions = AgentDecision.query.order_by(
        AgentDecision.created_at.desc()
    ).limit(20).all()
    
    # Get latest consensus round
    from app.models.demo2_models import ConsensusRound
    latest_consensus = ConsensusRound.query.order_by(
        ConsensusRound.created_at.desc()
    ).first()
    
    # Create a default consensus if none exists
    if not latest_consensus:
        latest_consensus = {
            'method': 'voting',
            'decision': 'No consensus yet',
            'confidence': 0.0
        }
    
    # Structure agents data for template
    agents = {
        'weather': {
            'confidence': 87,
            'last_update': '2 mins ago',
            'status': 'active'
        },
        'demand': {
            'accuracy': 92,
            'last_update': '1 min ago',
            'status': 'active'
        },
        'storage': {
            'efficiency': 95,
            'last_update': '30 secs ago',
            'status': 'active'
        },
        'trading': {
            'roi': 8.5,
            'last_update': '5 mins ago',
            'status': 'active'
        },
        'maintenance': {
            'uptime': 99.2,
            'last_update': '10 mins ago',
            'status': 'active'
        }
    }
    
    return render_template(
        'demo2/dashboard.html',
        plant_state=latest_state,
        recent_decisions=recent_decisions,
        agents=agents,
        latest_consensus=latest_consensus
    )


@demo2_bp.route('/api/plant-state')
def api_plant_state():
    """Get current plant state"""
    state = simulator.get_state(demo_id=2)
    return jsonify(state)

@demo2_bp.route('/api/current-state')
def api_current_state():
    """Get current plant state for real-time updates"""
    latest_state = PlantState.query.order_by(
        PlantState.created_at.desc()
    ).first()
    
    if not latest_state:
        return jsonify({'error': 'No state available'}), 404
    
    return jsonify({
        'current_generation_mw': latest_state.current_generation_mw,
        'solar_generation_mw': latest_state.solar_generation_mw,
        'wind_generation_mw': latest_state.wind_generation_mw,
        'battery_soc_percent': latest_state.battery_soc_percent,
        'battery_power_mw': latest_state.battery_power_mw,
        'grid_demand_mw': latest_state.grid_demand_mw or 0,
        'market_price_per_mwh': latest_state.market_price_per_mwh or 0,
        'capacity_factor_percent': latest_state.capacity_factor_percent,
        'curtailment_percent': latest_state.curtailment_percent,
        'status': latest_state.status.value if hasattr(latest_state.status, 'value') else str(latest_state.status),
        'timestamp': latest_state.created_at.isoformat()
    })

@demo2_bp.route('/api/run-coordination', methods=['POST'])
@login_required
def api_run_coordination():
    """Run multi-agent coordination round"""
    # Get current plant state
    plant_state = simulator.get_state(demo_id=2)
    
    # Run coordination
    result = coordinator.run_coordination_round(plant_state)
    
    # Save plant state
    state_record = PlantState(
        solar_generation_mw=plant_state['solar_generation'],
        wind_generation_mw=plant_state['wind_generation'],
        total_generation_mw=plant_state['total_generation'],
        battery_soc=plant_state['battery_soc'],
        battery_power_mw=0,
        grid_frequency_hz=plant_state['grid_frequency'],
        market_price_inr_mwh=plant_state['market_price'],
        status=PlantStatus.NORMAL
    )
    state_record.save()
    
    # Save agent decisions
    for proposal in result['proposals']:
        decision = AgentDecision(
            agent_id=proposal['agent_id'],
            agent_type=proposal['agent_type'],
            decision_type='coordination_proposal',
            decision_data=proposal['proposal'],
            confidence_score=proposal['confidence'],
            plant_state_id=state_record.id
        )
        decision.save()
    
    # Save consensus round
    consensus = ConsensusRound(
        round_number=ConsensusRound.query.count() + 1,
        decision_topic='Plant optimization',
        proposals=[p['proposal'] for p in result['proposals']],
        consensus_reached=result['consensus']['consensus_reached'],
        final_decision=result['consensus'],
        convergence_time_ms=result['coordination_time_ms']
    )
    consensus.save()
    
    return jsonify({
        'success': True,
        'result': result,
        'state_id': state_record.id
    })


@demo2_bp.route('/agents')
@login_required
def agents():
    """Agent details page"""
    agents_info = [
        {
            'agent': coordinator.weather_agent,
            'name': 'Weather Forecast Agent',
            'type': 'T3 Cognitive',
            'capabilities': ['PK.OB', 'CG.PS', 'LA.SL'],
            'description': 'Predicts solar irradiance and wind speeds using historical patterns'
        },
        {
            'agent': coordinator.demand_agent,
            'name': 'Demand Prediction Agent',
            'type': 'T3 Cognitive',
            'capabilities': ['LA.SL', 'CG.RS', 'PK.KB'],
            'description': 'Forecasts grid demand patterns based on time and historical data'
        },
        {
            'agent': coordinator.storage_agent,
            'name': 'Storage Optimization Agent',
            'type': 'T3 Cognitive',
            'capabilities': ['CG.DC', 'AE.TX', 'LA.RL'],
            'description': 'Manages battery charging/discharging for grid stability and revenue'
        },
        {
            'agent': coordinator.trading_agent,
            'name': 'Market Trading Agent',
            'type': 'T3 Cognitive',
            'capabilities': ['CG.RS', 'AE.TL', 'LA.RL'],
            'description': 'Participates in real-time electricity markets for revenue optimization'
        },
        {
            'agent': coordinator.maintenance_agent,
            'name': 'Maintenance Coordinator Agent',
            'type': 'T2 Procedural',
            'capabilities': ['LA.MM', 'IC.CL', 'CG.PS'],
            'description': 'Schedules predictive maintenance to maximize asset longevity'
        }
    ]
    
    return render_template('demo2/agents.html', agents=agents_info)


@demo2_bp.route('/communication')
@login_required
def communication():
    """Agent communication log"""
    communications = AgentCommunication.query.order_by(
        AgentCommunication.created_at.desc()
    ).limit(50).all()
    
    return render_template('demo2/communication.html', communications=communications)


@demo2_bp.route('/maintenance')
@login_required
def maintenance():
    """Maintenance schedule"""
    schedules = MaintenanceSchedule.query.order_by(
        MaintenanceSchedule.scheduled_date
    ).all()
    
    return render_template('demo2/maintenance.html', schedules=schedules)


@demo2_bp.route('/digital-twin')
@login_required
def digital_twin():
    """Digital twin visualization"""
    return render_template('demo2/digital_twin.html')