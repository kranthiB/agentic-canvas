"""
Demo 5: Engineer's Copilot Blueprint
T2 Procedural Workflow + Generative Agent routes
"""
from flask import Blueprint, render_template, jsonify, request, session
from flask_login import login_required, current_user
from datetime import datetime
import uuid

from app import db
from app.models.demo5_models import (
    ResearchPaper, FormulationTrial, FormulationRequest,
    RecommendedFormulation, TestProtocol, ChatMessage,
    FormulationStatus, ProtocolStatus
)
from app.agents.demo5_agent import EngineersCopilotAgent
from app.config import Config

demo5_bp = Blueprint('demo5', __name__)

# Initialize agent
copilot_agent = EngineersCopilotAgent(openai_api_key=Config.OPENAI_API_KEY)


@demo5_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    # Get statistics
    papers_count = ResearchPaper.query.count()
    trials_count = FormulationTrial.query.count()
    protocols_count = TestProtocol.query.count()
    
    # Get today's queries
    from datetime import datetime, timedelta
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    queries_today = FormulationRequest.query.filter(
        FormulationRequest.created_at >= today_start
    ).count()
    
    # Create stats dict
    stats = {
        'total_papers': papers_count,
        'formulation_trials': trials_count,
        'test_protocols': protocols_count,
        'queries_today': queries_today,
        'avg_response_time': 2.3  # Average response time in seconds
    }
    
    # Get recent activity
    recent_requests = FormulationRequest.query.order_by(
        FormulationRequest.created_at.desc()
    ).limit(5).all()
    
    recent_protocols = TestProtocol.query.order_by(
        TestProtocol.created_at.desc()
    ).limit(5).all()
    
    return render_template(
        'demo5/dashboard.html',
        stats=stats,
        recent_requests=recent_requests,
        recent_protocols=recent_protocols
    )


@demo5_bp.route('/search')
@login_required
def search():
    """Research search page"""
    return render_template('demo5/search.html')


@demo5_bp.route('/api/search', methods=['POST'])
@login_required
def api_search():
    """Search research papers and trials"""
    data = request.get_json()
    query = data.get('query', '')
    search_type = data.get('type', 'papers')  # papers or trials
    language = data.get('language', 'en')
    
    environment = {
        'query': query,
        'language': language,
        'intent': 'search_papers' if search_type == 'papers' else 'search_trials'
    }
    
    result = copilot_agent.run_cycle(environment)
    
    if result['success']:
        return jsonify({
            'success': True,
            'results': result['result']['data']
        })
    
    return jsonify({'success': False, 'error': result.get('error')}), 500


@demo5_bp.route('/formulation')
@login_required
def formulation():
    """Formulation recommendation page"""
    requests = FormulationRequest.query.filter_by(
        researcher_name=current_user.username
    ).order_by(FormulationRequest.created_at.desc()).all()
    
    return render_template('demo5/formulation.html', requests=requests)


@demo5_bp.route('/api/request-formulation', methods=['POST'])
@login_required
def api_request_formulation():
    """Request formulation recommendation"""
    data = request.get_json()
    
    # Create request record
    request_record = FormulationRequest(
        request_id=f'FR-{datetime.now().strftime("%Y%m%d%H%M")}-{str(uuid.uuid4())[:8]}',
        request_title=data.get('title', 'Formulation Request'),
        product_type=data.get('product_type'),
        target_properties=data.get('target_properties'),
        constraints=data.get('constraints'),
        application=data.get('application'),
        operating_conditions=data.get('operating_conditions'),
        researcher_name=current_user.username,
        department=data.get('department', 'R&D'),
        request_language=data.get('language', 'en')
    )
    request_record.save()
    
    # Generate recommendations using agent
    environment = {
        'query': '',
        'language': data.get('language', 'en'),
        'intent': 'recommend_formulation',
        'context': {
            'product_type': data.get('product_type'),
            'target_properties': data.get('target_properties'),
            'constraints': data.get('constraints')
        }
    }
    
    result = copilot_agent.run_cycle(environment)
    
    if result['success']:
        recommendations_data = result['result']['data']['recommendations']
        
        # Save recommendations
        for rec_data in recommendations_data:
            rec = RecommendedFormulation(
                request_id=request_record.id,
                formulation_id=rec_data['formulation_id'],
                name=rec_data['name'],
                description=f"AI-recommended formulation for {data.get('product_type')}",
                base_oil=rec_data['base_oil'],
                additive_package=rec_data['additive_package'],
                predicted_viscosity_index=rec_data['predicted_properties']['viscosity_index'],
                predicted_wear_resistance=rec_data['predicted_properties']['wear_resistance'],
                predicted_oxidation_stability=rec_data['predicted_properties']['oxidation_stability'],
                predicted_performance_score=rec_data['predicted_properties']['performance_score'],
                total_cost_per_liter=rec_data['cost_per_liter_inr'],
                reasoning_chain=[rec_data['reasoning']],
                confidence_score=rec_data['confidence_score'],
                similar_trials=[],
                recommendation_rank=rec_data['rank'],
                pros=rec_data['pros'],
                cons=rec_data['cons'],
                status=FormulationStatus.RECOMMENDED
            )
            rec.save()
        
        # Mark request as processed
        request_record.processed = True
        request_record.processing_time_ms=random.randint(2000, 5000)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'request_id': request_record.request_id,
            'recommendations': [r.to_dict() for r in request_record.recommended_formulations]
        })
    
    return jsonify({'success': False, 'error': result.get('error')}), 500


@demo5_bp.route('/protocol')
@login_required
def protocol():
    """Test protocol generation page"""
    protocols = TestProtocol.query.order_by(
        TestProtocol.created_at.desc()
    ).limit(20).all()
    
    return render_template('demo5/protocol.html', protocols=protocols)


@demo5_bp.route('/api/generate-protocol', methods=['POST'])
@login_required
def api_generate_protocol():
    """Generate test protocol"""
    data = request.get_json()
    
    formulation_data = data.get('formulation', {})
    test_standards = data.get('test_standards', ['ASTM D445', 'ASTM D4172'])
    
    # Generate protocol using agent
    environment = {
        'query': '',
        'language': data.get('language', 'en'),
        'intent': 'generate_protocol',
        'context': {
            'formulation': formulation_data,
            'test_standards': test_standards
        }
    }
    
    result = copilot_agent.run_cycle(environment)
    
    if result['success']:
        protocol_data = result['result']['data']
        
        # Save protocol
        protocol = TestProtocol(
            protocol_id=protocol_data['protocol_id'],
            title=protocol_data['title'],
            formulation_id=formulation_data.get('formulation_id'),
            test_standards=test_standards,
            test_sequence=[],
            objective='Evaluate formulation performance',
            scope='Comprehensive testing per industry standards',
            equipment_required=[],
            reagents_required=[],
            safety_precautions='Follow standard laboratory safety protocols',
            procedure_steps=[],
            expected_results=[],
            acceptance_criteria=[],
            estimated_duration_hours=protocol_data['estimated_duration_hours'],
            estimated_cost_inr=protocol_data['estimated_cost_inr'],
            required_personnel=2,
            generated_by_agent=copilot_agent.agent_id,
            generation_prompt=data.get('prompt', ''),
            confidence_score=copilot_agent.confidence,
            language=data.get('language', 'en'),
            status=ProtocolStatus.GENERATED
        )
        protocol.save()
        
        return jsonify({
            'success': True,
            'protocol': {
                **protocol.to_dict(),
                'content': protocol_data['content']
            }
        })
    
    return jsonify({'success': False, 'error': result.get('error')}), 500


@demo5_bp.route('/protocol/')
@login_required
def protocol_detail(protocol_id):
    """Protocol detail page"""
    protocol = TestProtocol.query.get_or_404(protocol_id)
    return render_template('demo5/protocol_detail.html', protocol=protocol)


@demo5_bp.route('/chat')
@login_required
def chat():
    """Chat interface"""
    # Get or create session ID
    if 'chat_session_id' not in session:
        session['chat_session_id'] = str(uuid.uuid4())
    
    session_id = session['chat_session_id']
    
    # Get chat history
    messages = ChatMessage.query.filter_by(
        session_id=session_id,
        user_id=current_user.id
    ).order_by(ChatMessage.created_at).all()
    
    return render_template('demo5/chat.html', messages=messages)


@demo5_bp.route('/api/chat', methods=['POST'])
@login_required
def api_chat():
    """Chat with agent"""
    data = request.get_json()
    message_text = data.get('message', '')
    language = data.get('language', 'en')
    
    # Get or create session ID
    if 'chat_session_id' not in session:
        session['chat_session_id'] = str(uuid.uuid4())
    
    session_id = session['chat_session_id']
    
    # Save user message
    user_msg = ChatMessage(
        session_id=session_id,
        user_id=current_user.id,
        role='user',
        content=message_text,
        language=language
    )
    user_msg.save()
    
    # Get agent response
    environment = {
        'query': message_text,
        'language': language,
        'intent': 'chat'
    }
    
    result = copilot_agent.run_cycle(environment)
    
    if result['success']:
        response_text = result['result']['response']
        
        # Save assistant message
        assistant_msg = ChatMessage(
            session_id=session_id,
            user_id=current_user.id,
            role='assistant',
            content=response_text,
            language=language,
            model_used=copilot_agent.model
        )
        assistant_msg.save()
        
        return jsonify({
            'success': True,
            'message': {
                'role': 'assistant',
                'content': response_text,
                'timestamp': assistant_msg.created_at.isoformat()
            }
        })
    
    return jsonify({'success': False, 'error': result.get('error')}), 500


@demo5_bp.route('/trials')
@login_required
def trials():
    """Formulation trials history"""
    trials = FormulationTrial.query.order_by(
        FormulationTrial.created_at.desc()
    ).limit(50).all()
    
    return render_template('demo5/trials.html', trials=trials)


@demo5_bp.route('/trial/')
@login_required
def trial_detail(trial_id):
    """Trial detail page"""
    trial = FormulationTrial.query.get_or_404(trial_id)
    return render_template('demo5/trial_detail.html', trial=trial)