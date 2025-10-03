"""
Agent Orchestrator - Coordinates specialized agents to solve complex problems.
Central hub that manages workflows and synthesizes results.
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from .specialized_agents import (
    formulation_agent,
    test_protocol_agent,
    regulatory_agent,
    supply_chain_agent,
    knowledge_mining_agent
)
from .event_simulator import SystemEvent, EventType, event_simulator
from .message_queue import message_queue, Message


class AgentOrchestrator:
    """
    The AgentOrchestrator is like a skilled project manager who knows which
    experts to call for each type of problem, how to coordinate their work,
    and how to synthesize their inputs into actionable recommendations.
    
    It maintains several key responsibilities:
    1. Intent Classification: Understanding what the user is asking for
    2. Agent Selection: Choosing which agents to involve
    3. Workflow Coordination: Managing the sequence and timing
    4. Context Propagation: Ensuring agents have the information they need
    5. Result Aggregation: Combining outputs into a unified response
    """
    
    def __init__(self):
        self.orchestrator_id = "knowledge-orchestrator-001"
        
        # Available agents and their capabilities
        self.agents = {
            'formulation': formulation_agent,
            'protocol': test_protocol_agent,
            'regulatory': regulatory_agent,
            'supply_chain': supply_chain_agent,
            'knowledge': knowledge_mining_agent
        }
        
        # Conversation context for multi-turn interactions
        self.conversation_context = {}
        
        # Track active workflows
        self.active_workflows = {}
        
        # Statistics for monitoring
        self.stats = {
            'requests_processed': 0,
            'total_agents_invoked': 0,
            'average_response_time_ms': 0
        }
    
    def classify_intent(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Classify the user's intent to determine which agents to invoke and
        what workflow to follow.
        
        In production, this would use an NLP model. For our demo, we use
        keyword matching which is surprisingly effective for domain-specific
        applications.
        
        Intent types include:
        - formulation_request: User wants formulation recommendations
        - protocol_request: User wants test procedures
        - compliance_check: User needs regulatory verification
        - research_query: User wants historical insights
        - cost_analysis: User wants supply chain optimization
        """
        query_lower = query.lower()
        
        # Intent classification logic
        intent = {
            'type': 'general_query',
            'confidence': 0.5,
            'required_agents': [],
            'workflow': 'simple'
        }
        
        # Check for formulation requests
        if any(keyword in query_lower for keyword in [
            'formulation', 'recommend', 'recipe', 'blend', 'optimize'
        ]):
            intent.update({
                'type': 'formulation_request',
                'confidence': 0.95,
                'required_agents': ['formulation', 'regulatory', 'supply_chain'],
                'workflow': 'parallel_with_synthesis'
            })
        
        # Check for protocol requests
        elif any(keyword in query_lower for keyword in [
            'test', 'protocol', 'procedure', 'astm', 'bis'
        ]):
            intent.update({
                'type': 'protocol_request',
                'confidence': 0.90,
                'required_agents': ['protocol'],
                'workflow': 'simple'
            })
        
        # Check for compliance queries
        elif any(keyword in query_lower for keyword in [
            'complian', 'regulat', 'standard', 'certification', 'permit'
        ]):
            intent.update({
                'type': 'compliance_check',
                'confidence': 0.92,
                'required_agents': ['regulatory'],
                'workflow': 'simple'
            })
        
        # Check for research queries
        elif any(keyword in query_lower for keyword in [
            'research', 'paper', 'historical', 'past', 'literature'
        ]):
            intent.update({
                'type': 'research_query',
                'confidence': 0.88,
                'required_agents': ['knowledge'],
                'workflow': 'simple'
            })
        
        # Check for cost/supply chain queries
        elif any(keyword in query_lower for keyword in [
            'cost', 'price', 'supplier', 'availability', 'lead time'
        ]):
            intent.update({
                'type': 'cost_analysis',
                'confidence': 0.85,
                'required_agents': ['supply_chain'],
                'workflow': 'simple'
            })
        
        return intent
    
    async def process_formulation_request(
        self, 
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a formulation request through the complete workflow.
        
        This is the most complex workflow, involving multiple agents working
        in parallel and sequence. The flow is:
        
        1. Formulation Agent analyzes requirements and generates recommendations
        2. In parallel, we check:
           - Regulatory compliance for each recommendation
           - Supply chain feasibility
           - Historical performance data
        3. Synthesize all inputs into final recommendations with full context
        
        This demonstrates the power of the multi-agent architecture - each agent
        focuses on what it does best, and the orchestrator weaves their insights
        together.
        """
        workflow_id = f'WF-{datetime.now().strftime("%Y%m%d%H%M%S")}'
        start_time = datetime.now()
        
        # Emit workflow start event
        workflow_start = SystemEvent(
            event_type=EventType.FORMULATION_REQUEST,
            source_system='UI',
            target_system=self.orchestrator_id,
            correlation_id=workflow_id,
            payload={'requirements': requirements}
        )
        event_simulator.emit_event(workflow_start)
        
        # Simulate UI -> Gateway -> Orchestrator flow
        gateway_event = SystemEvent(
            event_type=EventType.FORMULATION_REQUEST,
            source_system='Unified Gateway',
            target_system=self.orchestrator_id,
            correlation_id=workflow_id,
            payload={'routed_from': 'UI'}
        )
        event_simulator.emit_event(gateway_event)
        
        # Track this workflow
        self.active_workflows[workflow_id] = {
            'type': 'formulation_request',
            'start_time': start_time,
            'status': 'in_progress',
            'steps_completed': 0,
            'total_steps': 5
        }
        
        try:
            # Step 1: Formulation Agent analyzes requirements and gathers data
            print(f"[Orchestrator] Step 1/5: Analyzing requirements...")
            
            # Emit orchestrator -> formulation agent event
            orchestrator_to_agent = SystemEvent(
                event_type=EventType.AGENT_ANALYSIS_START,
                source_system=self.orchestrator_id,
                target_system='formulation-agent-001',
                correlation_id=workflow_id,
                payload={'step': 1, 'action': 'analyze_requirements'}
            )
            event_simulator.emit_event(orchestrator_to_agent)
            
            analysis = await formulation_agent.analyze_requirements(requirements)
            self.active_workflows[workflow_id]['steps_completed'] = 1
            
            # Step 2: Generate formulation recommendations
            print(f"[Orchestrator] Step 2/5: Generating formulation recommendations...")
            
            # Emit agent -> RAG engine for knowledge retrieval
            agent_to_rag = SystemEvent(
                event_type=EventType.RAG_QUERY_INITIATED,
                source_system='formulation-agent-001',
                target_system='RAG_Engine',
                correlation_id=workflow_id,
                payload={'query_type': 'formulation_knowledge'}
            )
            event_simulator.emit_event(agent_to_rag)
            
            # Emit RAG -> Vector DB
            rag_to_vector = SystemEvent(
                event_type=EventType.VECTOR_SEARCH_STARTED,
                source_system='RAG_Engine',
                target_system='Vector_DB',
                correlation_id=workflow_id,
                payload={'search_type': 'semantic_similarity'}
            )
            event_simulator.emit_event(rag_to_vector)
            
            # Emit Vector DB -> LLM Models
            vector_to_llm = SystemEvent(
                event_type=EventType.LLM_INFERENCE_START,
                source_system='Vector_DB',
                target_system='LLM_Models',
                correlation_id=workflow_id,
                payload={'model_type': 'formulation_assistant'}
            )
            event_simulator.emit_event(vector_to_llm)
            
            recommendations = await formulation_agent.generate_recommendations(analysis)
            self.active_workflows[workflow_id]['steps_completed'] = 2
            
            # Step 3: Parallel processing - check regulatory, supply chain, and research
            print(f"[Orchestrator] Step 3/5: Running parallel checks (regulatory, supply chain, research)...")
            
            # Create tasks that run concurrently
            tasks = []
            
            # Check regulatory compliance for first recommendation
            if recommendations:
                tasks.append(
                    regulatory_agent.check_compliance(
                        recommendations[0],
                        target_markets=['India', 'Middle East']
                    )
                )
            
            # Analyze supply chain for first recommendation
            if recommendations:
                tasks.append(
                    supply_chain_agent.analyze_supply_chain(recommendations[0])
                )
            
            # Search research literature
            tasks.append(
                knowledge_mining_agent.search_research_literature({
                    'product_type': requirements.get('product_type', '5W-30'),
                    'focus_areas': ['viscosity_optimization', 'cost_reduction']
                })
            )
            
            # Emit events for parallel processing
            # Regulatory agent -> Regulatory DB
            reg_event = SystemEvent(
                event_type=EventType.REGULATORY_STANDARD_CHECK,
                source_system='regulatory-agent-001',
                target_system='Regulatory_DB',
                correlation_id=workflow_id,
                payload={'standards': ['API SN Plus', 'ACEA C3']}
            )
            event_simulator.emit_event(reg_event)
            
            # Supply chain agent -> SAP ERP
            sap_event = SystemEvent(
                event_type=EventType.SAP_MATERIAL_QUERY,
                source_system='supply-chain-agent-001',
                target_system='SAP_ERP',
                correlation_id=workflow_id,
                payload={'query_type': 'material_availability'}
            )
            event_simulator.emit_event(sap_event)
            
            # Supply chain agent -> Supplier Portal via MCP Gateway
            mcp_event = SystemEvent(
                event_type=EventType.MCP_CONNECTION_ESTABLISHED,
                source_system='supply-chain-agent-001',
                target_system='MCP_Gateway',
                correlation_id=workflow_id,
                payload={'target_system': 'Supplier_Portal'}
            )
            event_simulator.emit_event(mcp_event)
            
            supplier_event = SystemEvent(
                event_type=EventType.SUPPLIER_AVAILABILITY_CHECK,
                source_system='MCP_Gateway',
                target_system='Supplier_Portal',
                correlation_id=workflow_id,
                payload={'materials': ['PAO4', 'ZDDP', 'Calcium Sulfonate']}
            )
            event_simulator.emit_event(supplier_event)
            
            # Knowledge mining agent -> LIMS via MCP Gateway
            lims_event = SystemEvent(
                event_type=EventType.LIMS_TEST_QUERY,
                source_system='MCP_Gateway',
                target_system='LIMS',
                correlation_id=workflow_id,
                payload={'query_type': 'historical_data'}
            )
            event_simulator.emit_event(lims_event)
            
            # Run all checks in parallel
            parallel_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Extract results (with error handling)
            compliance_report = parallel_results[0] if len(parallel_results) > 0 else None
            supply_chain_analysis = parallel_results[1] if len(parallel_results) > 1 else None
            research_insights = parallel_results[2] if len(parallel_results) > 2 else None
            
            self.active_workflows[workflow_id]['steps_completed'] = 3
            
            # Step 4: Generate test protocol for best recommendation
            print(f"[Orchestrator] Step 4/5: Generating test protocol...")
            
            # Emit protocol agent -> LIMS for test procedures
            protocol_to_lims = SystemEvent(
                event_type=EventType.LIMS_TEST_QUERY,
                source_system='test-protocol-agent-001',
                target_system='LIMS',
                correlation_id=workflow_id,
                payload={'query_type': 'test_protocols'}
            )
            event_simulator.emit_event(protocol_to_lims)
            
            # Emit protocol agent -> PLM for specifications
            protocol_to_plm = SystemEvent(
                event_type=EventType.PLM_SPECIFICATION_QUERY,
                source_system='test-protocol-agent-001',
                target_system='PLM',
                correlation_id=workflow_id,
                payload={'query_type': 'product_specifications'}
            )
            event_simulator.emit_event(protocol_to_plm)
            
            if recommendations:
                test_protocol = await test_protocol_agent.generate_protocol(recommendations[0])
            else:
                test_protocol = None
            
            self.active_workflows[workflow_id]['steps_completed'] = 4
            
            # Step 5: Synthesize all results into comprehensive response
            print(f"[Orchestrator] Step 5/5: Synthesizing final response...")
            
            # Calculate processing time
            end_time = datetime.now()
            processing_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Build comprehensive response
            response = {
                'workflow_id': workflow_id,
                'status': 'success',
                'processing_time_ms': processing_time_ms,
                'timestamp': datetime.now().isoformat(),
                
                # Core recommendations
                'recommendations': recommendations,
                'recommended_count': len(recommendations),
                
                # Supporting analysis
                'regulatory_compliance': compliance_report,
                'supply_chain_analysis': supply_chain_analysis,
                'research_insights': research_insights,
                'test_protocol': test_protocol,
                
                # Original request context
                'requirements': requirements,
                
                # Agent contributions
                'agents_involved': [
                    'FormulationAgent',
                    'RegulatoryAgent',
                    'SupplyChainAgent',
                    'KnowledgeMiningAgent',
                    'TestProtocolAgent'
                ],
                
                # Executive summary
                'summary': self._generate_summary(
                    recommendations,
                    compliance_report,
                    supply_chain_analysis
                )
            }
            
            # Update workflow status
            self.active_workflows[workflow_id].update({
                'status': 'completed',
                'steps_completed': 5,
                'end_time': end_time,
                'processing_time_ms': processing_time_ms
            })
            
            # Update statistics
            self.stats['requests_processed'] += 1
            self.stats['total_agents_invoked'] += len(response['agents_involved'])
            
            # Calculate moving average of response times
            current_avg = self.stats['average_response_time_ms']
            n = self.stats['requests_processed']
            self.stats['average_response_time_ms'] = (
                (current_avg * (n - 1) + processing_time_ms) / n
            )
            
            # Emit completion event
            completion_event = SystemEvent(
                event_type=EventType.AGENT_RECOMMENDATION_READY,
                source_system=self.orchestrator_id,
                correlation_id=workflow_id,
                payload={
                    'recommendations': len(recommendations),
                    'processing_time_ms': processing_time_ms
                }
            )
            event_simulator.emit_event(completion_event)
            
            # Publish to message queue for other systems
            message_queue.publish(
                topic='formulation.completed',
                payload=response,
                correlation_id=workflow_id
            )
            
            return response
            
        except Exception as e:
            # Handle errors gracefully
            self.active_workflows[workflow_id]['status'] = 'failed'
            self.active_workflows[workflow_id]['error'] = str(e)
            
            error_event = SystemEvent(
                event_type=EventType.SYSTEM_ERROR,
                source_system=self.orchestrator_id,
                correlation_id=workflow_id,
                payload={'error': str(e)}
            )
            event_simulator.emit_event(error_event)
            
            raise
    
    def _generate_summary(
        self,
        recommendations: List[Dict[str, Any]],
        compliance: Optional[Dict[str, Any]],
        supply_chain: Optional[Dict[str, Any]]
    ) -> str:
        """
        Generate an executive summary that distills the analysis into key takeaways.
        
        This is what a busy R&D manager wants to see first - the bottom line
        before diving into details.
        """
        if not recommendations:
            return "No viable recommendations could be generated based on the requirements."
        
        best_rec = recommendations[0]
        
        summary_parts = []
        
        # Main recommendation
        summary_parts.append(
            f"Recommended formulation: {best_rec['name']} using {best_rec['composition']['base_oil']['type']} "
            f"base oil at ₹{best_rec['total_cost_per_liter_inr']:.2f}/liter."
        )
        
        # Performance
        props = best_rec.get('predicted_properties', {})
        if 'viscosity_index' in props:
            summary_parts.append(
                f"Expected performance: VI {props['viscosity_index']}, "
                f"performance score {props.get('performance_score', 'N/A')}/100."
            )
        
        # Compliance status
        if compliance and 'compliance_summary' in compliance:
            status = compliance['compliance_summary'].get('overall_status', 'unknown')
            summary_parts.append(f"Regulatory status: {status}.")
        
        # Supply chain
        if supply_chain and 'supply_chain_score' in supply_chain:
            score = supply_chain['supply_chain_score']
            summary_parts.append(
                f"Supply chain feasibility: {score:.0%} "
                f"(all materials available with acceptable lead times)."
            )
        
        # Timeline
        dev_time = best_rec.get('development_time_weeks', 6)
        summary_parts.append(
            f"Estimated time to market: {dev_time} weeks including testing and certification."
        )
        
        return " ".join(summary_parts)
    
    async def process_simple_query(
        self, 
        intent: Dict[str, Any],
        query_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process simpler queries that only need one agent. This is much faster
        than the full formulation workflow.
        """
        workflow_id = f'WF-{datetime.now().strftime("%Y%m%d%H%M%S")}'
        start_time = datetime.now()
        
        intent_type = intent['type']
        required_agents = intent['required_agents']
        
        result = None
        
        # Route to appropriate agent
        if 'protocol' in required_agents:
            result = await test_protocol_agent.generate_protocol(query_data)
        
        elif 'regulatory' in required_agents:
            result = await regulatory_agent.check_compliance(
                query_data,
                target_markets=['India']
            )
        
        elif 'knowledge' in required_agents:
            result = await knowledge_mining_agent.search_research_literature(query_data)
        
        elif 'supply_chain' in required_agents:
            result = await supply_chain_agent.analyze_supply_chain(query_data)
        
        # Calculate processing time
        processing_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        response = {
            'workflow_id': workflow_id,
            'status': 'success',
            'intent': intent_type,
            'processing_time_ms': processing_time_ms,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }
        
        # Update statistics
        self.stats['requests_processed'] += 1
        self.stats['total_agents_invoked'] += len(required_agents)
        
        return response
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get orchestrator statistics for monitoring and debugging.
        """
        return {
            'orchestrator_id': self.orchestrator_id,
            'requests_processed': self.stats['requests_processed'],
            'total_agents_invoked': self.stats['total_agents_invoked'],
            'average_response_time_ms': round(self.stats['average_response_time_ms'], 2),
            'active_workflows': len([w for w in self.active_workflows.values() if w['status'] == 'in_progress']),
            'available_agents': list(self.agents.keys()),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a specific workflow. Useful for tracking long-running
        processes in the UI.
        """
        return self.active_workflows.get(workflow_id)


# Create singleton instance
agent_orchestrator = AgentOrchestrator()
