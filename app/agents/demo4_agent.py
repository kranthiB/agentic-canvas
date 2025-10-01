"""
Demo 4: Mobility Maestro Agent
T3 Cognitive Autonomous Agent for EV charging network optimization
"""
import random
from typing import Dict, Any, List
from datetime import datetime
import logging

from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class NetworkOptimizationAgent(BaseAgent):
    """
    T3 Cognitive Autonomous Agent
    Capabilities: CG.PS, CG.DC, AE.TL, LA.SL
    """
    
    def __init__(self):
        super().__init__(
            agent_id='network-optimizer-001',
            agent_type='T3-Cognitive',
            capabilities=['CG.PS', 'CG.DC', 'AE.TL', 'LA.SL']
        )
        self.confidence = 0.91
    
    def perceive(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """
        PK.OB - Environmental Sensing
        Analyze site characteristics
        """
        site = environment.get('site', {})
        
        perception = {
            'site_id': site.get('site_id'),
            'city': site.get('city'),
            'city_tier': site.get('city_tier'),
            'location': {
                'latitude': site.get('latitude'),
                'longitude': site.get('longitude')
            },
            'characteristics': {
                'daily_traffic': site.get('daily_traffic_count', 5000),
                'population_density': site.get('population_density', 2000),
                'avg_income': site.get('avg_household_income', 800000),
                'ev_penetration': site.get('ev_penetration_rate', 2.5),
                'existing_chargers': site.get('existing_chargers_within_5km', 0)
            },
            'infrastructure': {
                'grid_available': site.get('grid_connection_available', True),
                'grid_capacity_kw': site.get('grid_capacity_kw', 500)
            }
        }
        
        return perception
    
    def reason(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """
        CG.PS - Problem Solving
        CG.DC - Decision Making
        Evaluate site suitability
        """
        char = perception['characteristics']
        infra = perception['infrastructure']
        
        # Multi-criteria evaluation
        traffic_score = min(100, (char['daily_traffic'] / 10000) * 100)
        demographics_score = self._evaluate_demographics(char)
        grid_score = 100 if infra['grid_available'] else 50
        competition_score = max(0, 100 - (char['existing_chargers'] * 15))
        accessibility_score = random.uniform(70, 95)  # Simplified
        
        # Weighted overall score
        weights = {
            'traffic': 0.30,
            'demographics': 0.25,
            'grid': 0.20,
            'competition': 0.15,
            'accessibility': 0.10
        }
        
        overall_score = (
            traffic_score * weights['traffic'] +
            demographics_score * weights['demographics'] +
            grid_score * weights['grid'] +
            competition_score * weights['competition'] +
            accessibility_score * weights['accessibility']
        )
        
        # Financial projections
        financials = self._project_financials(perception, overall_score)
        
        # Recommendation
        if overall_score >= 80 and financials['npv_inr'] > 5000000:
            recommendation = 'strong_select'
        elif overall_score >= 65 and financials['npv_inr'] > 2000000:
            recommendation = 'select'
        elif overall_score >= 50:
            recommendation = 'consider'
        else:
            recommendation = 'reject'
        
        decision = {
            'scores': {
                'traffic': round(traffic_score, 1),
                'demographics': round(demographics_score, 1),
                'grid_infrastructure': round(grid_score, 1),
                'competition': round(competition_score, 1),
                'accessibility': round(accessibility_score, 1),
                'overall': round(overall_score, 1)
            },
            'financials': financials,
            'recommendation': recommendation,
            'confidence': self.confidence,
            'reasoning': self._generate_reasoning(perception, overall_score, recommendation)
        }
        
        return decision
    
    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        AE.TL - Tool Lifecycle Management
        Generate evaluation report
        """
        result = {
            'evaluation': decision,
            'risk_factors': self._identify_risks(decision),
            'opportunities': self._identify_opportunities(decision),
            'next_steps': self._recommend_next_steps(decision['recommendation'])
        }
        
        return result
    
    def _evaluate_demographics(self, characteristics: Dict) -> float:
        """Evaluate demographic suitability"""
        income = characteristics['avg_income']
        ev_penetration = characteristics['ev_penetration']
        population = characteristics['population_density']
        
        # Income score (normalized)
        income_score = min(100, (income / 1500000) * 100)
        
        # EV adoption score
        adoption_score = min(100, (ev_penetration / 5) * 100)
        
        # Population score
        pop_score = min(100, (population / 5000) * 100)
        
        # Weighted average
        demo_score = (income_score * 0.4 + adoption_score * 0.4 + pop_score * 0.2)
        
        return demo_score
    
    def _project_financials(self, perception: Dict, overall_score: float) -> Dict:
        """Project financial performance"""
        char = perception['characteristics']
        
        # Estimate sessions per day
        daily_sessions = char['daily_traffic'] * (char['ev_penetration'] / 100) * 0.15
        
        # CAPEX (Capital Expenditure)
        capex = random.uniform(2500000, 3500000)  # INR
        
        # OPEX (Operating Expenditure) - annual
        opex_annual = random.uniform(400000, 600000)  # INR
        
        # Revenue projections
        avg_revenue_per_session = 250  # INR
        revenue_year1 = daily_sessions * 365 * avg_revenue_per_session * 0.7  # 70% utilization Y1
        revenue_year5 = daily_sessions * 365 * avg_revenue_per_session * 1.2  # 120% growth by Y5
        
        # NPV calculation (simplified)
        discount_rate = 0.12
        years = 7
        cash_flows = []
        for year in range(1, years + 1):
            revenue = revenue_year1 * (1 + (year - 1) * 0.08)  # 8% annual growth
            cash_flow = revenue - opex_annual
            discounted_cf = cash_flow / ((1 + discount_rate) ** year)
            cash_flows.append(discounted_cf)
        
        npv = sum(cash_flows) - capex
        
        # IRR (simplified approximation)
        irr = ((sum(cash_flows) / capex) ** (1 / years) - 1) * 100
        
        # Payback period
        cumulative_cf = 0
        payback_years = 0
        for year, cf in enumerate(cash_flows, 1):
            cumulative_cf += cf + opex_annual
            if cumulative_cf >= capex:
                payback_years = year
                break
        if payback_years == 0:
            payback_years = 10  # Beyond horizon
        
        return {
            'capex_inr': round(capex, 0),
            'opex_annual_inr': round(opex_annual, 0),
            'revenue_year1_inr': round(revenue_year1, 0),
            'revenue_year5_inr': round(revenue_year5, 0),
            'npv_inr': round(npv, 0),
            'irr_percentage': round(irr, 2),
            'payback_years': round(payback_years, 1),
            'estimated_daily_sessions': round(daily_sessions, 0)
        }
    
    def _generate_reasoning(self, perception: Dict, overall_score: float, recommendation: str) -> str:
        """Generate reasoning for decision"""
        city = perception['city']
        tier = perception['city_tier']
        
        if recommendation == 'strong_select':
            return f"Excellent site in {city} ({tier}). High traffic, favorable demographics, strong financial projections. Priority for network expansion."
        elif recommendation == 'select':
            return f"Good site opportunity in {city} ({tier}). Solid fundamentals with positive ROI. Recommended for inclusion in network."
        elif recommendation == 'consider':
            return f"Marginal site in {city} ({tier}). Mixed indicators. Consider if strategic location or future growth expected."
        else:
            return f"Not recommended for {city} ({tier}). Low scores across key metrics or poor financial outlook."
    
    def _identify_risks(self, decision: Dict) -> List[str]:
        """Identify risk factors"""
        risks = []
        scores = decision['scores']
        financials = decision['financials']
        
        if scores['competition'] < 60:
            risks.append("High competition - existing chargers nearby may limit utilization")
        
        if scores['grid_infrastructure'] < 80:
            risks.append("Grid infrastructure concerns - may require expensive upgrades")
        
        if financials['payback_years'] > 5:
            risks.append("Long payback period - higher investment risk")
        
        if scores['demographics'] < 60:
            risks.append("Demographics below optimal - EV adoption may be slower than projected")
        
        if not risks:
            risks.append("Low risk profile - strong fundamentals across all metrics")
        
        return risks
    
    def _identify_opportunities(self, decision: Dict) -> List[str]:
        """Identify opportunities"""
        opportunities = []
        scores = decision['scores']
        
        if scores['traffic'] > 80:
            opportunities.append("High traffic location - potential for premium pricing during peak hours")
        
        if scores['demographics'] > 75:
            opportunities.append("Strong demographics - opportunity for value-added services (café, retail)")
        
        if scores['competition'] > 80:
            opportunities.append("Low competition - first-mover advantage in area")
        
        opportunities.append("Strategic positioning for future network expansion in region")
        
        return opportunities
    
    def _recommend_next_steps(self, recommendation: str) -> List[str]:
        """Recommend next steps"""
        if recommendation == 'strong_select':
            return [
                "Initiate land acquisition or lease negotiations",
                "Begin grid connection application process",
                "Conduct detailed site survey and engineering assessment",
                "Include in next quarterly network deployment plan"
            ]
        elif recommendation == 'select':
            return [
                "Schedule site visit and detailed evaluation",
                "Assess grid connection costs and timeline",
                "Validate traffic and demographic assumptions",
                "Include in candidate list for optimization analysis"
            ]
        elif recommendation == 'consider':
            return [
                "Monitor local EV adoption trends",
                "Re-evaluate if nearby sites unavailable",
                "Consider for Phase 2 expansion",
                "Track competitive developments in area"
            ]
        else:
            return [
                "Remove from active consideration",
                "Document reasoning for future reference",
                "Focus resources on higher-priority sites"
            ]
    
    def optimize_network(self, candidate_sites: List[Dict], 
                        budget_inr: float, target_sites: int) -> Dict[str, Any]:
        """
        Optimize network configuration using OR-Tools
        Simplified version for demo
        """
        # Evaluate all sites
        evaluated_sites = []
        for site in candidate_sites:
            perception = self.perceive({'site': site})
            decision = self.reason(perception)
            
            evaluated_sites.append({
                'site_id': site.get('site_id'),
                'overall_score': decision['scores']['overall'],
                'npv': decision['financials']['npv_inr'],
                'capex': decision['financials']['capex_inr'],
                'recommendation': decision['recommendation']
            })
        
        # Sort by score and NPV
        evaluated_sites.sort(key=lambda x: (x['overall_score'], x['npv']), reverse=True)
        
        # Select sites within budget
        selected_sites = []
        total_capex = 0
        
        for site in evaluated_sites:
            if len(selected_sites) >= target_sites:
                break
            if total_capex + site['capex'] <= budget_inr:
                selected_sites.append(site['site_id'])
                total_capex += site['capex']
        
        # Calculate network metrics
        total_revenue = sum(
            s['npv'] for s in evaluated_sites if s['site_id'] in selected_sites
        )
        
        return {
            'selected_site_ids': selected_sites,
            'total_capex_inr': total_capex,
            'network_npv_inr': total_revenue,
            'sites_selected': len(selected_sites),
            'optimization_time_ms': random.randint(100, 500)
        }