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
from app.models.demo4_models import CNGSite, CityTier
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


@demo4_scenario_bp.route('/scenario4')
@login_required
def scenario4():
    """Scenario 4: Real-Time Operations & Continuous Optimization"""
    return render_template('demo4/scenario4.html')


@demo4_scenario_bp.route('/scenario6')
@login_required
def scenario6():
    """Scenario 6: Competitive Acquisition (M&A)"""
    return render_template('demo4/scenario6.html')


@demo4_scenario_bp.route('/scenario7')
@login_required
def scenario7():
    """Scenario 7: Dynamic Pricing & Revenue Optimization"""
    return render_template('demo4/scenario7.html')


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
    
    site = CNGSite.query.filter_by(site_id=site_id).first()
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
    query = CNGSite.query
    
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


@demo4_scenario_bp.route('/api/scenario7/current-pricing-state', methods=['GET'])
@login_required
def api_scenario7_current_pricing_state():
    """Get current pricing state and opportunity analysis"""
    pricing_data = {
        'network_overview': {
            'total_stations': 311,
            'static_price': 16.00,
            'revenue_efficiency_score': 67,
            'estimated_annual_loss': 8.4  # Crores
        },
        'inefficiencies': [
            {
                'type': 'location_underpricing',
                'description': 'Premium locations underpriced',
                'impact': '₹8.4 Cr/year loss',
                'stations_affected': 45
            },
            {
                'type': 'off_peak_idle',
                'description': '42% of network capacity idle during off-peak',
                'impact': '₹12.2 Cr opportunity',
                'avg_utilization': 20
            },
            {
                'type': 'peak_congestion',
                'description': '18% of peak sessions have >10 min wait',
                'impact': 'Customer dissatisfaction',
                'avg_wait_time': 12.3
            }
        ],
        'opportunity': {
            'potential_revenue_uplift': 18,  # percentage
            'estimated_additional_revenue': 20.6,  # Crores annually
            'implementation_timeline': 90,  # days
            'confidence_level': 85  # percentage
        }
    }
    
    return jsonify({
        'success': True,
        'pricing_analysis': pricing_data,
        'timestamp': datetime.now().isoformat()
    })


@demo4_scenario_bp.route('/api/scenario7/network-stations', methods=['GET'])
@login_required
def api_scenario7_network_stations():
    """Get network stations with pricing tiers for map visualization"""
    # Sample station data with different pricing tiers
    stations = [
        # Tier 1 Premium (Mumbai CBD)
        {'id': 'CNG-001', 'name': 'Nariman Point CNG Station', 'lat': 18.9254, 'lng': 72.8243, 'tier': 'premium', 'current_price': 16.00, 'optimal_price': 22.40, 'utilization': 85},
        {'id': 'CNG-002', 'name': 'BKC CNG Refueling Center', 'lat': 19.0608, 'lng': 72.8683, 'tier': 'premium', 'current_price': 16.00, 'optimal_price': 23.60, 'utilization': 90},
        {'id': 'CNG-003', 'name': 'Lower Parel CNG Center', 'lat': 18.9968, 'lng': 72.8288, 'tier': 'premium', 'current_price': 16.00, 'optimal_price': 21.80, 'utilization': 82},
        
        # Tier 2 High Traffic
        {'id': 'CNG-004', 'name': 'Andheri SEEPZ CNG Hub', 'lat': 19.1136, 'lng': 72.8697, 'tier': 'high', 'current_price': 16.00, 'optimal_price': 19.20, 'utilization': 75},
        {'id': 'CNG-005', 'name': 'Bandra West CNG Center', 'lat': 19.0596, 'lng': 72.8295, 'tier': 'high', 'current_price': 16.00, 'optimal_price': 18.80, 'utilization': 78},
        {'id': 'CNG-006', 'name': 'Powai Tech Park CNG Station', 'lat': 19.1197, 'lng': 72.9059, 'tier': 'high', 'current_price': 16.00, 'optimal_price': 19.60, 'utilization': 73},
        
        # Tier 3 Standard
        {'id': 'CNG-007', 'name': 'Malad Industrial CNG Hub', 'lat': 19.1865, 'lng': 72.8486, 'tier': 'standard', 'current_price': 16.00, 'optimal_price': 16.80, 'utilization': 62},
        {'id': 'CNG-008', 'name': 'Goregaon East CNG Station', 'lat': 19.1653, 'lng': 72.8526, 'tier': 'standard', 'current_price': 16.00, 'optimal_price': 16.40, 'utilization': 58},
        {'id': 'CNG-009', 'name': 'Vikhroli CNG Center', 'lat': 19.1076, 'lng': 72.9248, 'tier': 'standard', 'current_price': 16.00, 'optimal_price': 17.20, 'utilization': 65},
        
        # Tier 4 Economy
        {'id': 'CNG-010', 'name': 'Thane West CNG Hub', 'lat': 19.2183, 'lng': 72.9781, 'tier': 'economy', 'current_price': 16.00, 'optimal_price': 15.20, 'utilization': 45},
        {'id': 'CNG-011', 'name': 'Navi Mumbai CNG Station', 'lat': 19.0330, 'lng': 73.0297, 'tier': 'economy', 'current_price': 16.00, 'optimal_price': 14.80, 'utilization': 42},
        {'id': 'CNG-012', 'name': 'Mulund CNG Station', 'lat': 19.1722, 'lng': 72.9577, 'tier': 'economy', 'current_price': 16.00, 'optimal_price': 15.60, 'utilization': 48}
    ]
    
    return jsonify({
        'success': True,
        'stations': stations,
        'pricing_tiers': {
            'premium': {'min_price': 21.80, 'max_price': 23.60, 'color': '#dc2626'},
            'high': {'min_price': 18.80, 'max_price': 19.60, 'color': '#f59e0b'},
            'standard': {'min_price': 16.40, 'max_price': 17.20, 'color': '#10b981'},
            'economy': {'min_price': 14.80, 'max_price': 15.60, 'color': '#3b82f6'}
        }
    })


@demo4_scenario_bp.route('/api/scenario7/simulate-price', methods=['POST'])
@login_required
def api_scenario7_simulate_price():
    """Simulate dynamic pricing for given parameters"""
    data = request.get_json()
    
    station_id = data.get('station_id', 'CNG-002')  # Default to BKC
    time_of_day = data.get('time_of_day', 19)  # 7 PM
    demand_level = data.get('demand_level', 'high')
    weather = data.get('weather', 'sunny')
    customer_tier = data.get('customer_tier', 'diamond')
    
    # Base pricing logic (aligned with Indian CNG market - ~₹70-85/kg converted to kWh equivalent)
    base_price = 16.00
    
    # Location-based pricing (Indian business districts)
    location_premiums = {
        'CNG-002': 5.20,  # Connaught Place, Delhi (CBD)
        'CNG-004': 4.80,  # BKC, Mumbai (Business District) 
        'CNG-007': 3.60,  # Gurgaon Cyber City (IT Hub)
        'CNG-010': 2.40,  # Noida Expressway (Highway)
        'CNG-015': 3.20,  # Bangalore Electronic City
        'CNG-020': 2.80   # Pune Hinjewadi
    }
    location_premium = location_premiums.get(station_id, 2.00)
    
    # Time-based pricing (Indian peak patterns: morning office rush & evening return)
    peak_hours = [8, 9, 18, 19, 20]  # 8-9 AM, 6-8 PM
    super_peak = [8, 19]  # Super peak hours
    peak_multiplier = 1.20 if time_of_day in super_peak else (1.10 if time_of_day in peak_hours else 0.92)
    
    # Demand-based pricing (realistic vehicle flow)
    demand_multipliers = {'low': 0.88, 'medium': 1.00, 'high': 1.15, 'very_high': 1.35}
    demand_adjustment = base_price * (demand_multipliers.get(demand_level, 1.0) - 1.0)
    
    # Weather impact (Indian conditions affect CNG demand)
    weather_adjustments = {
        'sunny': 0.0, 'cloudy': 0.30, 'rain': 0.80, 'extreme': 0.50, 'winter': 0.20
    }
    weather_adjustment = weather_adjustments.get(weather, 0.0)
    
    # Customer tier discounts (realistic commercial/corporate rates)
    tier_adjustments = {
        'standard': 0.0, 'commercial': -0.80, 'premium': -1.20, 'corporate': -1.50
    }
    customer_adjustment = tier_adjustments.get(customer_tier, 0.0)
    
    # Calculate final price
    calculated_price = ((base_price + location_premium) * peak_multiplier + 
                       demand_adjustment + weather_adjustment + customer_adjustment)
    calculated_price = round(calculated_price, 2)
    
    # Price breakdown
    breakdown = {
        'base': base_price,
        'location_premium': location_premium,
        'peak_adjustment': round((base_price * peak_multiplier) - base_price, 2),
        'demand_adjustment': round(demand_adjustment, 2),
        'weather_adjustment': round(weather_adjustment, 2),
        'customer_discount': round(customer_adjustment, 2)
    }
    
    # Future price forecast
    forecast = {
        '21:00': round(calculated_price * 0.85, 2),  # 9 PM
        '23:00': round(calculated_price * 0.72, 2),  # 11 PM
        '06:00': round(calculated_price * 0.68, 2),  # 6 AM tomorrow
    }
    
    return jsonify({
        'success': True,
        'simulation': {
            'station_id': station_id,
            'parameters': {
                'time_of_day': time_of_day,
                'demand_level': demand_level,
                'weather': weather,
                'customer_tier': customer_tier
            },
            'calculated_price': calculated_price,
            'price_breakdown': breakdown,
            'price_forecast': forecast,
            'customer_app_view': {
                'display_price': calculated_price,
                'demand_indicator': demand_level.upper(),
                'next_price_drop': '21:00',
                'savings_available': round(calculated_price - forecast['21:00'], 2)
            }
        }
    })


@demo4_scenario_bp.route('/api/scenario7/run-pricing-analysis', methods=['POST'])
@login_required
def api_scenario7_run_pricing_analysis():
    """Trigger multi-agent pricing analysis workflow"""
    data = request.get_json()
    analysis_type = data.get('type', 'comprehensive')
    
    # Generate correlation ID for this analysis
    import uuid
    correlation_id = f"pricing_analysis_{uuid.uuid4().hex[:8]}"
    
    # Simulate agent workflow execution
    workflow_events = [
        {
            'timestamp': datetime.now(),
            'agent': 'Orchestrator',
            'action': 'Workflow started. Deploying 4 specialized agents for dynamic pricing analysis.',
            'status': 'initiated',
            'correlation_id': correlation_id
        },
        {
            'timestamp': datetime.now(),
            'agent': 'Financial Agent',
            'action': 'Calculating price elasticity models across 311 stations...',
            'details': 'Querying Finance ERP and Pricing Engine. Using Reasoning Engine for demand modeling.',
            'status': 'processing',
            'correlation_id': correlation_id
        },
        {
            'timestamp': datetime.now(),
            'agent': 'Geographic Agent', 
            'action': 'Classifying 311 stations by location tier and traffic patterns...',
            'details': 'Querying Census DB and Traffic Analytics. Utilizing Semantic Cache for faster results.',
            'status': 'processing',
            'correlation_id': correlation_id
        },
        {
            'timestamp': datetime.now(),
            'agent': 'Market Agent',
            'action': 'Segmenting customer base and analyzing pricing sensitivity...',
            'details': 'Querying CRM for session data. Using RAG Engine on Vector DB of market reports.',
            'status': 'processing',
            'correlation_id': correlation_id
        },
        {
            'timestamp': datetime.now(),
            'agent': 'Network Agent',
            'action': 'Modeling demand shifting potential and capacity optimization...',
            'details': 'Querying Grid Monitor and ML Platform for utilization patterns.',
            'status': 'processing',
            'correlation_id': correlation_id
        }
    ]
    
    return jsonify({
        'success': True,
        'analysis_started': True,
        'correlation_id': correlation_id,
        'estimated_duration': 180,  # seconds
        'initial_events': workflow_events[:2]  # Return first 2 events immediately
    })


@demo4_scenario_bp.route('/api/scenario7/analysis-events/<correlation_id>', methods=['GET'])
@login_required
def api_scenario7_analysis_events(correlation_id):
    """Get analysis events for a specific workflow"""
    # In a real implementation, this would fetch from database
    # For demo, we'll return progressive events based on time
    
    import time
    from datetime import datetime, timedelta
    
    # Simulate progressive event stream
    all_events = [
        {'time': 0, 'agent': 'Orchestrator', 'action': 'Workflow started. Deploying 4 specialized agents for dynamic pricing analysis.', 'status': 'initiated'},
        {'time': 3, 'agent': 'Financial Agent', 'action': 'Calculating price elasticity models across 311 stations...', 'status': 'processing'},
        {'time': 8, 'agent': 'Geographic Agent', 'action': 'Classifying 311 stations by location tier and traffic patterns...', 'status': 'processing'},
        {'time': 12, 'agent': 'Market Agent', 'action': 'Segmenting customer base and analyzing pricing sensitivity...', 'status': 'processing'},
        {'time': 18, 'agent': 'Network Agent', 'action': 'Modeling demand shifting potential and capacity optimization...', 'status': 'processing'},
        {'time': 25, 'agent': 'Financial Agent', 'action': '✅ Price elasticity analysis complete. Identified 4 pricing tiers with 15-35% revenue potential.', 'status': 'completed'},
        {'time': 32, 'agent': 'Geographic Agent', 'action': '✅ Location analysis complete. 45 premium sites, 89 high-traffic, 132 standard, 45 economy tier.', 'status': 'completed'},
        {'time': 38, 'agent': 'Market Agent', 'action': '✅ Customer segmentation complete. 3 loyalty tiers identified with different price sensitivities.', 'status': 'completed'},
        {'time': 45, 'agent': 'Network Agent', 'action': '✅ Demand modeling complete. Peak shifting potential: 23% improvement in utilization.', 'status': 'completed'},
        {'time': 50, 'agent': 'Orchestrator', 'action': 'Synthesizing agent reports using Prompt Manager template "PricingStrategy"...', 'status': 'processing'},
        {'time': 55, 'agent': 'Orchestrator', 'action': 'Applying Guardrails for price volatility limits and customer impact assessment...', 'status': 'processing'},
        {'time': 60, 'agent': 'Orchestrator', 'action': '✅ ANALYSIS COMPLETE. Dynamic pricing model ready for review.', 'status': 'completed'}
    ]
    
    # Return events that should be visible now (simulate real-time progression)
    current_events = []
    for event in all_events:
        event_time = datetime.now() + timedelta(seconds=event['time'])
        current_events.append({
            'timestamp': event_time.isoformat(),
            'agent': event['agent'],
            'action': event['action'],
            'status': event['status'],
            'correlation_id': correlation_id
        })
    
    return jsonify({
        'success': True,
        'correlation_id': correlation_id,
        'events': current_events,
        'total_events': len(current_events),
        'analysis_complete': len(current_events) >= len(all_events)
    })


# =============================================================================
# SCENARIO 4: REAL-TIME OPERATIONS & CONTINUOUS OPTIMIZATION
# =============================================================================

@demo4_scenario_bp.route('/api/scenario4/noc-dashboard', methods=['GET'])
@login_required
def get_noc_dashboard():
    """Get Network Operations Center dashboard data"""
    try:
        # Simulate NOC dashboard data for Bangalore network
        dashboard_data = {
            'network_status': 'operational',
            'uptime_24h': 99.8,
            'active_sessions': 2,
            'available_dispensers': '70/72',
            'supply_pressure_bar': 45,
            'compressor_load_kw': 850,
            'current_time': '2025-10-04T06:00:00',
            'sites': [
                {
                    'id': 'BLR-001',
                    'name': 'Whitefield Tech Park',
                    'status': 'online',
                    'dispensers': 4,
                    'utilization': 0.25,
                    'location': [12.9698, 77.7500],
                    'current_pressure_bar': 45
                },
                {
                    'id': 'BLR-002',
                    'name': 'Electronic City Hub',
                    'status': 'online',
                    'dispensers': 4,
                    'utilization': 0.15,
                    'location': [12.8456, 77.6603],
                    'current_pressure_bar': 46
                },
                {
                    'id': 'BLR-003',
                    'name': 'Koramangala Junction',
                    'status': 'online',
                    'dispensers': 3,
                    'utilization': 0.33,
                    'location': [12.9279, 77.6271],
                    'current_pressure_bar': 44
                },
                {
                    'id': 'BLR-004',
                    'name': 'Indiranagar Metro',
                    'status': 'online',
                    'dispensers': 4,
                    'utilization': 0.0,
                    'location': [12.9716, 77.6412],
                    'current_pressure_bar': 43
                },
                {
                    'id': 'BLR-005',
                    'name': 'Brigade Road',
                    'status': 'maintenance',
                    'dispensers': 2,
                    'utilization': 0.0,
                    'location': [12.9716, 77.6103],
                    'current_pressure_bar': 41
                }
            ],
            'load_chart_data': {
                'labels': ['00:00', '02:00', '04:00', '06:00', '08:00', '10:00',
                          '12:00', '14:00', '16:00', '18:00', '20:00', '22:00'],
                'supply_pressure': [44, 43, 42, 45, 46, 45, 47, 46, 46, 48, 47, 45],
                'compressor_load': [450, 320, 280, 850, 1200, 980, 1380, 1240,
                                   1160, 1450, 1280, 680],
                'pressure_threshold': [40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40]
            },
            'alerts': [
                {
                    'level': 'medium',
                    'icon': 'warning',
                    'message': 'BLR-003-DC-02 Connector wear >85%. Maintenance scheduled.',
                    'timestamp': '2025-10-04T05:45:00'
                },
                {
                    'level': 'medium', 
                    'icon': 'thermometer',
                    'message': 'BLR-008-DC-01 Temperature variance. Inspection recommended.',
                    'timestamp': '2025-10-04T05:30:00'
                }
            ]
        }
        
        return jsonify({
            'success': True,
            'data': dashboard_data
        })
        
    except Exception as e:
        logger.error(f"Error in get_noc_dashboard: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@demo4_scenario_bp.route('/api/scenario4/trigger-event', methods=['POST'])
@login_required  
def trigger_operational_event():
    """Trigger a specific operational event for demo"""
    try:
        data = request.get_json()
        event_type = data.get('event_type')
        timestamp = data.get('timestamp', '08:15:00')
        
        # Generate correlation ID for this event
        correlation_id = f"ops_{event_type}_{int(datetime.now().timestamp())}"
        
        # Define event scenarios
        event_scenarios = {
            'morning_peak': {
                'title': 'Morning Peak Load Management',
                'description': 'Smart load balancing to avoid demand charge penalties',
                'severity': 'high',
                'estimated_savings': 9000
            },
            'anomaly_detection': {
                'title': 'Charger Anomaly Detection', 
                'description': 'Graceful shutdown prevents dispenser failure',
                'severity': 'critical',
                'estimated_savings': 14800
            },
            'lunch_surge': {
                'title': 'Lunch Hour Revenue Optimization',
                'description': 'Dynamic pricing during demand surge',
                'severity': 'medium',
                'estimated_revenue': 780
            },
            'predictive_maintenance': {
                'title': 'Predictive Maintenance Alert',
                'description': 'ML model predicts component failure',
                'severity': 'predictive',
                'estimated_savings': 17400
            }
        }
        
        scenario = event_scenarios.get(event_type, {})
        
        return jsonify({
            'success': True,
            'correlation_id': correlation_id,
            'event_type': event_type,
            'timestamp': timestamp,
            'scenario': scenario
        })
        
    except Exception as e:
        logger.error(f"Error in trigger_operational_event: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@demo4_scenario_bp.route('/api/scenario4/live-stream/<correlation_id>', methods=['GET'])
@login_required
def get_operational_live_stream(correlation_id):
    """Get live event stream for operational scenarios"""
    try:
        # Extract event type from correlation_id
        event_type = correlation_id.split('_')[1] if '_' in correlation_id else 'unknown'
        
        # Define event streams for different scenarios
        event_streams = {
            'morning_peak': [
                {'time': 0, 'agent': 'Operations Agent', 'action': 'Peak load detected. Querying Grid Monitor for capacity status.', 'components': ['Grid Monitor']},
                {'time': 7, 'agent': 'Orchestrator', 'action': 'Threshold breach likely. Invoking Energy Optimization Agent.', 'components': ['CNG Orchestrator', 'Network Optimizer']},
                {'time': 12, 'agent': 'Energy Optimization Agent', 'action': 'Strategy: Smart Load Balancing. Using Reasoning Engine for optimal throttling.', 'components': ['Reasoning Engine']},
                {'time': 17, 'agent': 'Energy Optimization Agent', 'action': 'Querying CRM to find customers near low-usage sites.', 'components': ['CRM']},
                {'time': 25, 'agent': 'Operations Agent', 'action': 'EXECUTING. Command sent to BLR-001 chargers (throttle 50kW→35kW).', 'components': ['Alerts']},  
                {'time': 35, 'agent': 'Operations Agent', 'action': '✅ MITIGATION SUCCESSFUL. Demand charge penalty avoided: ₹9,000', 'components': []}
            ],
            'anomaly_detection': [
                {'time': 0, 'agent': 'Observability', 'action': 'High pressure alert from BLR-004-DC-03 dispenser.', 'components': ['Observability']},
                {'time': 2, 'agent': 'Operations Agent', 'action': 'Anomaly detected. Initiating diagnosis.', 'components': ['Operations Agent']},
                {'time': 18, 'agent': 'Operations Agent', 'action': 'Using RAG Engine on Vector DB (maintenance logs & manuals).', 'components': ['RAG Engine', 'Vector DB']},
                {'time': 30, 'agent': 'Reasoning Engine', 'action': 'Diagnosis: Valve wear. Recommendation: Graceful shutdown.', 'components': ['Reasoning Engine']},
                {'time': 35, 'agent': 'Operations Agent', 'action': 'EXECUTING. Command: "Finish current refueling, no new starts."', 'components': ['Alerts', 'CRM']},
                {'time': 45, 'agent': 'Operations Agent', 'action': '✅ GRACEFUL SHUTDOWN COMPLETE. Dispenser failure prevented.', 'components': []}
            ]
        }
        
        events = event_streams.get(event_type, [])
        
        # Convert to proper format with timestamps
        formatted_events = []
        for event in events:
            event_time = datetime.now() + timedelta(seconds=event['time'])
            formatted_events.append({
                'timestamp': event_time.strftime('%H:%M:%S'),
                'agent': event['agent'],
                'action': event['action'],
                'components_activated': event['components'],
                'correlation_id': correlation_id
            })
        
        return jsonify({
            'success': True,
            'correlation_id': correlation_id,
            'events': formatted_events,
            'total_events': len(formatted_events)
        })
        
    except Exception as e:
        logger.error(f"Error in get_operational_live_stream: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@demo4_scenario_bp.route('/api/scenario4/dispenser-health/<dispenser_id>', methods=['GET'])
@login_required
def get_dispenser_health(dispenser_id):
    """Get detailed CNG dispenser health telemetry"""
    try:
        # Simulate CNG dispenser telemetry data
        health_data = {
            'dispenser_id': dispenser_id,
            'status': 'critical' if 'DC-03' in dispenser_id else 'normal',
            'temperature': {
                'current': 78 if 'DC-03' in dispenser_id else 45,
                'max_safe': 65,
                'history': [42, 44, 46, 52, 58, 65, 72, 78] if 'DC-03' in dispenser_id else [42, 43, 44, 45, 44, 45, 45, 45]
            },
            'valve_pressure': {
                'current': 285 if 'DC-03' in dispenser_id else 250,
                'max_safe': 275,
                'history': [250, 255, 260, 268, 275, 280, 285, 290] if 'DC-03' in dispenser_id else [248, 250, 251, 250, 249, 250, 250, 250]
            },
            'flow_rate': {
                'current': 35 if 'DC-03' in dispenser_id else 50,
                'rated': 50,
                'efficiency': 70 if 'DC-03' in dispenser_id else 96
            },
            'session_count': 1247,
            'last_maintenance': '2025-09-15T10:00:00',
            'last_update': '2025-01-21T14:30:00',
            'predicted_failure': '3-7 days' if 'DC-03' in dispenser_id else None,
            'confidence': 87 if 'DC-03' in dispenser_id else None,
            'recent_alerts': [
                {
                    'level': 'critical',
                    'message': 'Temperature exceeding safe limits',
                    'timestamp': '2025-01-21T14:15:00'
                },
                {
                    'level': 'warning',
                    'message': 'Valve pressure approaching maximum',
                    'timestamp': '2025-01-21T13:45:00'
                }
            ] if 'DC-03' in dispenser_id else [
                {
                    'level': 'info',
                    'message': 'Routine maintenance completed',
                    'timestamp': '2025-01-20T10:00:00'
                }
            ]
        }
        
        return jsonify({
            'success': True,
            'data': health_data
        })
        
    except Exception as e:
        logger.error(f"Error in get_charger_health: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@demo4_scenario_bp.route('/api/scenario4/end-of-day-report', methods=['GET'])
@login_required
def get_end_of_day_report():
    """Get end of day operational report"""
    try:
        report_data = {
            'date': '2025-10-04',
            'network': 'Bangalore Network - 18 Sites',
            'daily_score': 96.2,
            'performance_metrics': {
                'network_uptime': 97.8,
                'revenue_beat_target': 3.9,
                'revenue_beat_amount': 12180,
                'avg_wait_time': 4.2
            },
            'ai_optimizations': [
                {
                    'title': 'Morning Peak Load Management',
                    'value': 9000,
                    'type': 'cost_avoidance',
                    'description': 'Demand charge penalty avoided'
                },
                {
                    'title': 'Anomaly Detection & Graceful Shutdown', 
                    'value': 14800,
                    'type': 'cost_avoidance',
                    'description': 'Catastrophic failure cost avoided'
                },
                {
                    'title': 'Lunch Hour Revenue Optimization',
                    'value': 780,
                    'type': 'revenue_uplift',
                    'description': 'Dynamic pricing uplift'
                },
                {
                    'title': 'Predictive Maintenance Alert',
                    'value': 17400, 
                    'type': 'cost_avoidance',
                    'description': 'Proactive repair savings'
                },
                {
                    'title': 'Evening Load Shifting',
                    'value': 28340,
                    'type': 'cost_avoidance', 
                    'description': 'Grid cost savings'
                }
            ],
            'total_daily_value': 70320
        }
        
        return jsonify({
            'success': True,
            'data': report_data
        })
        
    except Exception as e:
        logger.error(f"Error in get_end_of_day_report: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@demo4_scenario_bp.route('/api/scenario4/annual-impact', methods=['GET'])
@login_required
def get_annual_impact():
    """Get annual impact projection"""
    try:
        impact_data = {
            'network': 'Bangalore Network - 18 Sites',
            'comparison': {
                'without_ai': {
                    'network_uptime': 92.0,
                    'annual_revenue': 11.4,
                    'annual_energy_costs': 37.6,
                    'annual_maint_costs': 4.2,
                    'customer_nps': 68
                },
                'with_agentic_canvas': {
                    'network_uptime': 97.9,
                    'annual_revenue': 11.9,
                    'annual_energy_costs': 27.1,
                    'annual_maint_costs': 2.5,
                    'customer_nps': 79
                },
                'improvements': {
                    'network_uptime': 6.4,
                    'annual_revenue': 0.5,
                    'annual_energy_costs': -10.5,
                    'annual_maint_costs': -1.7,
                    'customer_nps': 11
                }
            },
            'total_annual_benefit': 11.2,
            'roi_percentage': 850,
            'payback_period_months': 2
        }
        
        return jsonify({
            'success': True,
            'data': impact_data
        })
        
    except Exception as e:
        logger.error(f"Error in get_annual_impact: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# =============================================================================
# SCENARIO 6: COMPETITIVE ACQUISITION (M&A)
# =============================================================================

@demo4_scenario_bp.route('/api/scenario6/ma-opportunity', methods=['GET'])
@login_required
def get_ma_opportunity():
    """Get M&A opportunity alert data"""
    try:
        opportunity_data = {
            'target': {
                'name': 'Statiq Energy',
                'description': "India's #3 CNG Network",
                'stations': 77,
                'owned_stations': 28,
                'aggregated_stations': 49,
                'annual_revenue': 18,  # Crores
                'ebitda': 2.4,  # Crores  
                'ebitda_margin': 13,  # Percentage
                'asking_price_min': 45,  # Crores
                'asking_price_max': 50   # Crores
            },
            'deadline': {
                'hours_remaining': 72,  
                'loi_deadline': '2025-10-12T18:00:00'
            },
            'strategic_rationale': [
                {
                    'title': 'Market Share Jump',
                    'description': '18% → 30% (Instant #2 Position)',
                    'icon': 'chart-line',
                    'color': '#10b981'
                },
                {
                    'title': 'Geographic Fill', 
                    'description': 'Critical Tier-2 cities (Lucknow, Indore)',
                    'icon': 'map-marked-alt',
                    'color': '#3b82f6'
                },
                {
                    'title': 'Speed to Market',
                    'description': '2-3 years of growth in 100 days', 
                    'icon': 'rocket',
                    'color': '#7c3aed'
                },
                {
                    'title': 'Competitive Threat',
                    'description': 'Adani & Tata are other bidders',
                    'icon': 'exclamation-triangle',
                    'color': '#f59e0b'
                }
            ],
            'source': 'Investment Banker (Confidential)',
            'competitors': ['Adani Group', 'Tata Power', 'Shell India']
        }
        
        return jsonify({
            'success': True,
            'data': opportunity_data
        })
        
    except Exception as e:
        logger.error(f"Error in get_ma_opportunity: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@demo4_scenario_bp.route('/api/scenario6/run-ma-sprint', methods=['POST'])
@login_required
def run_ma_sprint():
    """Trigger M&A analysis sprint"""
    try:
        data = request.get_json()
        target_company = data.get('target', 'Statiq Energy')
        
        # Generate correlation ID for this sprint
        import uuid
        correlation_id = f"ma_sprint_{uuid.uuid4().hex[:8]}"
        
        sprint_data = {
            'correlation_id': correlation_id,
            'target_company': target_company,  
            'sprint_started': datetime.now().isoformat(),
            'estimated_duration': 92,  # seconds (simulating 48 hours)
            'agents_deployed': 4,
            'status': 'initiated'
        }
        
        return jsonify({
            'success': True,
            'sprint': sprint_data
        })
        
    except Exception as e:
        logger.error(f"Error in run_ma_sprint: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@demo4_scenario_bp.route('/api/scenario6/sprint-events/<correlation_id>')
@login_required
def get_ma_sprint_events(correlation_id):
    """Get M&A sprint events"""
    try:
        # Simulate progressive event stream for M&A analysis
        all_events = [
            {
                'time': 0,
                'agent': 'Orchestrator',
                'action': 'M&A Sprint initiated. All agents deployed in parallel.',
                'status': 'initiated'
            },
            {
                'time': 1,
                'agent': 'Market Intel Agent',
                'action': 'Assessing strategic fit using RAG Engine on market reports.',  # noqa: E501
                'details': 'Querying Competitor Intel system for bidder analysis.',
                'status': 'processing'
            },
            {
                'time': 1,
                'agent': 'Geographic Intel Agent',
                'action': 'Analyzing network synergy and spatial coverage.',
                'details': 'Performing spatial analysis against NHAI and Traffic data.',  # noqa: E501
                'status': 'processing'
            },
            {
                'time': 1,
                'agent': 'Financial Analysis Agent',
                'action': 'Building comprehensive valuation models.',
                'details': 'Accessing VDR via secure tool. Using Reasoning Engine for DCF.',  # noqa: E501
                'status': 'processing'
            },
            {
                'time': 1,
                'agent': 'Permit Manager Agent',
                'action': 'Evaluating regulatory approval requirements.',
                'details': 'Using RAG Engine on legal KB for CCI compliance rules.',  # noqa: E501
                'status': 'processing'
            },
            {
                'time': 30,
                'agent': 'Financial Agent',
                'action': '✅ DCF Valuation complete: ₹37 Cr standalone value.',
                'status': 'completed'
            },
            {
                'time': 45,
                'agent': 'Geographic Agent',
                'action': '✅ Network synergy calculated: ₹9 Cr/year value creation.',  # noqa: E501
                'status': 'completed'
            },
            {
                'time': 60,
                'agent': 'Market Intel Agent',
                'action': '✅ Competitive threat from Adani confirmed. Speed advantage identified.',  # noqa: E501
                'status': 'completed'
            },
            {
                'time': 75,
                'agent': 'Permit Manager Agent',
                'action': '✅ No CCI approval required. 100-day close feasible.',
                'status': 'completed'
            },
            {
                'time': 90,
                'agent': 'Orchestrator',
                'action': 'Synthesizing reports using Prompt Manager "M&A_Decision_Memo" template.',  # noqa: E501
                'status': 'processing'
            },
            {
                'time': 92,
                'agent': 'Orchestrator',
                'action': '✅ SPRINT COMPLETE. Decision Package ready for executive review.',  # noqa: E501
                'status': 'completed'
            }
        ]
        
        # Convert to proper format with timestamps
        formatted_events = []
        for event in all_events:
            event_time = datetime.now() + timedelta(seconds=event['time'])
            formatted_events.append({
                'timestamp': event_time.strftime('%H:%M:%S'),
                'agent': event['agent'],
                'action': event['action'],
                'details': event.get('details', ''),
                'status': event['status'],
                'correlation_id': correlation_id
            })
        
        return jsonify({
            'success': True,
            'correlation_id': correlation_id,
            'events': formatted_events,
            'total_events': len(formatted_events),
            'sprint_complete': len(formatted_events) >= len(all_events)
        })
        
    except Exception as e:
        logger.error(f"Error in get_ma_sprint_events: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@demo4_scenario_bp.route('/api/scenario6/decision-package', methods=['GET'])
@login_required
def get_ma_decision_package():
    """Get M&A decision package"""
    try:
        decision_data = {
            'recommendation': 'PROCEED_WITH_BID',
            'confidence_score': 8.5,
            'strategic_fit': {
                'score': 9,
                'market_share_before': 18,
                'market_share_after': 30,
                'market_position': '#2 (vs #1 Tata)',
                'new_customers': 39000,
                'brand_synergy': 'Excellent'
            },
            'network_fit': {
                'score': 9,
                'new_cities': 10,
                'complementary_sites': 85,  # percentage
                'strategic_corridors': 'NH-48 corridor complete',
                'integration_complexity': 'Straightforward'
            },
            'valuation': {
                'dcf_standalone': 37,
                'comparable_transactions': 42,
                'asset_value': 24,
                'with_synergies_npv': 75,
                'fair_value': 42
            },
            'bid_strategy': {
                'asking_price_range': [45, 50],
                'opening_bid': 40,
                'target_price': 42,
                'walk_away_price': 48,
                'structure': {
                    'upfront_cash': 36,
                    'earnout': 4,
                    'earnout_description': 'Performance-based over 2 years'
                }
            },
            'execution_risk': {
                'regulatory_path': 'CLEAR - No CCI approval needed',
                'timeline_feasible': '100-day close is feasible',
                'primary_risk': 'Competitive overbidding by Adani',
                'mitigation': 'Emphasize speed, certainty, and strategic fit'
            }
        }
        
        return jsonify({
            'success': True,
            'decision': decision_data
        })
        
    except Exception as e:
        logger.error(f"Error in get_ma_decision_package: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@demo4_scenario_bp.route('/api/scenario6/approve-bid', methods=['POST'])
@login_required
def approve_ma_bid():
    """Approve M&A bid and start execution"""
    try:
        data = request.get_json()
        bid_amount = data.get('bid_amount', 40)
        
        execution_data = {
            'bid_approved': True,
            'final_bid_amount': bid_amount,
            'loi_submitted': datetime.now().isoformat(),
            'deal_timeline': {
                'phase_1_negotiation': {
                    'duration_days': 14,
                    'milestones': [
                        {
                            'date': '2025-10-09',
                            'event': 'LOI Submitted',
                            'status': 'completed'
                        },
                        {
                            'date': '2025-10-11',
                            'event': 'Counter-offer Expected',
                            'status': 'pending'
                        },
                        {
                            'date': '2025-10-13',
                            'event': 'Final Agreement Target',
                            'status': 'pending'
                        }
                    ]
                },
                'phase_2_due_diligence': {
                    'duration_days': 30,
                    'start_date': '2025-10-23'
                },
                'phase_3_closing': {  
                    'duration_days': 56,
                    'target_close_date': '2026-01-15'
                }
            }
        }
        
        return jsonify({
            'success': True,
            'execution': execution_data
        })
        
    except Exception as e:
        logger.error(f"Error in approve_ma_bid: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@demo4_scenario_bp.route('/api/scenario6/post-merger-results', methods=['GET'])
@login_required
def get_post_merger_results():
    """Get post-merger integration results"""
    try:
        results_data = {
            'integration_period': '6 months',
            'network_transformation': {
                'before': {
                    'total_sites': 235,
                    'market_share': 18,
                    'market_position': 3,
                    'separate_brands': True
                },
                'after': {
                    'total_sites': 311,
                    'market_share': 30.2,
                    'market_position': 2,
                    'integrated_brand': True
                }
            },
            'synergy_realization': {
                'projected_annual': 9.0,  # Crores
                'actual_6_months': 12.7,  # Crores
                'performance_vs_target': 141,  # percentage
                'outperformance': 41  # percentage points
            },
            'business_impact': {
                'customer_retention': {
                    'actual': 89,  # percentage
                    'target': 80,  # percentage
                    'earnout_triggered': True
                },
                'npv_created': 18.2,  # Crores
                'roi_percentage': 46,
                'market_gap_to_leader': {
                    'before': 14,  # percentage points
                    'after': 1  # percentage points
                }
            },
            'strategic_outcomes': [
                'Achieved #2 market position in India CNG market',
                'Successfully integrated 77 Statiq stations',
                'Exceeded all synergy targets by 41%',
                'Reduced gap to market leader from 14% to 1%',
                'Completed integration 2 months ahead of schedule'
            ]
        }
        
        return jsonify({
            'success': True,
            'results': results_data
        })
        
    except Exception as e:
        logger.error(f"Error in get_post_merger_results: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

