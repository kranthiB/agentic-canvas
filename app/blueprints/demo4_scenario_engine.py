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

