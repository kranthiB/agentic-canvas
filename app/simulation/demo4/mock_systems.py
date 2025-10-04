"""
Mock External Systems for EV Charging Network Simulation
Simulates external APIs and databases
"""
import asyncio
import random
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional


class MockVAHANAPI:
    """Mock VAHAN (Vehicle Registration) API - Government of India"""
    
    async def get_ev_registrations(self, city: str, state: str) -> Dict[str, Any]:
        """Get EV registration data for a city"""
        await asyncio.sleep(random.uniform(0.3, 0.8))
        
        base_registrations = {
            'Mumbai': 45000,
            'Delhi': 38000,
            'Bengaluru': 52000,
            'Hyderabad': 28000,
            'Pune': 22000,
            'Chennai': 25000,
            'Ahmedabad': 18000
        }
        
        total_evs = base_registrations.get(city, random.randint(8000, 20000))
        
        return {
            'city': city,
            'state': state,
            'total_ev_registrations': total_evs,
            'monthly_new_registrations': int(total_evs * 0.035),
            'ev_types': {
                'two_wheeler': int(total_evs * 0.62),
                'three_wheeler': int(total_evs * 0.18),
                'passenger_car': int(total_evs * 0.15),
                'commercial_vehicle': int(total_evs * 0.05)
            },
            'growth_rate_yoy': random.uniform(25, 45),
            'data_date': date.today().isoformat(),
            'source': 'VAHAN Database'
        }
    
    async def get_vehicle_density(self, latitude: float, longitude: float, radius_km: float = 5) -> Dict[str, Any]:
        """Get vehicle density in an area"""
        await asyncio.sleep(random.uniform(0.2, 0.5))
        
        return {
            'center': {'latitude': latitude, 'longitude': longitude},
            'radius_km': radius_km,
            'total_vehicles': random.randint(50000, 200000),
            'ev_count': random.randint(1000, 8000),
            'ev_penetration_rate': random.uniform(1.5, 4.2),
            'daily_traffic': random.randint(8000, 25000)
        }


class MockCensusDatabase:
    """Mock Census Database - India Government"""
    
    async def get_demographics(self, city: str) -> Dict[str, Any]:
        """Get demographic data for a city"""
        await asyncio.sleep(random.uniform(0.3, 0.6))
        
        population_data = {
            'Mumbai': 12442373,
            'Delhi': 11034555,
            'Bengaluru': 8443675,
            'Hyderabad': 6809970,
            'Chennai': 7088000,
            'Pune': 3124458,
            'Ahmedabad': 5577940
        }
        
        population = population_data.get(city, random.randint(500000, 2000000))
        
        return {
            'city': city,
            'total_population': population,
            'population_density': population / 500,  # Simplified
            'households': int(population / 4.5),
            'avg_household_income': random.randint(600000, 1200000),
            'income_distribution': {
                'low': 0.35,
                'middle': 0.45,
                'high': 0.20
            },
            'literacy_rate': random.uniform(82, 95),
            'vehicle_ownership_rate': random.uniform(0.20, 0.35),
            'data_year': 2021
        }


class MockMunicipalPortal:
    """Mock Municipal Corporation Portal"""
    
    def __init__(self, city: str):
        self.city = city
        self.portal_name = f"{city} Municipal Corporation"
    
    async def check_land_use_clearance(self, location: Dict[str, float]) -> Dict[str, Any]:
        """Check if land use permits charging station"""
        await asyncio.sleep(random.uniform(0.5, 1.0))
        
        return {
            'clearance_available': random.random() > 0.15,
            'land_use_zone': random.choice(['Commercial', 'Mixed Use', 'Industrial', 'Residential']),
            'restrictions': [],
            'additional_permits_required': random.choice([
                ['Building Permit', 'Fire Safety NOC'],
                ['Environmental Clearance'],
                ['Traffic Impact Assessment']
            ]),
            'estimated_approval_days': random.randint(30, 90),
            'fees_estimated': random.randint(25000, 75000),
            'portal': self.portal_name
        }
    
    async def get_building_permits_status(self, site_id: str) -> Dict[str, Any]:
        """Get status of building permits"""
        await asyncio.sleep(random.uniform(0.3, 0.7))
        
        return {
            'site_id': site_id,
            'permits': [
                {
                    'type': 'Building Permit',
                    'status': random.choice(['Approved', 'Under Review', 'Submitted', 'Pending']),
                    'submitted_date': (date.today() - timedelta(days=random.randint(10, 60))).isoformat(),
                    'estimated_approval': random.randint(15, 45)
                },
                {
                    'type': 'Fire Safety NOC',
                    'status': random.choice(['Approved', 'Under Review', 'Submitted']),
                    'submitted_date': (date.today() - timedelta(days=random.randint(5, 40))).isoformat(),
                    'estimated_approval': random.randint(10, 30)
                }
            ]
        }


class MockGridMonitoring:
    """Mock Grid Capacity Monitoring System"""
    
    def __init__(self, utility_name: str):
        self.utility_name = utility_name
    
    async def check_grid_capacity(self, location: Dict[str, float]) -> Dict[str, Any]:
        """Check grid capacity at location"""
        await asyncio.sleep(random.uniform(0.4, 0.8))
        
        return {
            'location': location,
            'grid_available': random.random() > 0.1,
            'available_capacity_kw': random.choice([250, 500, 750, 1000, 1500]),
            'transformer_proximity_km': random.uniform(0.1, 2.5),
            'voltage_level': random.choice(['11kV', '33kV', '66kV']),
            'connection_cost_estimate': random.randint(500000, 2000000),
            'connection_timeline_days': random.randint(45, 120),
            'utility': self.utility_name,
            'reliability_score': random.uniform(92, 98)
        }
    
    async def get_load_profile(self, site_id: str) -> Dict[str, Any]:
        """Get load profile for a site"""
        await asyncio.sleep(random.uniform(0.2, 0.5))
        
        return {
            'site_id': site_id,
            'peak_load_kw': random.uniform(200, 500),
            'off_peak_load_kw': random.uniform(50, 150),
            'load_factor': random.uniform(0.65, 0.85),
            'power_factor': random.uniform(0.90, 0.98),
            'hourly_profile': [random.uniform(50, 300) for _ in range(24)]
        }


class MockCompetitorDatabase:
    """Mock Competitor Intelligence Database"""
    
    async def get_nearby_competitors(self, location: Dict[str, float], radius_km: float = 5) -> Dict[str, Any]:
        """Get competitors in area"""
        await asyncio.sleep(random.uniform(0.3, 0.7))
        
        competitors = [
            'Tata Power EZ Charge',
            'Fortum Charge & Drive',
            'Ather Grid',
            'Magenta ChargeGrid',
            'ChargeZone'
        ]
        
        nearby = random.randint(0, 3)
        
        stations = []
        for i in range(nearby):
            stations.append({
                'operator': random.choice(competitors),
                'distance_km': random.uniform(0.5, 5.0),
                'chargers': random.randint(2, 8),
                'pricing': random.uniform(16, 22),
                'utilization': random.uniform(45, 85)
            })
        
        return {
            'location': location,
            'radius_km': radius_km,
            'competitors_found': nearby,
            'stations': stations,
            'market_saturation': 'Low' if nearby == 0 else 'Medium' if nearby <= 2 else 'High'
        }
    
    async def get_pricing_intelligence(self, city: str) -> Dict[str, Any]:
        """Get pricing data for city"""
        await asyncio.sleep(random.uniform(0.2, 0.5))
        
        return {
            'city': city,
            'avg_price_inr_kwh': random.uniform(17, 21),
            'price_range': {
                'min': random.uniform(15, 17),
                'max': random.uniform(22, 26)
            },
            'peak_hour_premium': random.uniform(1.15, 1.35),
            'pricing_models': ['Fixed', 'Dynamic', 'Time-of-Use']
        }


class MockTrafficAnalysis:
    """Mock Traffic Analysis System"""
    
    async def get_traffic_data(self, location: Dict[str, float]) -> Dict[str, Any]:
        """Get traffic data for location"""
        await asyncio.sleep(random.uniform(0.4, 0.9))
        
        return {
            'location': location,
            'avg_daily_traffic': random.randint(8000, 25000),
            'peak_hours': ['08:00-10:00', '18:00-21:00'],
            'peak_hour_factor': random.uniform(1.8, 2.5),
            'traffic_composition': {
                'two_wheeler': 0.55,
                'four_wheeler': 0.38,
                'commercial': 0.07
            },
            'congestion_level': random.choice(['Low', 'Medium', 'High']),
            'data_source': 'Google Traffic API (Simulated)'
        }


class MockWeatherService:
    """Mock Weather Service"""
    
    async def get_weather_data(self, city: str) -> Dict[str, Any]:
        """Get weather data"""
        await asyncio.sleep(random.uniform(0.1, 0.3))
        
        return {
            'city': city,
            'temperature_celsius': random.uniform(22, 38),
            'humidity': random.uniform(45, 85),
            'conditions': random.choice(['Clear', 'Partly Cloudy', 'Cloudy', 'Rain']),
            'ev_usage_impact': random.choice(['Low', 'Medium', 'High'])
        }


class MockFinancialSystem:
    """Mock Financial System for cost estimation"""
    
    async def get_cost_estimates(self, site_type: str, capacity_kw: float) -> Dict[str, Any]:
        """Get cost estimates for charging station"""
        await asyncio.sleep(random.uniform(0.3, 0.6))
        
        # Base costs
        land_cost = random.uniform(5000000, 15000000)
        equipment_cost = capacity_kw * random.uniform(25000, 35000)
        civil_work = random.uniform(800000, 1500000)
        grid_connection = random.uniform(500000, 2000000)
        
        total_capex = land_cost + equipment_cost + civil_work + grid_connection
        
        return {
            'site_type': site_type,
            'capacity_kw': capacity_kw,
            'capex_breakdown': {
                'land_cost': land_cost,
                'equipment_cost': equipment_cost,
                'civil_work': civil_work,
                'grid_connection': grid_connection,
                'total': total_capex
            },
            'opex_annual': {
                'electricity': random.uniform(300000, 600000),
                'maintenance': random.uniform(150000, 300000),
                'staff': random.uniform(400000, 800000),
                'total': random.uniform(850000, 1700000)
            },
            'revenue_projections': {
                'year_1': random.uniform(2000000, 4000000),
                'year_5': random.uniform(4000000, 8000000)
            }
        }


# Create singleton instances
mock_vahan = MockVAHANAPI()
mock_census = MockCensusDatabase()
mock_traffic = MockTrafficAnalysis()
mock_weather = MockWeatherService()
mock_competitor = MockCompetitorDatabase()
mock_financial = MockFinancialSystem()


def get_municipal_portal(city: str) -> MockMunicipalPortal:
    """Get municipal portal for city"""
    return MockMunicipalPortal(city)


def get_grid_monitoring(state: str) -> MockGridMonitoring:
    """Get grid monitoring system for state"""
    utility_map = {
        'Maharashtra': 'MSEDCL',
        'Karnataka': 'BESCOM',
        'Delhi': 'BSES',
        'Tamil Nadu': 'TANGEDCO',
        'Telangana': 'TSSPDCL',
        'Gujarat': 'DGVCL'
    }
    
    utility_name = utility_map.get(state, 'State Electricity Board')
    return MockGridMonitoring(utility_name)
