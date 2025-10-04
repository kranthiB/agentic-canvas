"""
Specialized Agents for EV Charging Network Optimization
Five expert agents working together
"""
import asyncio
import random
from typing import Dict, List, Any, Optional
from datetime import datetime, date

from .mock_systems import (
    mock_vahan, mock_census, mock_traffic, mock_competitor,
    mock_financial, get_municipal_portal, get_grid_monitoring
)
from .event_simulator import SystemEvent, EventType, event_simulator


class GeographicIntelligenceAgent:
    """
    Analyzes geographic suitability of charging station sites.
    
    Responsibilities:
    - Location scoring based on demographics
    - Traffic pattern analysis
    - Proximity to key infrastructure
    - Spatial clustering analysis
    """
    
    def __init__(self):
        self.agent_id = "geographic-intelligence-001"
        self.capabilities = ['location_analysis', 'traffic_analysis', 'demographic_scoring']
    
    async def analyze_site_location(self, site: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive location analysis"""
        
        # Emit analysis start event
        event_simulator.emit_event(SystemEvent(
            event_type=EventType.SITE_ANALYSIS_START,
            source_system=self.agent_id,
            payload={'site_id': site.get('site_id'), 'city': site.get('city')}
        ))
        
        # Query VAHAN for EV data
        event_simulator.emit_event(SystemEvent(
            event_type=EventType.VAHAN_API_QUERY,
            source_system=self.agent_id,
            target_system='VAHAN_API',
            payload={'city': site.get('city')}
        ))
        
        ev_data = await mock_vahan.get_ev_registrations(site.get('city', ''), site.get('state', ''))
        
        event_simulator.emit_event(SystemEvent(
            event_type=EventType.VAHAN_API_RESPONSE,
            source_system='VAHAN_API',
            target_system=self.agent_id,
            payload={'ev_count': ev_data['total_ev_registrations']}
        ))
        
        # Query Census for demographics
        event_simulator.emit_event(SystemEvent(
            event_type=EventType.CENSUS_DB_QUERY,
            source_system=self.agent_id,
            target_system='Census_DB'
        ))
        
        demographics = await mock_census.get_demographics(site.get('city', ''))
        
        event_simulator.emit_event(SystemEvent(
            event_type=EventType.CENSUS_DB_RESPONSE,
            source_system='Census_DB',
            target_system=self.agent_id,
            payload={'population': demographics['total_population']}
        ))
        
        # Traffic analysis
        event_simulator.emit_event(SystemEvent(
            event_type=EventType.TRAFFIC_ANALYSIS,
            source_system=self.agent_id,
            payload={'analyzing': 'traffic patterns'}
        ))
        
        traffic_data = await mock_traffic.get_traffic_data({
            'latitude': site.get('latitude'),
            'longitude': site.get('longitude')
        })
        
        # Calculate location score
        location_score = self._calculate_location_score(
            ev_data, demographics, traffic_data, site
        )
        
        return {
            'agent': self.agent_id,
            'site_id': site.get('site_id'),
            'location_score': location_score,
            'ev_data': ev_data,
            'demographics': demographics,
            'traffic_data': traffic_data,
            'recommendation': self._generate_location_recommendation(location_score),
            'analyzed_at': datetime.now().isoformat()
        }
    
    def _calculate_location_score(
        self, 
        ev_data: Dict, 
        demographics: Dict, 
        traffic_data: Dict,
        site: Dict
    ) -> float:
        """Calculate comprehensive location score"""
        
        # EV adoption score (0-30 points)
        ev_penetration = (ev_data['total_ev_registrations'] / demographics['total_population']) * 100
        ev_score = min(30, ev_penetration * 10)
        
        # Demographics score (0-30 points)
        income = demographics['avg_household_income']
        demo_score = min(30, (income / 1500000) * 30)
        
        # Traffic score (0-25 points)
        daily_traffic = traffic_data['avg_daily_traffic']
        traffic_score = min(25, (daily_traffic / 10000) * 25)
        
        # Infrastructure score (0-15 points)
        infra_score = 15 if site.get('grid_connection_available', True) else 5
        
        total_score = ev_score + demo_score + traffic_score + infra_score
        
        return round(total_score, 2)
    
    def _generate_location_recommendation(self, score: float) -> str:
        """Generate recommendation based on score"""
        if score >= 80:
            return "Excellent location - Priority for deployment"
        elif score >= 65:
            return "Good location - Recommended for network"
        elif score >= 50:
            return "Acceptable location - Consider for Phase 2"
        else:
            return "Poor location - Not recommended"


class FinancialAnalysisAgent:
    """
    Performs detailed financial analysis and ROI projections.
    
    Responsibilities:
    - CAPEX and OPEX estimation
    - Revenue projections
    - NPV and IRR calculations
    - Break-even analysis
    """
    
    def __init__(self):
        self.agent_id = "financial-analysis-001"
        self.capabilities = ['financial_modeling', 'roi_analysis', 'cost_estimation']
    
    async def analyze_financials(self, site: Dict[str, Any], location_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive financial analysis"""
        
        event_simulator.emit_event(SystemEvent(
            event_type=EventType.FINANCIAL_ANALYSIS_START,
            source_system=self.agent_id,
            payload={'site_id': site.get('site_id')}
        ))
        
        # Get cost estimates
        event_simulator.emit_event(SystemEvent(
            event_type=EventType.CAPEX_CALCULATION,
            source_system=self.agent_id,
            target_system='Financial_System'
        ))
        
        capacity_kw = site.get('grid_capacity_kw', 500)
        cost_data = await mock_financial.get_cost_estimates(
            site.get('network_position', 'urban'),
            capacity_kw
        )
        
        # Calculate revenue projections
        event_simulator.emit_event(SystemEvent(
            event_type=EventType.ROI_PROJECTION,
            source_system=self.agent_id,
            payload={'calculating': 'revenue projections'}
        ))
        
        revenue_projections = self._project_revenues(site, location_analysis)
        
        # Calculate NPV and IRR
        event_simulator.emit_event(SystemEvent(
            event_type=EventType.NPV_CALCULATION,
            source_system=self.agent_id,
            payload={'calculating': 'NPV and IRR'}
        ))
        
        npv_irr = self._calculate_npv_irr(
            cost_data['capex_breakdown']['total'],
            cost_data['opex_annual']['total'],
            revenue_projections
        )
        
        event_simulator.emit_event(SystemEvent(
            event_type=EventType.FINANCIAL_REPORT_READY,
            source_system=self.agent_id,
            payload={'npv': npv_irr['npv'], 'irr': npv_irr['irr']}
        ))
        
        return {
            'agent': self.agent_id,
            'site_id': site.get('site_id'),
            'capex': cost_data['capex_breakdown'],
            'opex_annual': cost_data['opex_annual'],
            'revenue_projections': revenue_projections,
            'npv': npv_irr['npv'],
            'irr_percentage': npv_irr['irr'],
            'payback_years': npv_irr['payback_years'],
            'financial_score': self._calculate_financial_score(npv_irr),
            'recommendation': self._generate_financial_recommendation(npv_irr),
            'analyzed_at': datetime.now().isoformat()
        }
    
    def _project_revenues(self, site: Dict, location_analysis: Dict) -> Dict[str, float]:
        """Project revenues over 7 years"""
        
        # Base daily sessions estimate
        traffic = location_analysis.get('traffic_data', {}).get('avg_daily_traffic', 10000)
        ev_penetration = location_analysis.get('ev_data', {}).get('total_ev_registrations', 20000)
        
        daily_sessions = (traffic * 0.15) * (ev_penetration / 100000)
        
        # Revenue per session
        avg_revenue_per_session = random.uniform(200, 300)
        
        # Year 1: 60% utilization
        year_1 = daily_sessions * 365 * avg_revenue_per_session * 0.60
        
        # Subsequent years with growth
        projections = {
            'year_1': year_1,
            'year_2': year_1 * 1.15,
            'year_3': year_1 * 1.32,
            'year_4': year_1 * 1.52,
            'year_5': year_1 * 1.75,
            'year_6': year_1 * 2.01,
            'year_7': year_1 * 2.31
        }
        
        return {k: round(v, 0) for k, v in projections.items()}
    
    def _calculate_npv_irr(self, capex: float, opex_annual: float, revenue_proj: Dict) -> Dict[str, Any]:
        """Calculate NPV and IRR"""
        
        discount_rate = 0.12
        
        # Calculate discounted cash flows
        cash_flows = []
        for year in range(1, 8):
            revenue = revenue_proj[f'year_{year}']
            net_cash_flow = revenue - opex_annual
            discounted_cf = net_cash_flow / ((1 + discount_rate) ** year)
            cash_flows.append(discounted_cf)
        
        npv = sum(cash_flows) - capex
        
        # IRR approximation
        total_cf = sum(revenue_proj.values()) - (opex_annual * 7)
        irr = ((total_cf / capex) ** (1/7) - 1) * 100
        
        # Payback period
        cumulative = 0
        payback_years = 0
        for year in range(1, 8):
            cumulative += revenue_proj[f'year_{year}'] - opex_annual
            if cumulative >= capex:
                payback_years = year
                break
        
        if payback_years == 0:
            payback_years = 10
        
        return {
            'npv': round(npv, 0),
            'irr': round(irr, 2),
            'payback_years': payback_years
        }
    
    def _calculate_financial_score(self, npv_irr: Dict) -> float:
        """Calculate financial score (0-100)"""
        
        npv = npv_irr['npv']
        irr = npv_irr['irr']
        payback = npv_irr['payback_years']
        
        # NPV score (0-40)
        npv_score = min(40, (npv / 10000000) * 40) if npv > 0 else 0
        
        # IRR score (0-40)
        irr_score = min(40, (irr / 30) * 40) if irr > 0 else 0
        
        # Payback score (0-20)
        payback_score = max(0, 20 - (payback * 3))
        
        return round(npv_score + irr_score + payback_score, 2)
    
    def _generate_financial_recommendation(self, npv_irr: Dict) -> str:
        """Generate financial recommendation"""
        if npv_irr['npv'] > 5000000 and npv_irr['irr'] > 20:
            return "Highly attractive investment - Strong ROI"
        elif npv_irr['npv'] > 2000000 and npv_irr['irr'] > 15:
            return "Good investment - Positive returns expected"
        elif npv_irr['npv'] > 0 and npv_irr['irr'] > 12:
            return "Acceptable investment - Meets minimum thresholds"
        else:
            return "Poor investment - Below required returns"


class PermitManagementAgent:
    """
    Manages regulatory compliance and permit tracking.
    
    Responsibilities:
    - Permit requirement identification
    - Processing timeline estimation
    - Multi-agency coordination
    - Compliance verification
    """
    
    def __init__(self):
        self.agent_id = "permit-management-001"
        self.capabilities = ['permit_tracking', 'regulatory_compliance', 'agency_coordination']
    
    async def analyze_permit_requirements(self, site: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze permit requirements and timelines"""
        
        event_simulator.emit_event(SystemEvent(
            event_type=EventType.PERMIT_CHECK_START,
            source_system=self.agent_id,
            payload={'site_id': site.get('site_id')}
        ))
        
        city = site.get('city', '')
        state = site.get('state', '')
        
        # Query municipal portal
        event_simulator.emit_event(SystemEvent(
            event_type=EventType.MUNICIPAL_PORTAL_QUERY,
            source_system=self.agent_id,
            target_system=f'{city}_Municipal',
            payload={'checking': 'land use clearance'}
        ))
        
        municipal_portal = get_municipal_portal(city)
        land_clearance = await municipal_portal.check_land_use_clearance({
            'latitude': site.get('latitude'),
            'longitude': site.get('longitude')
        })
        
        event_simulator.emit_event(SystemEvent(
            event_type=EventType.MUNICIPAL_PORTAL_RESPONSE,
            source_system=f'{city}_Municipal',
            target_system=self.agent_id,
            payload={'clearance': land_clearance['clearance_available']}
        ))
        
        # Identify required permits
        required_permits = self._identify_required_permits(site, state)
        
        # Estimate timeline
        event_simulator.emit_event(SystemEvent(
            event_type=EventType.PERMIT_TIMELINE_ESTIMATE,
            source_system=self.agent_id,
            payload={'estimating': 'permit approval timeline'}
        ))
        
        timeline = self._estimate_permit_timeline(required_permits)
        
        event_simulator.emit_event(SystemEvent(
            event_type=EventType.PERMIT_REPORT_READY,
            source_system=self.agent_id,
            payload={'total_permits': len(required_permits), 'timeline_days': timeline['total_days']}
        ))
        
        return {
            'agent': self.agent_id,
            'site_id': site.get('site_id'),
            'land_use_clearance': land_clearance,
            'required_permits': required_permits,
            'timeline': timeline,
            'regulatory_score': self._calculate_regulatory_score(land_clearance, timeline),
            'recommendation': self._generate_permit_recommendation(timeline),
            'analyzed_at': datetime.now().isoformat()
        }
    
    def _identify_required_permits(self, site: Dict, state: str) -> List[Dict[str, Any]]:
        """Identify all required permits"""
        
        permits = [
            {
                'type': 'Land Use Clearance',
                'agency': f"{site.get('city')} Municipal Corporation",
                'estimated_days': random.randint(30, 60),
                'fees': random.randint(15000, 40000),
                'priority': 'High'
            },
            {
                'type': 'Building Permit',
                'agency': f"{site.get('city')} Building Department",
                'estimated_days': random.randint(40, 75),
                'fees': random.randint(25000, 60000),
                'priority': 'High'
            },
            {
                'type': 'Fire Safety NOC',
                'agency': f"{state} Fire Services",
                'estimated_days': random.randint(20, 45),
                'fees': random.randint(10000, 25000),
                'priority': 'High'
            },
            {
                'type': 'Electrical Safety Certificate',
                'agency': 'Chief Electrical Inspector',
                'estimated_days': random.randint(15, 30),
                'fees': random.randint(8000, 20000),
                'priority': 'Medium'
            },
            {
                'type': 'Environmental Clearance',
                'agency': f"{state} Pollution Control Board",
                'estimated_days': random.randint(50, 90),
                'fees': random.randint(30000, 70000),
                'priority': 'Medium'
            },
            {
                'type': 'Grid Connection Approval',
                'agency': f"{state} Electricity Distribution Company",
                'estimated_days': random.randint(30, 60),
                'fees': random.randint(500000, 1500000),
                'priority': 'High'
            }
        ]
        
        return permits
    
    def _estimate_permit_timeline(self, permits: List[Dict]) -> Dict[str, Any]:
        """Estimate total permit timeline"""
        
        # Some permits can be parallel, others sequential
        critical_path_days = max(p['estimated_days'] for p in permits)
        parallel_savings = random.randint(20, 40)
        
        total_days = critical_path_days + parallel_savings
        total_fees = sum(p['fees'] for p in permits)
        
        return {
            'total_days': total_days,
            'total_fees': total_fees,
            'critical_path': critical_path_days,
            'parallel_processing_possible': True,
            'expedited_available': random.choice([True, False]),
            'expedited_timeline_days': int(total_days * 0.7) if random.choice([True, False]) else None
        }
    
    def _calculate_regulatory_score(self, clearance: Dict, timeline: Dict) -> float:
        """Calculate regulatory ease score"""
        
        # Base score
        score = 50
        
        # Land clearance
        if clearance.get('clearance_available'):
            score += 25
        
        # Timeline
        if timeline['total_days'] < 90:
            score += 15
        elif timeline['total_days'] < 120:
            score += 10
        elif timeline['total_days'] < 150:
            score += 5
        
        # Fees
        if timeline['total_fees'] < 1000000:
            score += 10
        elif timeline['total_fees'] < 2000000:
            score += 5
        
        return min(100, score)
    
    def _generate_permit_recommendation(self, timeline: Dict) -> str:
        """Generate permit recommendation"""
        days = timeline['total_days']
        
        if days < 90:
            return "Fast-track regulatory path - Minimal delays expected"
        elif days < 120:
            return "Standard regulatory timeline - Manageable approval process"
        elif days < 150:
            return "Extended timeline - Consider parallel processing"
        else:
            return "Complex regulatory environment - Significant delays likely"


class MarketIntelligenceAgent:
    """
    Analyzes market conditions and competitive landscape.
    
    Responsibilities:
    - Competitor analysis
    - Demand forecasting
    - Pricing intelligence
    - Market saturation assessment
    """
    
    def __init__(self):
        self.agent_id = "market-intelligence-001"
        self.capabilities = ['competitor_analysis', 'demand_forecasting', 'pricing_intelligence']
    
    async def analyze_market(self, site: Dict[str, Any], location_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive market analysis"""
        
        event_simulator.emit_event(SystemEvent(
            event_type=EventType.MARKET_ANALYSIS_START,
            source_system=self.agent_id,
            payload={'site_id': site.get('site_id')}
        ))
        
        city = site.get('city', '')
        
        # Competitor analysis
        event_simulator.emit_event(SystemEvent(
            event_type=EventType.COMPETITOR_ANALYSIS,
            source_system=self.agent_id,
            target_system='Competitor_DB',
            payload={'analyzing': 'competitor landscape'}
        ))
        
        competitors = await mock_competitor.get_nearby_competitors({
            'latitude': site.get('latitude'),
            'longitude': site.get('longitude')
        }, radius_km=5)
        
        # Pricing intelligence
        pricing_data = await mock_competitor.get_pricing_intelligence(city)
        
        # Demand forecast
        event_simulator.emit_event(SystemEvent(
            event_type=EventType.DEMAND_FORECAST,
            source_system=self.agent_id,
            payload={'forecasting': 'charging demand'}
        ))
        
        demand_forecast = self._forecast_demand(site, location_analysis, competitors)
        
        event_simulator.emit_event(SystemEvent(
            event_type=EventType.MARKET_REPORT_READY,
            source_system=self.agent_id,
            payload={
                'competitors': competitors['competitors_found'],
                'demand_sessions_daily': demand_forecast['daily_sessions']
            }
        ))
        
        return {
            'agent': self.agent_id,
            'site_id': site.get('site_id'),
            'competitors': competitors,
            'pricing_intelligence': pricing_data,
            'demand_forecast': demand_forecast,
            'market_score': self._calculate_market_score(competitors, demand_forecast),
            'recommendation': self._generate_market_recommendation(competitors, demand_forecast),
            'analyzed_at': datetime.now().isoformat()
        }
    
    def _forecast_demand(self, site: Dict, location_analysis: Dict, competitors: Dict) -> Dict[str, Any]:
        """Forecast charging demand"""
        
        # Base demand from traffic and EV penetration
        traffic = location_analysis.get('traffic_data', {}).get('avg_daily_traffic', 10000)
        ev_count = location_analysis.get('ev_data', {}).get('total_ev_registrations', 20000)
        
        # Market capture rate (lower if high competition)
        competition_impact = 1.0 - (competitors['competitors_found'] * 0.15)
        
        daily_sessions = (traffic * 0.15) * (ev_count / 100000) * competition_impact
        daily_sessions = max(20, daily_sessions)  # Minimum threshold
        
        # Revenue projection
        avg_revenue_per_session = 250
        daily_revenue = daily_sessions * avg_revenue_per_session
        
        return {
            'daily_sessions': round(daily_sessions, 0),
            'daily_revenue': round(daily_revenue, 0),
            'monthly_sessions': round(daily_sessions * 30, 0),
            'annual_sessions': round(daily_sessions * 365, 0),
            'growth_rate_yoy': random.uniform(20, 40),
            'confidence_level': random.uniform(0.75, 0.92)
        }
    
    def _calculate_market_score(self, competitors: Dict, demand: Dict) -> float:
        """Calculate market attractiveness score"""
        
        # Competition score (0-40)
        comp_count = competitors['competitors_found']
        comp_score = max(0, 40 - (comp_count * 12))
        
        # Demand score (0-40)
        daily_sessions = demand['daily_sessions']
        demand_score = min(40, (daily_sessions / 100) * 40)
        
        # Growth score (0-20)
        growth = demand['growth_rate_yoy']
        growth_score = min(20, (growth / 50) * 20)
        
        return round(comp_score + demand_score + growth_score, 2)
    
    def _generate_market_recommendation(self, competitors: Dict, demand: Dict) -> str:
        """Generate market recommendation"""
        comp_count = competitors['competitors_found']
        daily_sessions = demand['daily_sessions']
        
        if comp_count == 0 and daily_sessions > 80:
            return "Excellent market opportunity - First mover advantage"
        elif comp_count <= 1 and daily_sessions > 60:
            return "Strong market potential - Good demand with low competition"
        elif comp_count <= 2 and daily_sessions > 40:
            return "Moderate market - Sufficient demand despite competition"
        else:
            return "Challenging market - High competition or low demand"


class NetworkOptimizationAgent:
    """
    Optimizes network configuration and site selection.
    
    Responsibilities:
    - Site ranking and selection
    - Network coverage optimization
    - Budget allocation
    - Portfolio optimization
    """
    
    def __init__(self):
        self.agent_id = "network-optimization-001"
        self.capabilities = ['site_selection', 'network_optimization', 'budget_allocation']
    
    async def optimize_network_selection(
        self,
        evaluated_sites: List[Dict[str, Any]],
        budget: float,
        target_count: int,
        objective: str = 'balanced'
    ) -> Dict[str, Any]:
        """Optimize site selection for network"""
        
        event_simulator.emit_event(SystemEvent(
            event_type=EventType.NETWORK_OPTIMIZATION_START,
            source_system=self.agent_id,
            payload={
                'candidate_sites': len(evaluated_sites),
                'budget': budget,
                'target_sites': target_count
            }
        ))
        
        # Rank sites
        ranked_sites = self._rank_sites(evaluated_sites, objective)
        
        # Select sites within budget
        event_simulator.emit_event(SystemEvent(
            event_type=EventType.SITE_SELECTION,
            source_system=self.agent_id,
            payload={'selecting': 'optimal sites'}
        ))
        
        selected_sites = self._select_sites(ranked_sites, budget, target_count)
        
        # Calculate network metrics
        event_simulator.emit_event(SystemEvent(
            event_type=EventType.COVERAGE_OPTIMIZATION,
            source_system=self.agent_id,
            payload={'calculating': 'network coverage'}
        ))
        
        network_metrics = self._calculate_network_metrics(selected_sites)
        
        event_simulator.emit_event(SystemEvent(
            event_type=EventType.NETWORK_PLAN_READY,
            source_system=self.agent_id,
            payload={
                'selected_count': len(selected_sites),
                'total_investment': network_metrics['total_capex']
            }
        ))
        
        return {
            'agent': self.agent_id,
            'selected_sites': selected_sites,
            'network_metrics': network_metrics,
            'optimization_objective': objective,
            'recommendation': self._generate_network_recommendation(network_metrics),
            'optimized_at': datetime.now().isoformat()
        }
    
    def _rank_sites(self, sites: List[Dict], objective: str) -> List[Dict]:
        """Rank sites based on objective"""
        
        for site in sites:
            if objective == 'max_roi':
                site['rank_score'] = site.get('financial_score', 0) * 0.7 + site.get('location_score', 0) * 0.3
            elif objective == 'max_coverage':
                site['rank_score'] = site.get('location_score', 0) * 0.6 + site.get('market_score', 0) * 0.4
            else:  # balanced
                site['rank_score'] = (
                    site.get('location_score', 0) * 0.3 +
                    site.get('financial_score', 0) * 0.3 +
                    site.get('market_score', 0) * 0.2 +
                    site.get('regulatory_score', 0) * 0.2
                )
        
        return sorted(sites, key=lambda x: x['rank_score'], reverse=True)
    
    def _select_sites(self, ranked_sites: List[Dict], budget: float, target_count: int) -> List[Dict]:
        """Select sites within budget constraints"""
        
        selected = []
        total_spent = 0
        
        for site in ranked_sites:
            if len(selected) >= target_count:
                break
            
            capex = site.get('capex', {}).get('total', 3000000)
            
            if total_spent + capex <= budget:
                selected.append(site)
                total_spent += capex
        
        return selected
    
    def _calculate_network_metrics(self, selected_sites: List[Dict]) -> Dict[str, Any]:
        """Calculate overall network metrics"""
        
        total_capex = sum(s.get('capex', {}).get('total', 3000000) for s in selected_sites)
        total_revenue_y1 = sum(s.get('revenue_projections', {}).get('year_1', 2000000) for s in selected_sites)
        avg_npv = sum(s.get('npv', 0) for s in selected_sites) / len(selected_sites) if selected_sites else 0
        
        # Geographic coverage
        unique_cities = len(set(s.get('city') for s in selected_sites))
        
        return {
            'sites_selected': len(selected_sites),
            'total_capex': total_capex,
            'total_revenue_year1': total_revenue_y1,
            'network_npv': avg_npv * len(selected_sites),
            'coverage_cities': unique_cities,
            'avg_site_score': sum(s.get('rank_score', 0) for s in selected_sites) / len(selected_sites) if selected_sites else 0
        }
    
    def _generate_network_recommendation(self, metrics: Dict) -> str:
        """Generate network recommendation"""
        sites = metrics['sites_selected']
        npv = metrics['network_npv']
        
        if npv > 50000000 and sites >= 30:
            return "Excellent network configuration - Strong portfolio"
        elif npv > 25000000 and sites >= 20:
            return "Good network configuration - Solid foundation"
        elif npv > 10000000:
            return "Acceptable network - Meets minimum criteria"
        else:
            return "Weak network configuration - Consider revisions"


# Create singleton instances
geographic_intelligence_agent = GeographicIntelligenceAgent()
financial_analysis_agent = FinancialAnalysisAgent()
permit_management_agent = PermitManagementAgent()
market_intelligence_agent = MarketIntelligenceAgent()
network_optimization_agent = NetworkOptimizationAgent()
