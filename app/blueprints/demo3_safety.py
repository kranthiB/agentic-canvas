"""
Demo 3: Safety Guardian Blueprint
T2 Procedural Workflow Agent routes
"""
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from datetime import datetime, timedelta
import random

from app import db
from app.models.demo3_models import (
    PermitToWork, GasSensorReading, SafetyConflict,
    SafetyIncident, RiskHeatmap, PermitType, PermitStatus, RiskLevel, AlertLevel
)
from app.agents.demo3_agent import SafetyGuardianAgent
from app.core.simulator import simulator

demo3_bp = Blueprint('demo3', __name__)

# Initialize agent
safety_agent = SafetyGuardianAgent()


@demo3_bp.route('/dashboard')
@login_required
def dashboard():
    """Main safety dashboard"""
    # Get active permits
    active_permits = PermitToWork.query.filter_by(
        status=PermitStatus.ACTIVE
    ).all()
    
    # Get recent gas readings
    recent_readings = GasSensorReading.query.order_by(
        GasSensorReading.created_at.desc()
    ).limit(20).all()

    # Get the latest reading and transform into gas_readings dict
    latest_reading = recent_readings[0] if recent_readings else None

    # Transform gas readings into dict grouped by gas type (latest reading per gas)
    gas_readings = {}
    if latest_reading:
        gas_readings = {
            'O2': {
                'value': latest_reading.o2_percentage or 20.9,
                'threshold': 19.5,  # Minimum safe O2 level
                'status': 'safe' if (latest_reading.o2_percentage or 20.9) >= 19.5 else 'alarm',
                'timestamp': latest_reading.created_at,
                'location': latest_reading.area
            },
            'LEL': {
                'value': latest_reading.lel_percentage or 0,
                'threshold': 10.0,  # LEL alarm threshold
                'status': 'safe' if (latest_reading.lel_percentage or 0) < 10 else 'alarm',
                'timestamp': latest_reading.created_at,
                'location': latest_reading.area
            },
            'H2S': {
                'value': latest_reading.h2s_ppm or 0,
                'threshold': 10.0,  # H2S alarm threshold (ppm)
                'status': 'safe' if (latest_reading.h2s_ppm or 0) < 10 else 'alarm',
                'timestamp': latest_reading.created_at,
                'location': latest_reading.area
            },
            'CO': {
                'value': latest_reading.co_ppm or 0,
                'threshold': 25.0,  # CO alarm threshold (ppm)
                'status': 'safe' if (latest_reading.co_ppm or 0) < 25 else 'alarm',
                'timestamp': latest_reading.created_at,
                'location': latest_reading.area
            }
        }
    
    # Get unresolved conflicts
    conflicts = SafetyConflict.query.filter_by(
        resolved=False
    ).all()
    
    # Get latest risk heatmap
    heatmap = RiskHeatmap.query.order_by(
        RiskHeatmap.created_at.desc()
    ).first()
    
    # Calculate statistics for dashboard
    total_permits = PermitToWork.query.count()
    active_count = len(active_permits)
    pending_permits = PermitToWork.query.filter_by(
        status=PermitStatus.PENDING
    ).count()
    
    # Get today's conflicts
    from datetime import datetime, timedelta
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    conflicts_today = SafetyConflict.query.filter(
        SafetyConflict.created_at >= today_start
    ).count()
    
    # Calculate compliance rate (approved permits / total permits)
    approved_permits = PermitToWork.query.filter_by(
        status=PermitStatus.APPROVED
    ).count()
    compliance_rate = (approved_permits / total_permits * 100) if total_permits > 0 else 100.0
    
    # Calculate current risk level based on gas readings and conflicts
    current_risk = 'low'  # Default
    
    # Check for gas hazards
    if gas_readings:
        for gas, reading in gas_readings.items():
            if reading.get('status') == 'alarm':
                current_risk = 'critical'
                break
            elif reading.get('status') == 'warning':
                if current_risk != 'critical':
                    current_risk = 'high'
    
    # Check for conflicts
    if conflicts:
        unresolved_critical = any(
            conflict.severity == RiskLevel.CRITICAL for conflict in conflicts
        )
        unresolved_high = any(
            conflict.severity == RiskLevel.HIGH for conflict in conflicts
        )
        
        if unresolved_critical:
            current_risk = 'critical'
        elif unresolved_high and current_risk not in ['critical']:
            current_risk = 'high'
        elif conflicts and current_risk == 'low':
            current_risk = 'medium'
    
    # Consider number of active permits
    if active_count > 5 and current_risk == 'low':
        current_risk = 'medium'
    elif active_count > 8:
        if current_risk not in ['critical']:
            current_risk = 'high'
    
    stats = {
        'active_permits': active_count,
        'pending_permits': pending_permits,
        'conflicts_today': conflicts_today,
        'compliance_rate': compliance_rate
    }
    
    return render_template(
        'demo3/dashboard.html',
        active_permits=active_permits,
        recent_readings=recent_readings,
        gas_readings=gas_readings,
        conflicts=conflicts,
        heatmap=heatmap,
        agent_status=safety_agent.get_status(),
        stats=stats,
        current_risk=current_risk
    )

@demo3_bp.route('/api/gas-readings')
def api_gas_readings():
    """Get current gas readings for real-time updates"""
    latest_reading = GasSensorReading.query.order_by(
        GasSensorReading.created_at.desc()
    ).first()
    
    if not latest_reading:
        return jsonify({'error': 'No readings available'}), 404
    
    return jsonify({
        'O2': {
            'value': latest_reading.o2_percentage or 20.9,
            'threshold': 19.5,
            'status': 'safe' if (latest_reading.o2_percentage or 20.9) >= 19.5 else 'alarm'
        },
        'LEL': {
            'value': latest_reading.lel_percentage or 0,
            'threshold': 10.0,
            'status': 'safe' if (latest_reading.lel_percentage or 0) < 10 else 'alarm'
        },
        'H2S': {
            'value': latest_reading.h2s_ppm or 0,
            'threshold': 10.0,
            'status': 'safe' if (latest_reading.h2s_ppm or 0) < 10 else 'alarm'
        },
        'CO': {
            'value': latest_reading.co_ppm or 0,
            'threshold': 25.0,
            'status': 'safe' if (latest_reading.co_ppm or 0) < 25 else 'alarm'
        },
        'timestamp': latest_reading.created_at.isoformat()
    })


@demo3_bp.route('/api/analyze-risk', methods=['POST'])
def api_analyze_risk():
    """Analyze risk for a specific area or permit"""
    data = request.get_json()
    area = data.get('area', 'unknown')
    
    # Get recent readings for the area
    recent_readings = GasSensorReading.query.filter_by(
        area=area
    ).order_by(GasSensorReading.created_at.desc()).limit(5).all()
    
    # Get active permits in the area
    active_permits = PermitToWork.query.filter(
        PermitToWork.work_area.contains(area),
        PermitToWork.status == PermitStatus.ACTIVE
    ).count()
    
    # Calculate risk score
    risk_score = 0
    risk_factors = []
    
    if recent_readings:
        latest = recent_readings[0]
        if latest.alert_level and latest.alert_level != AlertLevel.NORMAL:
            risk_score += 30
            risk_factors.append(f"Gas alert level: {latest.alert_level.value}")
    
    if active_permits > 3:
        risk_score += 20
        risk_factors.append(f"High permit activity: {active_permits} active permits")
    
    # Check for conflicts
    conflicts = SafetyConflict.query.filter_by(
        resolved=False
    ).filter(
        SafetyConflict.area.contains(area)
    ).count()
    
    if conflicts > 0:
        risk_score += 25
        risk_factors.append(f"{conflicts} unresolved safety conflicts")
    
    return jsonify({
        'area': area,
        'risk_score': min(risk_score, 100),
        'risk_level': 'high' if risk_score >= 70 else 'medium' if risk_score >= 40 else 'low',
        'risk_factors': risk_factors,
        'active_permits': active_permits,
        'timestamp': datetime.now().isoformat()
    })

@demo3_bp.route('/api/safety-analysis', methods=['POST'])
@login_required
def api_safety_analysis():
    """Run safety analysis"""
    # Get current environment state
    gas_readings = {}
    for area in ['CDU', 'FCC', 'Storage', 'Loading', 'Utilities', 'Admin']:
        gas_readings[area] = simulator.get_state(demo_id=3)['gas_readings']
    
    # Get active permits (mock data)
    active_permits = [
        {
            'permit_number': f'PTW-{datetime.now().strftime("%Y%m%d")}-{1000+i}',
            'permit_type': random.choice(['hot_work', 'confined_space', 'electrical']),
            'area': random.choice(list(gas_readings.keys())),
            'coordinates_x': random.uniform(20, 80),
            'coordinates_y': random.uniform(20, 80),
            'coordinates_z': random.uniform(0, 8),
            'start_time': (datetime.now() - timedelta(hours=random.randint(1, 4))).isoformat(),
            'end_time': (datetime.now() + timedelta(hours=random.randint(1, 3))).isoformat()
        }
        for i in range(random.randint(3, 6))
    ]
    
    environment = {
        'gas_readings': gas_readings,
        'active_permits': active_permits
    }
    
    # Run agent analysis
    result = safety_agent.run_cycle(environment)
    
    if result['success']:
        # Save conflicts to database
        for recommendation in result['result']['actions_taken']:
            if recommendation['action_type'] == 'emergency_response':
                # Create safety conflict record
                conflict = SafetyConflict(
                    conflict_type='gas_alarm',
                    severity=RiskLevel.CRITICAL,
                    description=recommendation['description'],
                    detected_by_agent=safety_agent.agent_id,
                    confidence_score=safety_agent.confidence
                )
                conflict.save()
        
        return jsonify({
            'success': True,
            'analysis': result['result'],
            'explanation': safety_agent.explain(result['decision'])
        })
    
    return jsonify({'success': False, 'error': result.get('error')}), 500


@demo3_bp.route('/permits')
@login_required
def permits():
    """Permits management page"""
    all_permits = PermitToWork.query.order_by(
        PermitToWork.created_at.desc()
    ).limit(50).all()
    
    return render_template('demo3/permits.html', permits=all_permits)


@demo3_bp.route('/gas-monitoring')
@login_required
def gas_monitoring():
    """Gas monitoring page"""
    sensors = GasSensorReading.query.order_by(
        GasSensorReading.created_at.desc()
    ).limit(100).all()
    
    return render_template('demo3/gas_monitoring.html', sensors=sensors)


@demo3_bp.route('/risk-heatmap')
@login_required
def risk_heatmap():
    """3D risk heatmap visualization"""
    return render_template('demo3/risk_heatmap.html')


@demo3_bp.route('/api/generate-procedure', methods=['POST'])
@login_required
def api_generate_procedure():
    """Generate safety procedure for scenario"""
    data = request.get_json()
    
    procedure = safety_agent.generate_safety_procedure(data)
    
    return jsonify({
        'success': True,
        'procedure': procedure
    })