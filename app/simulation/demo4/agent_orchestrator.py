"""
Agent Orchestrator - Central coordinator for EV Charging Network multi-agent system
Manages workflows and synthesizes results from specialized agents
"""
import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

from .specialized_agents import (
    geographic_intelligence_agent,
    financial_analysis_agent,
    permit_management_agent,
    market_intelligence_agent,
    network_optimization_agent
)
from .event_simulator import SystemEvent, EventType, event_simulator
from .message_queue import message_queue

logger = logging.getLogger(__name__)


class EVChargingOrchestrator:
    """
    Central orchestrator for EV charging network expansion and optimization.
    Coordinates multiple specialized agents to solve complex problems.
    """
    
    def __init__(self):
        self.orchestrator_id = "ev-charging-orchestrator-001"
        
        # Available agents
        self.agents = {
            'geographic': geographic_intelligence_agent,
            'financial': financial_analysis_agent,
            'permit': permit_management_agent,
            'market': market_intelligence_agent,
            'network': network_optimization_agent
        }
        
        # Active workflows
        self.active_workflows = {}
        
        # Statistics
        self.stats = {
            'requests_processed': 0,
            'total_agents_invoked': 0,
            'average_response_time_ms': 0
        }
    
    async def evaluate_site_comprehensive(self, site: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive site evaluation using all agents.
        
        Workflow:
        1. Geographic Intelligence analyzes location
        2. Market Intelligence analyzes competition and demand
        3. Financial Analysis projects ROI
        4. Permit Management checks regulatory requirements
        5. Orchestrator synthesizes all results
        """
        workflow_id = f'WF-SITE-EVAL-{uuid.uuid4().hex[:8]}'
        start_time = datetime.now()
        
        logger.info(f"[Orchestrator] Starting comprehensive evaluation for site {site.get('site_id')}")
        
        # Emit workflow start
        event_simulator.emit_event(SystemEvent(
            event_type=EventType.USER_QUERY,
            source_system='UI',
            target_system=self.orchestrator_id,
            correlation_id=workflow_id,
            payload={'site_id': site.get('site_id'), 'action': 'comprehensive_evaluation'}
        ))
        
        event_simulator.emit_event(SystemEvent(
            event_type=EventType.QUERY_ROUTING,
            source_system='Unified_Gateway',
            target_system=self.orchestrator_id,
            correlation_id=workflow_id,
            payload={'routed_from': 'UI'}
        ))
        
        try:
            # Step 1: Geographic Intelligence Analysis
            logger.info(f"[Orchestrator] Step 1/5: Geographic analysis...")
            event_simulator.emit_event(SystemEvent(
                event_type=EventType.AGENT_INVOCATION,
                source_system=self.orchestrator_id,
                target_system='geographic-intelligence-001',
                correlation_id=workflow_id,
                payload={'step': 1, 'action': 'analyze_location'}
            ))
            
            location_analysis = await self.agents['geographic'].analyze_site_location(site)
            
            # Step 2: Market Intelligence Analysis (parallel with Step 3)
            logger.info(f"[Orchestrator] Step 2/5: Market analysis...")
            event_simulator.emit_event(SystemEvent(
                event_type=EventType.AGENT_INVOCATION,
                source_system=self.orchestrator_id,
                target_system='market-intelligence-001',
                correlation_id=workflow_id,
                payload={'step': 2, 'action': 'analyze_market'}
            ))
            
            # Step 3: Financial Analysis (parallel with Step 2)
            logger.info(f"[Orchestrator] Step 3/5: Financial analysis...")
            event_simulator.emit_event(SystemEvent(
                event_type=EventType.AGENT_INVOCATION,
                source_system=self.orchestrator_id,
                target_system='financial-analysis-001',
                correlation_id=workflow_id,
                payload={'step': 3, 'action': 'analyze_financials'}
            ))
            
            # Run market and financial analysis in parallel
            market_analysis, financial_analysis = await asyncio.gather(
                self.agents['market'].analyze_market(site, location_analysis),
                self.agents['financial'].analyze_financials(site, location_analysis)
            )
            
            # Step 4: Permit Management Analysis
            logger.info(f"[Orchestrator] Step 4/5: Permit analysis...")
            event_simulator.emit_event(SystemEvent(
                event_type=EventType.AGENT_INVOCATION,
                source_system=self.orchestrator_id,
                target_system='permit-management-001',
                correlation_id=workflow_id,
                payload={'step': 4, 'action': 'analyze_permits'}
            ))
            
            permit_analysis = await self.agents['permit'].analyze_permit_requirements(site)
            
            # Step 5: Synthesize results
            logger.info(f"[Orchestrator] Step 5/5: Synthesizing results...")
            event_simulator.emit_event(SystemEvent(
                event_type=EventType.RESPONSE_AGGREGATION,
                source_system=self.orchestrator_id,
                correlation_id=workflow_id,
                payload={'synthesizing': 'all agent results'}
            ))
            
            synthesis = self._synthesize_site_evaluation(
                site,
                location_analysis,
                market_analysis,
                financial_analysis,
                permit_analysis
            )
            
            # Calculate processing time
            end_time = datetime.now()
            processing_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Emit completion
            event_simulator.emit_event(SystemEvent(
                event_type=EventType.RESPONSE_DELIVERY,
                source_system=self.orchestrator_id,
                target_system='UI',
                correlation_id=workflow_id,
                payload={'recommendation': synthesis['recommendation'], 'score': synthesis['overall_score']},
                processing_time_ms=processing_time_ms
            ))
            
            # Update statistics
            self.stats['requests_processed'] += 1
            self.stats['total_agents_invoked'] += 4  # 4 agents used
            
            # Publish to message queue
            message_queue.publish(
                topic='site.evaluation.completed',
                payload=synthesis,
                sender=self.orchestrator_id,
                correlation_id=workflow_id
            )
            
            logger.info(f"[Orchestrator] Evaluation complete in {processing_time_ms}ms")
            
            return {
                'success': True,
                'workflow_id': workflow_id,
                'site_id': site.get('site_id'),
                'processing_time_ms': processing_time_ms,
                'agents_involved': ['geographic', 'market', 'financial', 'permit'],
                'synthesis': synthesis,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"[Orchestrator] Error in evaluation: {e}")
            event_simulator.emit_event(SystemEvent(
                event_type=EventType.SYSTEM_ERROR,
                source_system=self.orchestrator_id,
                correlation_id=workflow_id,
                payload={'error': str(e)}
            ))
            
            return {
                'success': False,
                'workflow_id': workflow_id,
                'error': str(e)
            }
    
    async def optimize_network_expansion(
        self,
        candidate_sites: List[Dict[str, Any]],
        budget: float,
        target_sites: int,
        objective: str = 'balanced'
    ) -> Dict[str, Any]:
        """
        Optimize network expansion across multiple sites.
        
        Workflow:
        1. Evaluate all candidate sites in parallel
        2. Network agent optimizes selection
        3. Return optimal configuration
        """
        workflow_id = f'WF-NETWORK-OPT-{uuid.uuid4().hex[:8]}'
        start_time = datetime.now()
        
        logger.info(f"[Orchestrator] Starting network optimization for {len(candidate_sites)} sites")
        
        event_simulator.emit_event(SystemEvent(
            event_type=EventType.OPTIMIZATION_REQUEST,
            source_system='UI',
            target_system=self.orchestrator_id,
            correlation_id=workflow_id,
            payload={
                'candidate_sites': len(candidate_sites),
                'budget': budget,
                'target_sites': target_sites
            }
        ))
        
        try:
            # Evaluate all sites (in batches for performance)
            logger.info(f"[Orchestrator] Evaluating {len(candidate_sites)} candidate sites...")
            
            evaluated_sites = []
            batch_size = 10
            
            for i in range(0, len(candidate_sites), batch_size):
                batch = candidate_sites[i:i+batch_size]
                
                # Evaluate batch in parallel
                batch_results = await asyncio.gather(
                    *[self.evaluate_site_comprehensive(site) for site in batch],
                    return_exceptions=True
                )
                
                for result in batch_results:
                    if isinstance(result, dict) and result.get('success'):
                        evaluated_sites.append(result['synthesis'])
            
            logger.info(f"[Orchestrator] Successfully evaluated {len(evaluated_sites)} sites")
            
            # Run network optimization
            event_simulator.emit_event(SystemEvent(
                event_type=EventType.AGENT_INVOCATION,
                source_system=self.orchestrator_id,
                target_system='network-optimization-001',
                correlation_id=workflow_id,
                payload={'optimizing': 'network configuration'}
            ))
            
            optimization_result = await self.agents['network'].optimize_network_selection(
                evaluated_sites,
                budget,
                target_sites,
                objective
            )
            
            # Calculate processing time
            end_time = datetime.now()
            processing_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            event_simulator.emit_event(SystemEvent(
                event_type=EventType.RESPONSE_DELIVERY,
                source_system=self.orchestrator_id,
                target_system='UI',
                correlation_id=workflow_id,
                payload={
                    'selected_sites': len(optimization_result['selected_sites']),
                    'total_investment': optimization_result['network_metrics']['total_capex']
                },
                processing_time_ms=processing_time_ms
            ))
            
            logger.info(f"[Orchestrator] Network optimization complete in {processing_time_ms}ms")
            
            return {
                'success': True,
                'workflow_id': workflow_id,
                'processing_time_ms': processing_time_ms,
                'optimization_result': optimization_result,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"[Orchestrator] Error in network optimization: {e}")
            return {
                'success': False,
                'workflow_id': workflow_id,
                'error': str(e)
            }
    
    async def handle_permit_crisis(
        self,
        sites: List[Dict[str, Any]],
        city: str
    ) -> Dict[str, Any]:
        """
        Handle permit crisis scenario across multiple sites.
        
        Workflow:
        1. Check permit status for all sites
        2. Identify bottlenecks
        3. Generate resolution plan
        """
        workflow_id = f'WF-PERMIT-CRISIS-{uuid.uuid4().hex[:8]}'
        start_time = datetime.now()
        
        logger.info(f"[Orchestrator] Handling permit crisis for {len(sites)} sites in {city}")
        
        event_simulator.emit_event(SystemEvent(
            event_type=EventType.CRISIS_ALERT,
            source_system='Permit_Monitoring',
            target_system=self.orchestrator_id,
            correlation_id=workflow_id,
            payload={'city': city, 'affected_sites': len(sites)}
        ))
        
        try:
            # Check all permits in parallel
            permit_analyses = await asyncio.gather(
                *[self.agents['permit'].analyze_permit_requirements(site) for site in sites],
                return_exceptions=True
            )
            
            # Identify bottlenecks
            event_simulator.emit_event(SystemEvent(
                event_type=EventType.CRISIS_ASSESSMENT,
                source_system=self.orchestrator_id,
                correlation_id=workflow_id,
                payload={'analyzing': 'permit bottlenecks'}
            ))
            
            bottlenecks = self._identify_permit_bottlenecks(permit_analyses)
            
            # Generate resolution plan
            resolution_plan = self._generate_permit_resolution_plan(bottlenecks, city)
            
            event_simulator.emit_event(SystemEvent(
                event_type=EventType.CRISIS_RESOLUTION,
                source_system=self.orchestrator_id,
                target_system='UI',
                correlation_id=workflow_id,
                payload={'action_items': len(resolution_plan['action_items'])}
            ))
            
            processing_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            logger.info(f"[Orchestrator] Crisis resolution plan generated in {processing_time_ms}ms")
            
            return {
                'success': True,
                'workflow_id': workflow_id,
                'processing_time_ms': processing_time_ms,
                'bottlenecks': bottlenecks,
                'resolution_plan': resolution_plan,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"[Orchestrator] Error handling crisis: {e}")
            return {
                'success': False,
                'workflow_id': workflow_id,
                'error': str(e)
            }
    
    def _synthesize_site_evaluation(
        self,
        site: Dict,
        location: Dict,
        market: Dict,
        financial: Dict,
        permit: Dict
    ) -> Dict[str, Any]:
        """Synthesize results from all agents"""
        
        # Calculate overall score (weighted average)
        weights = {
            'location': 0.25,
            'market': 0.25,
            'financial': 0.30,
            'regulatory': 0.20
        }
        
        overall_score = (
            location['location_score'] * weights['location'] +
            market['market_score'] * weights['market'] +
            financial['financial_score'] * weights['financial'] +
            permit['regulatory_score'] * weights['regulatory']
        )
        
        # Determine recommendation
        if overall_score >= 80 and financial['npv'] > 5000000:
            recommendation = 'strong_select'
            priority = 'High'
        elif overall_score >= 65 and financial['npv'] > 2000000:
            recommendation = 'select'
            priority = 'Medium'
        elif overall_score >= 50:
            recommendation = 'consider'
            priority = 'Low'
        else:
            recommendation = 'reject'
            priority = 'None'
        
        # Compile key insights
        key_insights = []
        
        if location['location_score'] > 80:
            key_insights.append(f"Excellent location: {location['recommendation']}")
        
        if market['market_score'] > 75:
            key_insights.append(f"Strong market: {market['recommendation']}")
        
        if financial['npv'] > 5000000:
            key_insights.append(f"High ROI: NPV ₹{financial['npv']:,.0f}, IRR {financial['irr_percentage']:.1f}%")
        
        if permit['regulatory_score'] < 60:
            key_insights.append(f"Regulatory concern: {permit['timeline']['total_days']} days approval time")
        
        return {
            'site_id': site.get('site_id'),
            'city': site.get('city'),
            'overall_score': round(overall_score, 2),
            'recommendation': recommendation,
            'priority': priority,
            'scores': {
                'location': location['location_score'],
                'market': market['market_score'],
                'financial': financial['financial_score'],
                'regulatory': permit['regulatory_score']
            },
            'financials': {
                'capex': financial['capex']['total'],
                'npv': financial['npv'],
                'irr': financial['irr_percentage'],
                'payback_years': financial['payback_years']
            },
            'key_insights': key_insights,
            'detailed_analysis': {
                'location': location,
                'market': market,
                'financial': financial,
                'permit': permit
            }
        }
    
    def _identify_permit_bottlenecks(self, permit_analyses: List[Dict]) -> List[Dict]:
        """Identify permit processing bottlenecks"""
        
        bottlenecks = []
        
        for analysis in permit_analyses:
            if isinstance(analysis, Exception):
                continue
            
            timeline = analysis.get('timeline', {})
            
            if timeline.get('total_days', 0) > 120:
                bottlenecks.append({
                    'site_id': analysis.get('site_id'),
                    'issue': 'Extended timeline',
                    'days': timeline['total_days'],
                    'severity': 'High'
                })
        
        return bottlenecks
    
    def _generate_permit_resolution_plan(self, bottlenecks: List[Dict], city: str) -> Dict[str, Any]:
        """Generate resolution plan for permit bottlenecks"""
        
        action_items = [
            f"Escalate to {city} Municipal Corporation senior management",
            "Engage external permit consultants for expedited processing",
            "Utilize single-window clearance system where available",
            "Submit parallel applications to multiple agencies",
            "Schedule regular follow-up meetings with agency officials"
        ]
        
        return {
            'city': city,
            'action_items': action_items,
            'estimated_improvement_days': 30,
            'priority': 'High',
            'owner': 'Permit Management Team'
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        return {
            'orchestrator_id': self.orchestrator_id,
            'requests_processed': self.stats['requests_processed'],
            'total_agents_invoked': self.stats['total_agents_invoked'],
            'active_workflows': len(self.active_workflows),
            'available_agents': list(self.agents.keys()),
            'timestamp': datetime.now().isoformat()
        }


# Global orchestrator instance
ev_charging_orchestrator = EVChargingOrchestrator()
