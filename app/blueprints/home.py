"""
Home Blueprint
Landing page and demo selector
"""
from flask import Blueprint, render_template, jsonify
from app.core.simulator import simulator

home_bp = Blueprint('home', __name__)


@home_bp.route('/')
def index():
    """Landing page with demo selector"""
    demos = [
        {
            'id': 1,
            'name': 'Carbon Compass',
            'description': 'T3 Cognitive Agent for emissions optimization',
            'icon': '🌍',
            'capabilities': ['CG.RS', 'CG.DC', 'LA.RL', 'GS.MO'],
            'url': '/demo1/dashboard',
            'color': 'success'
        },
        {
            'id': 2,
            'name': 'GridMind AI',
            'description': 'T4 Multi-Agent System for renewable energy',
            'icon': '⚡',
            'capabilities': ['IC.DS', 'IC.CF', 'IC.CS', 'LA.MM'],
            'url': '/demo2/dashboard',
            'color': 'warning'
        },
        {
            'id': 3,
            'name': 'Safety Guardian',
            'description': 'T2 Procedural Agent for refinery safety',
            'icon': '🛡️',
            'capabilities': ['PK.OB', 'CG.PS', 'IC.HL', 'GS.SF'],
            'url': '/demo3/dashboard',
            'color': 'danger'
        },
        {
            'id': 4,
            'name': 'Mobility Maestro',
            'description': 'T3 Cognitive Agent for EV network optimization',
            'icon': '🔌',
            'capabilities': ['CG.PS', 'CG.DC', 'AE.TL', 'LA.SL'],
            'url': '/demo4/dashboard',
            'color': 'info'
        },
        {
            'id': 5,
            'name': "Engineer's Copilot",
            'description': 'T2 Generative Agent for R&D acceleration',
            'icon': '🔬',
            'capabilities': ['PK.KB', 'CG.RS', 'AE.CX', 'IC.NL'],
            'url': '/demo5/dashboard',
            'color': 'primary'
        }
    ]
    
    return render_template('home.html', demos=demos)


@home_bp.route('/about')
def about():
    """About the Agentic Canvas"""
    return render_template('about.html')


@home_bp.route('/api/status')
def api_status():
    """API health check"""
    return jsonify({
        'status': 'healthy',
        'simulator_running': simulator.running,
        'timestamp': simulator.get_state()['demo1']['timestamp']
    })