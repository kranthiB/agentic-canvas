"""
Demo 1: Carbon Compass Agent
T3 Cognitive Autonomous Agent for emissions optimization
"""
import random
from typing import Dict, Any, List
from datetime import datetime
import logging

from app.agents.base_agent import BaseAgent
from app.models.demo1_models import ActionType, EmissionStatus

logger = logging.getLogger(__name__)


class CarbonOptimizationAgent(BaseAgent):
    """
    T3 Cognitive Autonomous Agent
    Capabilities: CG.RS, CG.DC, LA.RL, GS.MO
    """
    
    def __init__(self):
        super().__init__(
            agent_id='carbon-optimizer-001',
            agent_type='T3-Cognitive',
            capabilities=['CG.RS', 'CG.DC', 'LA.RL', 'GS.MO', 'AE.TX']
        )
        
        # Q-learning parameters (simplified)
        self.q_table = {}  # State-action Q values
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.epsilon = 0.1  # Exploration rate
        
        self.confidence = 0.85
    
    def perceive(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """
        PK.OB - Environmental Sensing
        Process emissions data
        """
        emissions_rate = environment.get('emissions_rate_kg_hr', 250)
        production_rate = environment.get('production_rate', 950)
        budget_remaining = environment.get('budget_remaining_mt', 50)
        
        # Calculate state features
        intensity = emissions_rate / production_rate if production_rate > 0 else 0
        budget_consumption_rate = (emissions_rate / 1_000_000) * 8760  # Mt/year
        days_until_budget_exceeded = (budget_remaining / budget_consumption_rate) * 365 if budget_consumption_rate > 0 else 365
        
        perception = {
            'emissions_rate': emissions_rate,
            'production_rate': production_rate,
            'intensity': intensity,
            'budget_remaining': budget_remaining,
            'days_until_budget_exceeded': days_until_budget_exceeded,
            'status': self._assess_status(emissions_rate, budget_remaining)
        }
        
        logger.info(f"Perceived emissions: {emissions_rate} kg/hr, intensity: {intensity:.4f}")
        
        return perception
    
    def reason(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """
        CG.RS - Reasoning
        CG.DC - Decision Making
        LA.RL - Reinforcement Learning
        """
        emissions_rate = perception['emissions_rate']
        intensity = perception['intensity']
        days_remaining = perception['days_until_budget_exceeded']
        
        # Determine action using Q-learning with exploration
        if random.random() < self.epsilon:
            # Explore: random action
            action_type = random.choice(list(ActionType))
        else:
            # Exploit: best known action
            action_type = self._get_best_action(perception)
        
        # Calculate expected impact
        expected_reduction, cost, reasoning = self._calculate_action_impact(
            action_type, emissions_rate, intensity
        )
        
        decision = {
            'action_type': action_type,
            'expected_reduction_kg_hr': expected_reduction,
            'expected_cost': cost,
            'reasoning': reasoning,
            'confidence_score': self.confidence,
            'priority': self._calculate_priority(days_remaining),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Decision: {action_type.value}, expected reduction: {expected_reduction} kg/hr")
        
        return decision
    
    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        AE.TX - Task Execution
        Generate action recommendation
        """
        action_type = decision['action_type']
        
        # Generate detailed action description
        description = self._generate_action_description(action_type, decision)
        
        result = {
            'action_type': action_type.value,
            'description': description,
            'expected_reduction_kg_hr': decision['expected_reduction_kg_hr'],
            'expected_cost': decision['expected_cost'],
            'reasoning': decision['reasoning'],
            'confidence_score': decision['confidence_score'],
            'priority': decision['priority'],
            'implemented': False
        }
        
        return result
    
    def _assess_status(self, emissions_rate: float, budget_remaining: float) -> str:
        """Assess current emissions status"""
        if budget_remaining < 10:
            return EmissionStatus.CRITICAL.value
        elif emissions_rate > 350:
            return EmissionStatus.WARNING.value
        else:
            return EmissionStatus.NORMAL.value
    
    def _get_best_action(self, perception: Dict[str, Any]) -> ActionType:
        """Get best action from Q-table"""
        state = self._discretize_state(perception)
        
        if state not in self.q_table:
            # Initialize Q-values for new state
            self.q_table[state] = {action: 0.0 for action in ActionType}
        
        # Return action with highest Q-value
        return max(self.q_table[state], key=self.q_table[state].get)
    
    def _discretize_state(self, perception: Dict[str, Any]) -> str:
        """Convert continuous state to discrete state for Q-learning"""
        emissions = perception['emissions_rate']
        intensity = perception['intensity']
        
        # Discretize into bins
        if emissions < 200:
            e_bin = 'low'
        elif emissions < 300:
            e_bin = 'medium'
        else:
            e_bin = 'high'
        
        if intensity < 0.2:
            i_bin = 'low'
        elif intensity < 0.3:
            i_bin = 'medium'
        else:
            i_bin = 'high'
        
        return f"{e_bin}_{i_bin}"
    
    def _calculate_action_impact(self, action_type: ActionType, 
                                 emissions_rate: float, intensity: float) -> tuple:
        """Calculate expected impact of action"""
        
        if action_type == ActionType.REDUCE_RATE:
            reduction = emissions_rate * 0.15  # 15% reduction
            cost = 50000
            reasoning = "Reduce production rate temporarily to lower emissions while maintaining critical operations"
            
        elif action_type == ActionType.OPTIMIZE_PROCESS:
            reduction = emissions_rate * 0.08  # 8% reduction
            cost = 30000
            reasoning = "Optimize furnace temperatures and combustion efficiency to reduce fuel consumption"
            
        elif action_type == ActionType.SWITCH_FUEL:
            reduction = emissions_rate * 0.25  # 25% reduction
            cost = 150000
            reasoning = "Switch from coal to natural gas in select units to significantly reduce carbon intensity"
            
        elif action_type == ActionType.SCHEDULE_MAINTENANCE:
            reduction = emissions_rate * 0.05  # 5% reduction
            cost = 80000
            reasoning = "Schedule preventive maintenance to improve equipment efficiency and reduce emissions"
            
        else:  # NO_ACTION
            reduction = 0
            cost = 0
            reasoning = "Current emissions within acceptable range, continue monitoring"
        
        return reduction, cost, reasoning
    
    def _generate_action_description(self, action_type: ActionType, decision: Dict) -> str:
        """Generate detailed action description"""
        
        descriptions = {
            ActionType.REDUCE_RATE: f"Temporarily reduce production rate by 10-15% to lower emissions by {decision['expected_reduction_kg_hr']:.1f} kg/hr. Estimated production impact: -100 barrels/day. Coordinate with operations team for implementation during next shift.",
            
            ActionType.OPTIMIZE_PROCESS: f"Optimize combustion parameters across FCC and CDU units. Expected emissions reduction: {decision['expected_reduction_kg_hr']:.1f} kg/hr through improved fuel efficiency. No production impact expected.",
            
            ActionType.SWITCH_FUEL: f"Switch fuel source from coal to natural gas in Boiler #3 and Furnace #7. Significant emissions reduction: {decision['expected_reduction_kg_hr']:.1f} kg/hr. Requires 48-hour notice for fuel logistics.",
            
            ActionType.SCHEDULE_MAINTENANCE: f"Schedule comprehensive maintenance for heat recovery systems. Improve thermal efficiency by 3-5%, reducing emissions by {decision['expected_reduction_kg_hr']:.1f} kg/hr. Plan 72-hour maintenance window.",
            
            ActionType.NO_ACTION: "Current emissions within optimal range. Continue real-time monitoring and maintain current operational parameters."
        }
        
        return descriptions.get(action_type, "Action details pending")
    
    def _calculate_priority(self, days_until_budget_exceeded: float) -> int:
        """Calculate action priority (1=highest, 5=lowest)"""
        if days_until_budget_exceeded < 30:
            return 1  # Critical
        elif days_until_budget_exceeded < 90:
            return 2  # High
        elif days_until_budget_exceeded < 180:
            return 3  # Medium
        else:
            return 4  # Low
    
    def update_q_value(self, state: str, action: ActionType, reward: float, next_state: str):
        """
        LA.RL - Reinforcement Learning
        Update Q-value based on reward
        """
        if state not in self.q_table:
            self.q_table[state] = {a: 0.0 for a in ActionType}
        if next_state not in self.q_table:
            self.q_table[next_state] = {a: 0.0 for a in ActionType}
        
        # Q-learning update
        current_q = self.q_table[state][action]
        max_next_q = max(self.q_table[next_state].values())
        
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )
        
        self.q_table[state][action] = new_q
    
    def generate_counterfactual(self, scenario_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        CG.PS - Problem Solving
        Generate counterfactual scenario analysis
        """
        baseline_emissions = scenario_params.get('baseline_emissions_mt', 100)
        actions = scenario_params.get('actions', [])
        
        # Calculate projected impact
        total_reduction = 0
        total_cost = 0
        
        for action in actions:
            reduction_pct = {
                'reduce_rate': 0.15,
                'optimize_process': 0.08,
                'switch_fuel': 0.25,
                'schedule_maintenance': 0.05
            }.get(action, 0)
            
            total_reduction += baseline_emissions * reduction_pct
        
        projected_emissions = baseline_emissions - total_reduction
        
        return {
            'scenario_name': scenario_params.get('name', 'Counterfactual Scenario'),
            'baseline_emissions_mt': baseline_emissions,
            'projected_emissions_mt': projected_emissions,
            'projected_savings_mt': total_reduction,
            'actions_count': len(actions),
            'feasibility_score': random.uniform(0.7, 0.95),
            'risk_level': 'medium' if len(actions) > 2 else 'low'
        }
    
    def explain(self, decision: Dict[str, Any]) -> str:
        """
        GS.EX - Explainability
        Provide human-readable explanation
        """
        action = decision.get('action_type', 'NO_ACTION')
        reduction = decision.get('expected_reduction_kg_hr', 0)
        
        explanation = f"""
        **Carbon Optimization Decision**
        
        Action Recommended: {action.value if hasattr(action, 'value') else action}
        
        Reasoning: {decision.get('reasoning', 'Standard optimization protocol')}
        
        Expected Impact: {reduction:.1f} kg/hr reduction in emissions
        
        This recommendation is based on:
        - Current emissions rate analysis
        - Carbon budget trajectory
        - Historical performance of similar actions
        - Real-time reinforcement learning optimization
        
        Confidence: {decision.get('confidence_score', 0.85) * 100:.0f}%
        Priority: {decision.get('priority', 3)}/5
        """
        
        return explanation.strip()