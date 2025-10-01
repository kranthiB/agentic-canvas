"""
Demo 4: Mobility Maestro Blueprint
T3 Cognitive Autonomous Agent routes
"""
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
import random

from app import db
from app.models.demo4_models import (
    ChargingSite, SiteEvaluation, NetworkConfiguration,
    DemandForecast, CityTier, NetworkPosition, SiteStatus
)
from app.agents.demo4_agent import NetworkOptimizationAgent

demo4_bp = Blueprint('demo4', __name__)

# Initialize agent
network_agent = NetworkOptimizationAgent()


@demo4_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    # Get site statistics
    total_sites = ChargingSite.query.count()
    evaluated_sites = SiteEvaluation.query.count()
    
    # Get recommended sites (high scores)
    recommended_sites = SiteEvaluation.query.filter(
        SiteEvaluation.overall_score >= 75
    ).count()
    
    # Calculate average ROI (Internal Rate of Return)
    avg_roi_result = db.session.query(
        db.func.avg(SiteEvaluation.irr_percentage)
    ).scalar()
    avg_roi = avg_roi_result if avg_roi_result else 0.0
    
    # Create stats dict
    stats = {
        'total_candidates': total_sites,
        'evaluated_sites': evaluated_sites,
        'recommended_sites': recommended_sites,
        'avg_roi': avg_roi
    }
    
    # Get top sites
    top_evaluations = db.session.query(
        SiteEvaluation, ChargingSite
    ).join(ChargingSite).order_by(
        SiteEvaluation.overall_score.desc()
    ).limit(10).all()
    
    # Get network configurations
    configurations = NetworkConfiguration.query.order_by(
        NetworkConfiguration.created_at.desc()
    ).limit(5).all()
    
    return render_template(
        'demo4/dashboard.html',
        stats=stats,
        top_evaluations=top_evaluations,
        configurations=configurations
    )


@demo4_bp.route('/sites')
@login_required
def sites():
    """Site list and map view"""
    # Get filter parameters
    city_tier = request.args.get('tier', 'all')
    status = request.args.get('status', 'all')
    
    query = ChargingSite.query
    
    if city_tier != 'all':
        query = query.filter_by(city_tier=CityTier[city_tier.upper()])
    
    if status != 'all':
        query = query.filter_by(status=SiteStatus[status.upper()])
    
    sites = query.all()
    
    return render_template('demo4/sites.html', sites=sites)


@demo4_bp.route('/site/')
@login_required
def site_detail(site_id):
    """Site detail page"""
    site = ChargingSite.query.get_or_404(site_id)
    evaluation = SiteEvaluation.query.filter_by(site_id=site.id).first()
    
    return render_template(
        'demo4/site_detail.html',
        site=site,
        evaluation=evaluation
    )


@demo4_bp.route('/api/evaluate-site/', methods=['POST'])
@login_required
def api_evaluate_site(site_id):
    """Evaluate a site"""
    site = ChargingSite.query.get_or_404(site_id)
    
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
            grid_infrastructure_score=evaluation_data['scores']['grid_infrastructure'],
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
        site = ChargingSite.query.get(site_id)
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
                grid_infrastructure_score=evaluation_data['scores']['grid_infrastructure'],
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


@demo4_bp.route('/optimize')
@login_required
def optimize():
    """Network optimization page"""
    configurations = NetworkConfiguration.query.order_by(
        NetworkConfiguration.created_at.desc()
    ).all()
    
    return render_template('demo4/optimize.html', configurations=configurations)


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
        ChargingSite, SiteEvaluation
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
            ChargingSite.query.filter_by(site_id=sid).first().id 
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
        ChargingSite.city_tier,
        db.func.count(ChargingSite.id),
        db.func.avg(SiteEvaluation.overall_score)
    ).join(SiteEvaluation).group_by(ChargingSite.city_tier).all()
    
    return render_template(
        'demo4/analytics.html',
        evaluations=evaluations,
        tier_stats=tier_stats
    )