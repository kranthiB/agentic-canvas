"""
Demo 2: GridMind AI Multi-Agent System
T4 Multi-Agent Generative System for Khavda renewable energy plant
5 specialized agents with coordination protocols
"""
import random
import math
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging

from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


# Agent 1: Weather Forecasting Agent
class WeatherForecastAgent(BaseAgent):
    """Predicts solar irradiance and wind speeds"""
    
    def __init__(self):
        super().__init__(
            agent_id='weather-agent-001',
            agent_type='T3-Cognitive',
            capabilities=['PK.OB', 'CG.PS', 'LA.SL']
        )
        self.confidence = 0.88
    
    def perceive(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """Sense weather data"""
        current_hour = datetime.now().hour
        current_temp = environment.get('temperature_c', 35)
        
        return {
            'current_hour': current_hour,
            'temperature_c': current_temp,
            'cloud_cover': random.uniform(0, 0.3),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def reason(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """Forecast weather patterns"""
        hour = perception['current_hour']
        
        # Solar irradiance forecast (W/m²)
        solar_factor = max(0, math.sin((hour - 6) * math.pi / 12))
        base_irradiance = 1000 * solar_factor
        cloud_factor = 1 - perception['cloud_cover']
        forecasted_irradiance = base_irradiance * cloud_factor
        
        # Wind speed forecast (m/s)
        forecasted_wind = 8 + random.gauss(0, 2)
        
        # 24-hour forecast
        forecast_24h = []
        for h in range(24):
            future_hour = (hour + h) % 24
            solar_f = max(0, math.sin((future_hour - 6) * math.pi / 12))
            forecast_24h.append({
                'hour': future_hour,
                'solar_irradiance': 1000 * solar_f * random.uniform(0.8, 1.0),
                'wind_speed': 8 + random.gauss(0, 2)
            })
        
        return {
            'current': {
                'solar_irradiance': forecasted_irradiance,
                'wind_speed': forecasted_wind
            },
            'forecast_24h': forecast_24h,
            'confidence': self.confidence
        }
    
    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Broadcast weather forecast"""
        return {
            'agent_id': self.agent_id,
            'forecast': decision,
            'message_type': 'weather_update'
        }


# Agent 2: Demand Prediction Agent
class DemandPredictionAgent(BaseAgent):
    """Forecasts grid demand patterns"""
    
    def __init__(self):
        super().__init__(
            agent_id='demand-agent-001',
            agent_type='T3-Cognitive',
            capabilities=['LA.SL', 'CG.RS', 'PK.KB']
        )
        self.confidence = 0.90
    
    def perceive(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """Sense current demand"""
        current_hour = datetime.now().hour
        day_of_week = datetime.now().weekday()
        
        return {
            'current_hour': current_hour,
            'day_of_week': day_of_week,
            'current_demand_mw': environment.get('grid_demand_mw', 25000)
        }
    
    def reason(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """Forecast demand"""
        hour = perception['current_hour']
        is_weekend = perception['day_of_week'] >= 5
        
        # Base demand pattern
        if 8 <= hour <= 10 or 18 <= hour <= 22:
            base_demand = 28000  # Peak hours
        elif 0 <= hour <= 6:
            base_demand = 18000  # Night
        else:
            base_demand = 24000  # Normal
        
        # Weekend adjustment
        if is_weekend:
            base_demand *= 0.85
        
        # Add variability
        forecasted_demand = base_demand + random.gauss(0, 1500)
        
        # 24-hour forecast
        forecast_24h = []
        for h in range(24):
            future_hour = (hour + h) % 24
            if 8 <= future_hour <= 10 or 18 <= future_hour <= 22:
                demand = 28000
            elif 0 <= future_hour <= 6:
                demand = 18000
            else:
                demand = 24000
            
            forecast_24h.append({
                'hour': future_hour,
                'demand_mw': demand + random.gauss(0, 1000)
            })
        
        return {
            'current_demand_mw': forecasted_demand,
            'forecast_24h': forecast_24h,
            'peak_demand_expected': max(f['demand_mw'] for f in forecast_24h),
            'confidence': self.confidence
        }
    
    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Broadcast demand forecast"""
        return {
            'agent_id': self.agent_id,
            'forecast': decision,
            'message_type': 'demand_update'
        }


# Agent 3: Storage Optimization Agent
class StorageOptimizationAgent(BaseAgent):
    """Manages battery charging/discharging"""
    
    def __init__(self):
        super().__init__(
            agent_id='storage-agent-001',
            agent_type='T3-Cognitive',
            capabilities=['CG.DC', 'AE.TX', 'LA.RL']
        )
        self.confidence = 0.92
    
    def perceive(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """Sense battery and generation state"""
        return {
            'battery_soc': environment.get('battery_soc', 0.65),
            'generation_mw': environment.get('total_generation_mw', 27000),
            'demand_mw': environment.get('grid_demand_mw', 25000),
            'market_price': environment.get('market_price', 3200),
            'grid_frequency': environment.get('grid_frequency', 50.0)
        }
    
    def reason(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """Decide charging/discharging strategy"""
        soc = perception['battery_soc']
        generation = perception['generation_mw']
        demand = perception['demand_mw']
        price = perception['market_price']
        frequency = perception['grid_frequency']
        
        # Decision logic
        surplus = generation - demand
        
        if frequency < 49.9:
            # Grid frequency low - discharge to support
            action = 'discharge'
            power_mw = min(2000, (1 - soc) * 5000)
            reasoning = "Grid frequency low, providing frequency support"
            
        elif frequency > 50.1:
            # Grid frequency high - charge to absorb
            action = 'charge'
            power_mw = min(2000, soc * 5000)
            reasoning = "Grid frequency high, absorbing excess power"
            
        elif surplus > 2000 and soc < 0.9 and price < 3000:
            # Excess generation, low price - charge
            action = 'charge'
            power_mw = min(surplus * 0.8, (0.9 - soc) * 5000)
            reasoning = "Storing excess renewable energy during low-price period"
            
        elif surplus < -2000 and soc > 0.3 and price > 3500:
            # Deficit, high price - discharge
            action = 'discharge'
            power_mw = min(abs(surplus) * 0.8, (soc - 0.2) * 5000)
            reasoning = "Supplying stored energy during high-demand, high-price period"
            
        else:
            action = 'hold'
            power_mw = 0
            reasoning = "Maintaining current state, conditions optimal"
        
        return {
            'action': action,
            'power_mw': power_mw,
            'reasoning': reasoning,
            'new_soc_estimate': soc + (power_mw / 5000) if action == 'charge' else soc - (power_mw / 5000),
            'confidence': self.confidence
        }
    
    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Execute storage action"""
        return {
            'agent_id': self.agent_id,
            'action': decision['action'],
            'power_mw': decision['power_mw'],
            'reasoning': decision['reasoning'],
            'message_type': 'storage_command'
        }


# Agent 4: Trading Agent
class MarketTradingAgent(BaseAgent):
    """Participates in real-time electricity markets"""
    
    def __init__(self):
        super().__init__(
            agent_id='trading-agent-001',
            agent_type='T3-Cognitive',
            capabilities=['CG.RS', 'AE.TL', 'LA.RL']
        )
        self.confidence = 0.87
    
    def perceive(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """Sense market conditions"""
        return {
            'current_price': environment.get('market_price', 3200),
            'available_capacity_mw': environment.get('available_capacity', 5000),
            'battery_soc': environment.get('battery_soc', 0.65)
        }
    
    def reason(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """Make trading decision"""
        price = perception['current_price']
        capacity = perception['available_capacity_mw']
        
        # Price forecast (simplified)
        price_trend = 'up' if random.random() > 0.5 else 'down'
        
        # Trading strategy
        if price > 3800:
            # High price - sell maximum
            action = 'sell'
            volume_mw = capacity * 0.9
            reasoning = "High market price, maximizing revenue by selling available capacity"
            
        elif price < 2800:
            # Low price - reduce sales, store
            action = 'hold'
            volume_mw = capacity * 0.3
            reasoning = "Low market price, reducing sales and storing for higher prices"
            
        else:
            # Normal price - standard trading
            action = 'sell'
            volume_mw = capacity * 0.7
            reasoning = "Normal market conditions, standard trading volume"
        
        expected_revenue = volume_mw * price
        
        return {
            'action': action,
            'volume_mw': volume_mw,
            'price_inr_mwh': price,
            'expected_revenue': expected_revenue,
            'price_trend': price_trend,
            'reasoning': reasoning,
            'confidence': self.confidence
        }
    
    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Execute trade"""
        return {
            'agent_id': self.agent_id,
            'trade': decision,
            'message_type': 'trade_execution'
        }


# Agent 5: Maintenance Coordinator Agent
class MaintenanceCoordinatorAgent(BaseAgent):
    """Schedules predictive maintenance"""
    
    def __init__(self):
        super().__init__(
            agent_id='maintenance-agent-001',
            agent_type='T2-Procedural',
            capabilities=['LA.MM', 'IC.CL', 'CG.PS']
        )
        self.confidence = 0.93
        
        # Asset health tracking
        self.asset_health = {
            'solar': 0.95,
            'wind': 0.92,
            'battery': 0.88
        }
    
    def perceive(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """Sense asset conditions"""
        # Simulate health degradation
        self.asset_health['solar'] = max(0.7, self.asset_health['solar'] - random.uniform(0, 0.002))
        self.asset_health['wind'] = max(0.7, self.asset_health['wind'] - random.uniform(0, 0.003))
        self.asset_health['battery'] = max(0.6, self.asset_health['battery'] - random.uniform(0, 0.001))
        
        return {
            'asset_health': self.asset_health.copy(),
            'demand_forecast': environment.get('demand_forecast', [])
        }
    
    def reason(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """Assess maintenance needs"""
        health = perception['asset_health']
        recommendations = []
        urgency = 'none'
        
        # Solar maintenance
        if health['solar'] < 0.85:
            recommendations.append({
                'asset': 'solar_arrays',
                'issue': 'Panel efficiency degradation detected',
                'action': 'Schedule cleaning and inspection',
                'urgency': 'medium',
                'estimated_downtime_hours': 4,
                'cost_estimate_inr': 50000
            })
            urgency = 'medium'
        
        # Wind maintenance
        if health['wind'] < 0.88:
            recommendations.append({
                'asset': 'wind_turbines',
                'issue': 'Gearbox vibration anomaly',
                'action': 'Perform vibration analysis',
                'urgency': 'high' if health['wind'] < 0.80 else 'medium',
                'estimated_downtime_hours': 8,
                'cost_estimate_inr': 120000
            })
            if health['wind'] < 0.80:
                urgency = 'high'
        
        # Battery maintenance
        if health['battery'] < 0.82:
            recommendations.append({
                'asset': 'battery_storage',
                'issue': f"Battery capacity degraded to {health['battery']*100:.0f}%",
                'action': 'Module replacement required',
                'urgency': 'high',
                'estimated_downtime_hours': 12,
                'cost_estimate_inr': 800000
            })
            urgency = 'high'
        
        # Find optimal maintenance window
        optimal_window = "Weekend (low demand period)"
        
        return {
            'recommendations': recommendations,
            'overall_urgency': urgency,
            'optimal_window': optimal_window,
            'asset_health': health,
            'confidence': self.confidence
        }
    
    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule maintenance"""
        return {
            'agent_id': self.agent_id,
            'maintenance_plan': decision,
            'message_type': 'maintenance_schedule'
        }


# Multi-Agent Coordinator
class MultiAgentCoordinator:
    """
    IC.DS - Distributed Coordination
    IC.CF - Conflict Resolution
    IC.CS - Consensus Protocols
    """
    
    def __init__(self):
        self.weather_agent = WeatherForecastAgent()
        self.demand_agent = DemandPredictionAgent()
        self.storage_agent = StorageOptimizationAgent()
        self.trading_agent = MarketTradingAgent()
        self.maintenance_agent = MaintenanceCoordinatorAgent()
        
        logger.info("Multi-agent system initialized with 5 agents")
    
    def run_coordination_round(self, plant_state: Dict[str, Any]) -> Dict[str, Any]:
        """Run coordination round with all agents"""
        
        # Collect proposals from all agents
        proposals = []
        
        # Weather agent
        weather_pred = self.weather_agent.run_cycle(plant_state)
        proposals.append({
            'agent_id': self.weather_agent.agent_id,
            'agent_type': 'weather',
            'proposal': weather_pred,
            'confidence': self.weather_agent.confidence
        })
        
        # Demand agent
        demand_pred = self.demand_agent.run_cycle(plant_state)
        proposals.append({
            'agent_id': self.demand_agent.agent_id,
            'agent_type': 'demand',
            'proposal': demand_pred,
            'confidence': self.demand_agent.confidence
        })
        
        # Storage agent
        storage_decision = self.storage_agent.run_cycle(plant_state)
        proposals.append({
            'agent_id': self.storage_agent.agent_id,
            'agent_type': 'storage',
            'proposal': storage_decision,
            'confidence': self.storage_agent.confidence
        })
        
        # Trading agent
        trading_decision = self.trading_agent.run_cycle(plant_state)
        proposals.append({
            'agent_id': self.trading_agent.agent_id,
            'agent_type': 'trading',
            'proposal': trading_decision,
            'confidence': self.trading_agent.confidence
        })
        
        # Maintenance agent
        maintenance_assessment = self.maintenance_agent.run_cycle(plant_state)
        proposals.append({
            'agent_id': self.maintenance_agent.agent_id,
            'agent_type': 'maintenance',
            'proposal': maintenance_assessment,
            'confidence': self.maintenance_agent.confidence
        })
        
        # Consensus protocol (simplified)
        consensus = self._reach_consensus(proposals)
        
        return {
            'proposals': proposals,
            'consensus': consensus,
            'coordination_time_ms': random.randint(50, 150),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _reach_consensus(self, proposals: List[Dict]) -> Dict[str, Any]:
        """Simplified consensus protocol"""
        
        # Weight proposals by confidence
        weighted_sum = sum(p['confidence'] for p in proposals)
        avg_confidence = weighted_sum / len(proposals)
        
        consensus_reached = avg_confidence > 0.85
        
        return {
            'consensus_reached': consensus_reached,
            'avg_confidence': avg_confidence,
            'participating_agents': len(proposals),
            'decision': 'proceed' if consensus_reached else 'review'
        }