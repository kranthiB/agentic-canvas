"""
Demo 4: Scenario Engine Blueprint
Executes multi-agent workflows and manages scenarios
"""
from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required
import asyncio
from datetime import datetime, timedelta

import logging

from app import db
from app.models.demo4_models import ChargingSite, CityTier
from app.models.demo4_extended_models import (
    TEEventTrace, TEAgentActivity
)
from app.simulation.demo4 import (
    ev_charging_orchestrator,
    event_simulator,
    message_queue
)

logger = logging.getLogger(__name__)

demo4_scenario_bp = Blueprint('demo4_scenario', __name__)





@demo4_scenario_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard - interactive map view"""
    return render_template('demo4/dashboard.html')


@demo4_scenario_bp.route('/scenario1')
@login_required
def scenario1():
    """Scenario 1: Mumbai Permit Crisis"""
    return render_template('demo4/scenario1.html')


@demo4_scenario_bp.route('/event-flow')
@login_required
def event_flow_page():
    """Event flow visualization page"""
    return render_template('demo4/event_flow.html')





@demo4_scenario_bp.route('/api/events/recent', methods=['GET'])
@login_required
def api_get_recent_events():
    """Get recent event traces"""
    limit = request.args.get('limit', 50, type=int)
    correlation_id = request.args.get('correlation_id')
    
    query = TEEventTrace.query
    
    if correlation_id:
        query = query.filter_by(correlation_id=correlation_id)
    
    events = query.order_by(TEEventTrace.timestamp.desc()).limit(limit).all()
    
    return jsonify({
        'success': True,
        'events': [e.to_dict() for e in events],
        'count': len(events)
    })


@demo4_scenario_bp.route('/api/events/by-workflow/<workflow_id>', methods=['GET'])
@login_required
def api_get_workflow_events(workflow_id):
    """Get all events for a specific workflow"""
    events = TEEventTrace.query.filter_by(
        correlation_id=workflow_id
    ).order_by(TEEventTrace.timestamp).all()
    
    activities = TEAgentActivity.query.filter_by(
        correlation_id=workflow_id
    ).order_by(TEAgentActivity.created_at).all()
    
    return jsonify({
        'success': True,
        'workflow_id': workflow_id,
        'events': [e.to_dict() for e in events],
        'agent_activities': [a.to_dict() for a in activities],
        'event_count': len(events),
        'total_duration_ms': sum(e.processing_time_ms or 0 for e in events)
    })


@demo4_scenario_bp.route('/api/events/realtime-stats', methods=['GET'])
@login_required
def api_realtime_stats():
    """Get real-time statistics"""
    # Get event counts
    total_events = TEEventTrace.query.count()
    
    # Get recent activity (last hour)
    one_hour_ago = datetime.now() - timedelta(hours=1)
    recent_events = TEEventTrace.query.filter(
        TEEventTrace.timestamp >= one_hour_ago
    ).count()
    
    # Get active workflows (last 5 minutes)
    five_min_ago = datetime.now() - timedelta(minutes=5)
    active_workflows = db.session.query(TEEventTrace.correlation_id).filter(
        TEEventTrace.timestamp >= five_min_ago
    ).distinct().count()
    
    # Get agent statistics
    agent_activities = TEAgentActivity.query.filter(
        TEAgentActivity.created_at >= one_hour_ago
    ).all()
    
    agent_stats = {}
    for activity in agent_activities:
        agent_type = activity.agent_type
        if agent_type not in agent_stats:
            agent_stats[agent_type] = {'count': 0, 'avg_time_ms': 0, 'total_time': 0}
        agent_stats[agent_type]['count'] += 1
        agent_stats[agent_type]['total_time'] += activity.execution_time_ms or 0
    
    # Calculate averages
    for agent_type in agent_stats:
        count = agent_stats[agent_type]['count']
        if count > 0:
            agent_stats[agent_type]['avg_time_ms'] = int(
                agent_stats[agent_type]['total_time'] / count
            )
    
    # Get system statistics
    orchestrator_stats = ev_charging_orchestrator.get_statistics()
    
    return jsonify({
        'success': True,
        'stats': {
            'total_events': total_events,
            'recent_events_1h': recent_events,
            'active_workflows': active_workflows,
            'agent_activities': len(agent_activities),
            'agent_breakdown': agent_stats,
            'orchestrator': orchestrator_stats
        },
        'timestamp': datetime.now().isoformat()
    })


@demo4_scenario_bp.route('/api/agents/activities', methods=['GET'])
@login_required
def api_get_agent_activities():
    """Get recent agent activities"""
    limit = request.args.get('limit', 20, type=int)
    agent_type = request.args.get('agent_type')
    
    query = TEAgentActivity.query
    
    if agent_type:
        query = query.filter_by(agent_type=agent_type)
    
    activities = query.order_by(TEAgentActivity.created_at.desc()).limit(limit).all()
    
    return jsonify({
        'success': True,
        'activities': [a.to_dict() for a in activities],
        'count': len(activities)
    })


@demo4_scenario_bp.route('/api/sites/evaluate-comprehensive', methods=['POST'])
@login_required
def api_evaluate_site_comprehensive():
    """Evaluate a site using all agents (comprehensive analysis)"""
    data = request.get_json()
    site_id = data.get('site_id')
    
    if not site_id:
        return jsonify({'success': False, 'error': 'site_id required'}), 400
    
    site = ChargingSite.query.filter_by(site_id=site_id).first()
    if not site:
        return jsonify({'success': False, 'error': 'Site not found'}), 404
    
    logger.info(f"Starting comprehensive evaluation for site {site_id}")
    
    try:
        # Run comprehensive evaluation
        result = asyncio.run(
            ev_charging_orchestrator.evaluate_site_comprehensive(site.to_dict())
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in comprehensive evaluation: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@demo4_scenario_bp.route('/api/network/optimize', methods=['POST'])
@login_required
def api_optimize_network():
    """Optimize network using orchestrator"""
    data = request.get_json()
    
    budget = data.get('budget', 100000000)
    target_sites = data.get('target_sites', 30)
    objective = data.get('objective', 'balanced')
    city_filter = data.get('city')
    tier_filter = data.get('tier')
    
    # Get candidate sites
    query = ChargingSite.query
    
    if city_filter:
        query = query.filter_by(city=city_filter)
    
    if tier_filter:
        query = query.filter_by(city_tier=CityTier[tier_filter.upper()])
    
    sites = query.limit(50).all()  # Limit for performance
    
    if not sites:
        return jsonify({'success': False, 'error': 'No candidate sites found'}), 404
    
    logger.info(f"Optimizing network with {len(sites)} candidate sites")
    
    try:
        result = asyncio.run(
            ev_charging_orchestrator.optimize_network_expansion(
                [s.to_dict() for s in sites],
                budget,
                target_sites,
                objective
            )
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in network optimization: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@demo4_scenario_bp.route('/api/scenario1/mumbai-cng-sites', methods=['GET'])
@login_required
def api_scenario1_mumbai_cng_sites():
    """Get Mumbai CNG crisis scenario data"""
    mumbai_cng_sites = [
        {'id': 'CNG-001', 'name': 'Nariman Point CNG Station', 'lat': 18.9254, 'lng': 72.8243, 'investment': 3.5, 'daysDelayed': 105},
        {'id': 'CNG-002', 'name': 'Andheri SEEPZ CNG Hub', 'lat': 19.1136, 'lng': 72.8697, 'investment': 3.2, 'daysDelayed': 108},
        {'id': 'CNG-003', 'name': 'Bandra West CNG Center', 'lat': 19.0596, 'lng': 72.8295, 'investment': 3.8, 'daysDelayed': 102},
        {'id': 'CNG-004', 'name': 'Powai Tech Park CNG Station', 'lat': 19.1197, 'lng': 72.9059, 'investment': 3.4, 'daysDelayed': 106},
        {'id': 'CNG-005', 'name': 'BKC CNG Refueling Center', 'lat': 19.0608, 'lng': 72.8683, 'investment': 4.2, 'daysDelayed': 110},
        {'id': 'CNG-006', 'name': 'Malad Industrial CNG Hub', 'lat': 19.1865, 'lng': 72.8486, 'investment': 3.1, 'daysDelayed': 103},
        {'id': 'CNG-007', 'name': 'Goregaon East CNG Station', 'lat': 19.1653, 'lng': 72.8526, 'investment': 3.0, 'daysDelayed': 101},
        {'id': 'CNG-008', 'name': 'Vikhroli CNG Center', 'lat': 19.1076, 'lng': 72.9248, 'investment': 2.9, 'daysDelayed': 107},
        {'id': 'CNG-009', 'name': 'Thane West CNG Hub', 'lat': 19.2183, 'lng': 72.9781, 'investment': 3.3, 'daysDelayed': 104},
        {'id': 'CNG-010', 'name': 'Navi Mumbai CNG Station', 'lat': 19.0330, 'lng': 73.0297, 'investment': 3.7, 'daysDelayed': 109},
        {'id': 'CNG-011', 'name': 'Lower Parel CNG Center', 'lat': 18.9968, 'lng': 72.8288, 'investment': 4.0, 'daysDelayed': 111},
        {'id': 'CNG-012', 'name': 'Worli CNG Refueling Station', 'lat': 19.0176, 'lng': 72.8169, 'investment': 4.1, 'daysDelayed': 105},
        {'id': 'CNG-013', 'name': 'Kurla Complex CNG Hub', 'lat': 19.0728, 'lng': 72.8826, 'investment': 3.4, 'daysDelayed': 102},
        {'id': 'CNG-014', 'name': 'Mulund CNG Station', 'lat': 19.1722, 'lng': 72.9577, 'investment': 3.0, 'daysDelayed': 106},
        {'id': 'CNG-015', 'name': 'Borivali CNG Center', 'lat': 19.2307, 'lng': 72.8567, 'investment': 3.1, 'daysDelayed': 103}
    ]
    
    return jsonify({
        'success': True,
        'cng_sites': mumbai_cng_sites,
        'total_investment': sum(s['investment'] for s in mumbai_cng_sites),
        'avg_delay': sum(s['daysDelayed'] for s in mumbai_cng_sites) / len(mumbai_cng_sites),
        'infrastructure_type': 'CNG_REFUELING'
    })



