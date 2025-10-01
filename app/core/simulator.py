"""
Real-time data simulator for all demos
Generates realistic industrial data streams
"""
import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any
import threading
import time


class UnifiedSimulator:
    """Unified simulator for all 5 demos"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        
        # Demo 1: Carbon Compass
        self.emissions_rate = 250.0  # kg/hr
        self.production_rate = 950.0  # barrels/hr
        self.carbon_budget = 100000  # Mt annually
        self.carbon_consumed = 45.2  # Mt year-to-date
        
        # Demo 2: GridMind AI (Khavda)
        self.solar_generation = 18000  # MW
        self.wind_generation = 9000  # MW
        self.battery_soc = 0.65  # State of charge (0-1)
        self.grid_frequency = 50.00  # Hz
        self.market_price = 3200  # INR/MWh
        
        # Demo 3: Safety Guardian
        self.gas_readings = {
            'O2': 20.9,
            'LEL': 0.0,
            'H2S': 0.0,
            'CO': 0.0
        }
        self.active_permits = []
        self.risk_level = 'low'
        
        # Demo 4: Mobility Maestro
        self.ev_demand = {}
        self.charging_load = 0
        
        # Demo 5: Engineer's Copilot
        self.lab_temperature = 25.0
        self.active_tests = 0
    
    def start(self):
        """Start simulation thread"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._simulation_loop, daemon=True)
            self.thread.start()
            print('Simulator started')
    
    def stop(self):
        """Stop simulation thread"""
        self.running = False
        if self.thread:
            self.thread.join()
        print('Simulator stopped')
    
    def _simulation_loop(self):
        """Main simulation loop"""
        while self.running:
            self.update_all()
            time.sleep(1.0)  # Update every second
    
    def update_all(self):
        """Update all simulation states"""
        self._update_carbon_compass()
        self._update_gridmind()
        self._update_safety_guardian()
        self._update_mobility_maestro()
        self._update_engineers_copilot()
    
    # Demo 1: Carbon Compass Updates
    def _update_carbon_compass(self):
        """Update carbon emissions simulation"""
        # Add random walk to emissions
        self.emissions_rate += random.gauss(0, 5)
        self.emissions_rate = max(150, min(400, self.emissions_rate))
        
        # Production varies with emissions
        self.production_rate += random.gauss(0, 10)
        self.production_rate = max(800, min(1100, self.production_rate))
        
        # Update consumed budget (kg/hr to Mt/year)
        hourly_mt = self.emissions_rate / 1_000_000
        self.carbon_consumed += hourly_mt / 8760
    
    # Demo 2: GridMind AI Updates
    def _update_gridmind(self):
        """Update renewable energy plant simulation"""
        # Solar follows sine wave (day/night cycle)
        hour = datetime.now().hour
        solar_factor = max(0, math.sin((hour - 6) * math.pi / 12))
        self.solar_generation = 20000 * solar_factor * random.uniform(0.9, 1.0)
        
        # Wind is more random
        self.wind_generation += random.gauss(0, 500)
        self.wind_generation = max(5000, min(12000, self.wind_generation))
        
        # Battery charges/discharges
        net_generation = self.solar_generation + self.wind_generation
        if net_generation > 25000:
            self.battery_soc += 0.001
        else:
            self.battery_soc -= 0.001
        self.battery_soc = max(0.2, min(0.95, self.battery_soc))
        
        # Grid frequency stability
        self.grid_frequency += random.gauss(0, 0.02)
        self.grid_frequency = max(49.8, min(50.2, self.grid_frequency))
        
        # Market price varies
        self.market_price += random.gauss(0, 100)
        self.market_price = max(2500, min(4500, self.market_price))
    
    # Demo 3: Safety Guardian Updates
    def _update_safety_guardian(self):
        """Update refinery safety simulation"""
        # Gas readings with occasional spikes
        if random.random() < 0.02:  # 2% chance of alarm
            self.gas_readings['LEL'] = random.uniform(10, 25)
            self.risk_level = 'high'
        else:
            self.gas_readings['O2'] = 20.9 + random.gauss(0, 0.1)
            self.gas_readings['LEL'] = max(0, random.gauss(0, 0.5))
            self.gas_readings['H2S'] = max(0, random.gauss(0, 0.2))
            self.gas_readings['CO'] = max(0, random.gauss(0, 1))
            
            # Determine risk level
            if self.gas_readings['LEL'] > 10:
                self.risk_level = 'critical'
            elif self.gas_readings['LEL'] > 5:
                self.risk_level = 'high'
            elif any(v > 5 for v in self.gas_readings.values()):
                self.risk_level = 'medium'
            else:
                self.risk_level = 'low'
    
    # Demo 4: Mobility Maestro Updates
    def _update_mobility_maestro(self):
        """Update EV charging network simulation"""
        # Simulate demand by hour
        hour = datetime.now().hour
        if 8 <= hour <= 10 or 17 <= hour <= 19:
            self.charging_load = random.uniform(70, 95)
        else:
            self.charging_load = random.uniform(20, 50)
    
    # Demo 5: Engineer's Copilot Updates
    def _update_engineers_copilot(self):
        """Update R&D lab simulation"""
        self.lab_temperature = 25.0 + random.gauss(0, 0.5)
        self.active_tests = random.randint(2, 8)
    
    # Get current state
    def get_state(self, demo_id: int = None) -> Dict[str, Any]:
        """Get current simulation state"""
        if demo_id == 1:
            return self._get_carbon_state()
        elif demo_id == 2:
            return self._get_gridmind_state()
        elif demo_id == 3:
            return self._get_safety_state()
        elif demo_id == 4:
            return self._get_mobility_state()
        elif demo_id == 5:
            return self._get_copilot_state()
        else:
            return {
                'demo1': self._get_carbon_state(),
                'demo2': self._get_gridmind_state(),
                'demo3': self._get_safety_state(),
                'demo4': self._get_mobility_state(),
                'demo5': self._get_copilot_state()
            }
    
    def _get_carbon_state(self):
        return {
            'emissions_rate': round(self.emissions_rate, 1),
            'production_rate': round(self.production_rate, 1),
            'carbon_budget': self.carbon_budget,
            'carbon_consumed': round(self.carbon_consumed, 2),
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_gridmind_state(self):
        return {
            'solar_generation': round(self.solar_generation, 1),
            'wind_generation': round(self.wind_generation, 1),
            'total_generation': round(self.solar_generation + self.wind_generation, 1),
            'battery_soc': round(self.battery_soc, 3),
            'grid_frequency': round(self.grid_frequency, 2),
            'market_price': round(self.market_price, 2),
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_safety_state(self):
        return {
            'gas_readings': {k: round(v, 2) for k, v in self.gas_readings.items()},
            'risk_level': self.risk_level,
            'active_permits': len(self.active_permits),
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_mobility_state(self):
        return {
            'charging_load': round(self.charging_load, 1),
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_copilot_state(self):
        return {
            'lab_temperature': round(self.lab_temperature, 1),
            'active_tests': self.active_tests,
            'timestamp': datetime.now().isoformat()
        }


# Global simulator instance
simulator = UnifiedSimulator()