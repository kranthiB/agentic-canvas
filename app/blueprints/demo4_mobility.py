"""
Demo 4: Mobility Maestro Blueprint
T3 Cognitive Autonomous Agent routes
"""
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
import random
from datetime import datetime

from app import db
from app.models.demo4_models import (
    CNGSite, SiteEvaluation, NetworkConfiguration,
    DemandForecast, CityTier, NetworkPosition, SiteStatus
)
from app.agents.demo4_agent import NetworkOptimizationAgent

demo4_bp = Blueprint('demo4', __name__)

# Initialize agent
network_agent = NetworkOptimizationAgent()


@demo4_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard - interactive map view"""
    return render_template('demo4/dashboard.html')





@demo4_bp.route('/api/evaluate-site/', methods=['POST'])
@login_required
def api_evaluate_site(site_id):
    """Evaluate a site"""
    site = CNGSite.query.get_or_404(site_id)
    
    # Check if already evaluated
    existing_eval = SiteEvaluation.query.filter_by(site_id=site.id).first()
    if existing_eval:
        return jsonify({
            'success': True,
            'evaluation': existing_eval.to_dict(),
            'message': 'Site already evaluated'
        })
    
    # Run agent evaluation
    environment = {'site': site.to_dict()}
    result = network_agent.run_cycle(environment)
    
    if result['success']:
        evaluation_data = result['result']['evaluation']
        
        # Save evaluation
        evaluation = SiteEvaluation(
            site_id=site.id,
            traffic_score=evaluation_data['scores']['traffic'],
            demographics_score=evaluation_data['scores']['demographics'],
            pipeline_infrastructure_score=evaluation_data['scores']['pipeline_infrastructure'],
            competition_score=evaluation_data['scores']['competition'],
            accessibility_score=evaluation_data['scores']['accessibility'],
            overall_score=evaluation_data['scores']['overall'],
            capex_inr=evaluation_data['financials']['capex_inr'],
            opex_annual_inr=evaluation_data['financials']['opex_annual_inr'],
            revenue_year1_inr=evaluation_data['financials']['revenue_year1_inr'],
            revenue_year5_inr=evaluation_data['financials']['revenue_year5_inr'],
            npv_inr=evaluation_data['financials']['npv_inr'],
            irr_percentage=evaluation_data['financials']['irr_percentage'],
            payback_years=evaluation_data['financials']['payback_years'],
            evaluated_by_agent=network_agent.agent_id,
            confidence_score=evaluation_data['confidence'],
            reasoning=evaluation_data['reasoning'],
            recommendation=evaluation_data['recommendation'],
            risk_factors=result['result']['risk_factors'],
            opportunities=result['result']['opportunities']
        )
        evaluation.save()
        
        # Update site status
        site.status = SiteStatus.EVALUATED
        db.session.commit()
        
        return jsonify({
            'success': True,
            'evaluation': evaluation.to_dict(),
            'next_steps': result['result']['next_steps']
        })
    
    return jsonify({'success': False, 'error': result.get('error')}), 500


@demo4_bp.route('/api/evaluate-batch', methods=['POST'])
@login_required
def api_evaluate_batch():
    """Evaluate multiple sites"""
    data = request.get_json()
    site_ids = data.get('site_ids', [])
    
    results = []
    
    for site_id in site_ids:
        site = CNGSite.query.get(site_id)
        if not site:
            continue
        
        # Check if already evaluated
        if SiteEvaluation.query.filter_by(site_id=site.id).first():
            continue
        
        # Evaluate
        environment = {'site': site.to_dict()}
        result = network_agent.run_cycle(environment)
        
        if result['success']:
            evaluation_data = result['result']['evaluation']
            
            evaluation = SiteEvaluation(
                site_id=site.id,
                traffic_score=evaluation_data['scores']['traffic'],
                demographics_score=evaluation_data['scores']['demographics'],
                pipeline_infrastructure_score=evaluation_data['scores']['pipeline_infrastructure'],
                competition_score=evaluation_data['scores']['competition'],
                accessibility_score=evaluation_data['scores']['accessibility'],
                overall_score=evaluation_data['scores']['overall'],
                capex_inr=evaluation_data['financials']['capex_inr'],
                opex_annual_inr=evaluation_data['financials']['opex_annual_inr'],
                revenue_year1_inr=evaluation_data['financials']['revenue_year1_inr'],
                revenue_year5_inr=evaluation_data['financials']['revenue_year5_inr'],
                npv_inr=evaluation_data['financials']['npv_inr'],
                irr_percentage=evaluation_data['financials']['irr_percentage'],
                payback_years=evaluation_data['financials']['payback_years'],
                evaluated_by_agent=network_agent.agent_id,
                confidence_score=evaluation_data['confidence'],
                reasoning=evaluation_data['reasoning'],
                recommendation=evaluation_data['recommendation'],
                risk_factors=result['result']['risk_factors'],
                opportunities=result['result']['opportunities']
            )
            evaluation.save()
            
            site.status = SiteStatus.EVALUATED
            results.append(evaluation.to_dict())
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'evaluated_count': len(results),
        'evaluations': results
    })





@demo4_bp.route('/api/optimize-network', methods=['POST'])
@login_required
def api_optimize_network():
    """Run network optimization"""
    data = request.get_json()
    
    budget_inr = data.get('budget_inr', 10000000)
    target_sites = data.get('target_sites', 50)
    objective = data.get('objective', 'balanced')
    
    # Get all evaluated sites
    evaluated = db.session.query(
        CNGSite, SiteEvaluation
    ).join(SiteEvaluation).all()
    
    candidate_sites = [site.to_dict() for site, _ in evaluated]
    
    # Run optimization
    result = network_agent.optimize_network(
        candidate_sites=candidate_sites,
        budget_inr=budget_inr,
        target_sites=target_sites
    )
    
    # Calculate network metrics
    selected_evaluations = SiteEvaluation.query.filter(
        SiteEvaluation.site_id.in_([
            CNGSite.query.filter_by(site_id=sid).first().id 
            for sid in result['selected_site_ids']
        ])
    ).all()
    
    total_revenue = sum(e.revenue_year1_inr for e in selected_evaluations)
    avg_score = sum(e.overall_score for e in selected_evaluations) / len(selected_evaluations) if selected_evaluations else 0
    
    # Save configuration
    config = NetworkConfiguration(
        config_name=data.get('name', f'Configuration {datetime.now().strftime("%Y%m%d-%H%M")}'),
        description=data.get('description', 'Auto-generated network configuration'),
        total_budget_inr=budget_inr,
        target_sites_count=target_sites,
        selected_site_ids=result['selected_site_ids'],
        total_capex_inr=result['total_capex_inr'],
        total_annual_revenue_inr=total_revenue,
        network_coverage_percentage=random.uniform(65, 85),
        population_served=sum(random.randint(100000, 500000) for _ in result['selected_site_ids']),
        optimization_objective=objective,
        optimization_algorithm='greedy_selection',
        optimization_time_ms=result['optimization_time_ms'],
        network_npv_inr=result['network_npv_inr'],
        network_irr_percentage=random.uniform(15, 25),
        optimized_by_agent=network_agent.agent_id
    )
    config.save()
    
    return jsonify({
        'success': True,
        'configuration': config.to_dict(),
        'selected_sites': result['selected_site_ids']
    })


@demo4_bp.route('/analytics')
@login_required
def analytics():
    """Analytics dashboard"""
    # Get evaluation statistics
    evaluations = SiteEvaluation.query.all()
    
    tier_stats = db.session.query(
        CNGSite.city_tier,
        db.func.count(CNGSite.id),
        db.func.avg(SiteEvaluation.overall_score)
    ).join(SiteEvaluation).group_by(CNGSite.city_tier).all()
    
    return render_template(
        'demo4/analytics.html',
        evaluations=evaluations,
        tier_stats=tier_stats
    )


@demo4_bp.route('/api/sites/map-data')
@login_required
def api_sites_map_data():
    """Get all CNG sites with evaluation data for map visualization"""
    sites = db.session.query(CNGSite, SiteEvaluation).outerjoin(SiteEvaluation).all()
    
    map_data = []
    for site, evaluation in sites:
        site_data = {
            'site_id': site.site_id,
            'city': site.city,
            'state': site.state,
            'latitude': site.latitude,
            'longitude': site.longitude,
            'city_tier': site.city_tier.value,
            'network_position': site.network_position.value,
            'status': site.status.value,
            'daily_traffic': site.daily_traffic_count,
            'estimated_refuels': site.estimated_daily_refuels
        }
        
        if evaluation:
            site_data.update({
                'score': evaluation.overall_score,
                'recommendation': evaluation.recommendation,
                'npv': evaluation.npv_inr,
                'irr': evaluation.irr_percentage,
                'evaluated': True
            })
        else:
            site_data.update({
                'score': 0,
                'recommendation': None,
                'evaluated': False
            })
        
        map_data.append(site_data)
    
    return jsonify({
        'success': True,
        'sites': map_data,
        'total_count': len(map_data)
    })


@demo4_bp.route('/api/sites/statistics')
@login_required
def api_sites_statistics():
    """Get site statistics by various dimensions"""
    
    # By tier
    tier_stats = db.session.query(
        CNGSite.city_tier,
        db.func.count(CNGSite.id).label('count'),
        db.func.avg(SiteEvaluation.overall_score).label('avg_score')
    ).outerjoin(SiteEvaluation).group_by(CNGSite.city_tier).all()
    
    # By status
    status_stats = db.session.query(
        CNGSite.status,
        db.func.count(CNGSite.id).label('count')
    ).group_by(CNGSite.status).all()
    
    # By recommendation
    recommendation_stats = db.session.query(
        SiteEvaluation.recommendation,
        db.func.count(SiteEvaluation.id).label('count')
    ).group_by(SiteEvaluation.recommendation).all()
    
    # Top cities
    city_stats = db.session.query(
        CNGSite.city,
        db.func.count(CNGSite.id).label('count'),
        db.func.avg(SiteEvaluation.overall_score).label('avg_score')
    ).outerjoin(SiteEvaluation).group_by(CNGSite.city).order_by(
        db.func.count(CNGSite.id).desc()
    ).limit(10).all()
    
    return jsonify({
        'success': True,
        'statistics': {
            'by_tier': [{'tier': t[0].value, 'count': t[1], 'avg_score': float(t[2]) if t[2] else 0} for t in tier_stats],
            'by_status': [{'status': s[0].value, 'count': s[1]} for s in status_stats],
            'by_recommendation': [{'recommendation': r[0], 'count': r[1]} for r in recommendation_stats],
            'by_city': [{'city': c[0], 'count': c[1], 'avg_score': float(c[2]) if c[2] else 0} for c in city_stats]
        }
    })


@demo4_bp.route('/api/sites/<site_id>/detailed')
@login_required
def api_site_detailed(site_id):
    """Get detailed CNG site information including evaluation and permits"""
    site = CNGSite.query.filter_by(site_id=site_id).first_or_404()
    evaluation = SiteEvaluation.query.filter_by(site_id=site.id).first()
    
    # Get permits for this site
    from app.models.demo4_extended_models import TEPermit
    permits = TEPermit.query.filter_by(site_id=site.id).all()
    
    return jsonify({
        'success': True,
        'site': site.to_dict(),
        'evaluation': evaluation.to_dict() if evaluation else None,
        'permits': [p.to_dict() for p in permits]
    })


# Scenario API Routes
@demo4_bp.route('/api/scenarios')
@login_required
def api_scenarios():
    """Get all available scenarios"""
    from app.data.demo4_scenarios import get_all_scenarios
    scenarios = get_all_scenarios()
    
    return jsonify({
        'success': True,
        'scenarios': scenarios
    })


@demo4_bp.route('/api/scenarios/<scenario_id>')
@login_required
def api_scenario_detail(scenario_id):
    """Get specific scenario details"""
    from app.data.demo4_scenarios import get_scenario_by_id
    scenario = get_scenario_by_id(scenario_id)
    
    if not scenario:
        return jsonify({
            'success': False,
            'error': 'Scenario not found'
        }), 404
    
    return jsonify({
        'success': True,
        'scenario': scenario
    })


@demo4_bp.route('/api/scenarios/<scenario_id>/simulate', methods=['POST'])
@login_required
def api_simulate_scenario(scenario_id):
    """Simulate a specific scenario"""
    from app.data.demo4_scenarios import get_scenario_by_id
    scenario = get_scenario_by_id(scenario_id)
    
    if not scenario:
        return jsonify({
            'success': False,
            'error': 'Scenario not found'
        }), 404
    
    return jsonify({
        'success': True,
        'scenario': scenario,
        'flow_steps': scenario['flow_steps'],
        'metadata': {
            'total_steps': len(scenario['flow_steps']),
            'involved_systems': scenario['involved_systems'],
            'involved_agents': scenario['involved_agents']
        }
    })
