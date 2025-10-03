"""
Additional routes for simulation and event flow visualization
This extends the existing demo5_copilot.py with simulation capabilities
"""

from flask import Blueprint, jsonify, request, Response
from flask_login import login_required, current_user
import json
import asyncio
from datetime import datetime

# Import demo5 simulation components  
from app.simulation import event_simulator, EventType, agent_orchestrator, message_queue

# Create a sub-blueprint for simulation routes
sim_bp = Blueprint('demo5_simulation', __name__)


@sim_bp.route('/event-flow')
@login_required
def event_flow_dashboard():
    """Enhanced Event Flow Dashboard"""
    from flask import render_template
    return render_template('demo5/event_flow.html')


@sim_bp.route('/api/simulate-formulation-flow', methods=['POST'])
@login_required
def api_simulate_formulation_flow():
    """
    Trigger a complete formulation workflow simulation.
    
    This endpoint demonstrates the full end-to-end flow with all systems
    and agents working together. It's the "grand tour" that shows off
    the entire architecture.
    
    The request flows through:
    1. User interface → API Gateway → Orchestrator
    2. Orchestrator → Multiple specialized agents
    3. Agents → Enterprise systems (SAP, LIMS, PLM, etc.)
    4. Systems → Response back through the chain
    5. Orchestrator → Synthesize results → User interface
    """
    try:
        data = request.get_json()
        
        # Extract requirements from request
        requirements = {
            'product_type': data.get('product_type', '5W-30'),
            'target_properties': data.get('target_properties', {
                'viscosity_index': 150,
                'wear_protection': 'high',
                'oxidation_stability': 'excellent'
            }),
            'constraints': data.get('constraints', {
                'max_cost_per_liter_inr': 150,
                'material_availability': 'standard',
                'development_timeline_weeks': 8
            }),
            'standards': data.get('standards', ['API SN Plus', 'ACEA C3']),
            'application': data.get('application', 'Passenger car engine oil'),
            'operating_conditions': data.get('operating_conditions', {
                'temperature_range': '-35°C to 150°C',
                'drain_interval': '10,000 km'
            })
        }
        
        # Run the workflow asynchronously
        # In production, this would be a background job
        # For demo, we run it synchronously but with async simulation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                agent_orchestrator.process_formulation_request(requirements)
            )
        finally:
            loop.close()
        
        # Return the complete workflow result
        return jsonify({
            'success': True,
            'workflow_id': result['workflow_id'],
            'result': result,
            'events_generated': len(event_simulator.get_event_chain(result['workflow_id']))
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@sim_bp.route('/api/events/stream')
@login_required
def event_stream():
    """
    Server-Sent Events endpoint for real-time event streaming.
    
    This keeps a persistent connection open and pushes events to the client
    as they happen. This is how we achieve the real-time animation in the UI.
    
    The client subscribes to this stream and receives events as they flow
    through the system. Each event updates the visualization in real-time.
    """
    def generate():
        """Generator that yields events as they occur"""
        # Keep track of last event index sent
        last_index = 0
        
        while True:
            # Get new events
            all_events = event_simulator.event_history
            new_events = all_events[last_index:]
            
            if new_events:
                for event in new_events:
                    # Format as Server-Sent Event
                    event_data = json.dumps(event.to_dict())
                    yield f"data: {event_data}\n\n"
                
                last_index = len(all_events)
            
            # Small delay to prevent overwhelming the client
            import time
            time.sleep(0.1)
    
    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )


@sim_bp.route('/api/events/recent')
@login_required
def get_recent_events():
    """
    Get recent events for display.
    
    This is a simple REST endpoint that returns the last N events.
    Useful for initializing the UI or for polling-based updates.
    """
    limit = request.args.get('limit', 50, type=int)
    correlation_id = request.args.get('correlation_id', None)
    
    if correlation_id:
        events = event_simulator.get_event_chain(correlation_id)
    else:
        events = event_simulator.get_recent_events(limit)
    
    return jsonify({
        'success': True,
        'events': [event.to_dict() for event in events],
        'total_events': len(event_simulator.event_history)
    })


@sim_bp.route('/api/events/metrics')
@login_required
def get_event_metrics():
    """
    Get metrics about system performance.
    
    This powers the monitoring dashboards that show things like:
    - Average response times by system
    - Event throughput
    - System health status
    - Error rates
    """
    metrics = event_simulator.get_system_metrics()
    orchestrator_stats = agent_orchestrator.get_statistics()
    queue_stats = message_queue.get_stats()
    
    return jsonify({
        'success': True,
        'timestamp': datetime.now().isoformat(),
        'event_metrics': metrics,
        'orchestrator_metrics': orchestrator_stats,
        'message_queue_metrics': queue_stats
    })


@sim_bp.route('/api/events/clear', methods=['POST'])
@login_required
def clear_event_history():
    """
    Clear event history for demo reset.
    
    This is useful when running multiple demos - you can reset the system
    to a clean state between demonstrations.
    """
    event_simulator.clear_history()
    message_queue.clear_history()
    
    return jsonify({
        'success': True,
        'message': 'Event history cleared'
    })


@sim_bp.route('/api/workflow/<workflow_id>/status')
@login_required
def get_workflow_status(workflow_id):
    """
    Get the status of a specific workflow.
    
    This allows the UI to show progress for long-running workflows.
    The response includes which step is currently executing, how many
    steps are complete, and estimated time remaining.
    """
    status = agent_orchestrator.get_workflow_status(workflow_id)
    
    if status:
        return jsonify({
            'success': True,
            'workflow_id': workflow_id,
            'status': status
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Workflow not found'
        }), 404


@sim_bp.route('/api/simulate/quick-demo', methods=['POST'])
@login_required
def quick_demo():
    """
    Run a quick demo that showcases the event flow.
    
    This is a faster version designed for presentations - it runs through
    a pre-configured scenario that hits all the key systems and produces
    a complete formulation recommendation in about 5-10 seconds.
    
    Perfect for when you want to show the system in action without waiting
    for the full workflow.
    """
    try:
        # Pre-configured demo scenario
        demo_requirements = {
            'product_type': '5W-30',
            'target_properties': {
                'viscosity_index': 155,
                'wear_protection': 'excellent',
                'oxidation_stability': 'high',
                'fuel_economy': 'improved'
            },
            'constraints': {
                'max_cost_per_liter_inr': 120,
                'material_availability': 'standard',
                'development_timeline_weeks': 6
            },
            'standards': ['API SN Plus', 'ACEA C3', 'ILSAC GF-6A'],
            'application': 'Premium synthetic motor oil for Maruti Swift',
            'operating_conditions': {
                'temperature_range': '-35°C to 150°C',
                'drain_interval': '10,000 km',
                'typical_usage': 'City and highway driving'
            }
        }
        
        # Run the simulation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                agent_orchestrator.process_formulation_request(demo_requirements)
            )
        finally:
            loop.close()
        
        return jsonify({
            'success': True,
            'workflow_id': result['workflow_id'],
            'summary': result['summary'],
            'recommendations_count': result['recommended_count'],
            'processing_time_ms': result['processing_time_ms'],
            'agents_involved': result['agents_involved'],
            'event_count': len(event_simulator.get_event_chain(result['workflow_id']))
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@sim_bp.route('/api/system/status')
@login_required
def system_status():
    """
    Get the current status of all systems.
    
    This shows which systems are "online" and responsive. In our simulation,
    all systems are always online, but in production this would check actual
    system health.
    
    Returns health status for:
    - SAP ERP
    - LIMS
    - PLM
    - Regulatory Databases
    - Supplier Portals
    - Message Queue
    - All AI Agents
    """
    return jsonify({
        'success': True,
        'timestamp': datetime.now().isoformat(),
        'systems': event_simulator.system_status,
        'agents': {
            'FormulationAgent': 'online',
            'TestProtocolAgent': 'online',
            'RegulatoryAgent': 'online',
            'SupplyChainAgent': 'online',
            'KnowledgeMiningAgent': 'online'
        },
        'orchestrator': 'online',
        'message_queue': 'online'
    })


# Register the simulation blueprint with the main demo5 blueprint
# This will be imported and registered in the main __init__.py
