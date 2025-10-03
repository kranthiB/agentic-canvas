"""
Mock Enterprise Systems

These classes simulate the behavior of real enterprise systems like SAP ERP,
LIMS (Laboratory Information Management System), PLM (Product Lifecycle Management),
and external regulatory databases.

The goal is not to replicate every feature of these complex systems, but rather
to create convincing responses that demonstrate how they integrate into the
Engineer's Copilot architecture. Think of these as "method actors" - they stay
in character and provide realistic responses that make the demo believable.

Each mock system:
1. Responds with realistic data structures
2. Introduces appropriate delays to simulate network calls
3. Maintains internal state to create consistency
4. Logs interactions for the event visualization
"""

import random
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from .event_simulator import SystemEvent, EventType, event_simulator


class MockSAPSystem:
    """
    Simulates SAP ERP system responses for material master data, costs,
    and supplier information.
    
    SAP is TotalEnergies' core enterprise resource planning system. In production,
    we would integrate via SAP's RFC/BAPI interface or their REST APIs. Here, we
    simulate those responses with realistic data.
    
    The data structures mirror what you'd actually get from SAP:
    - Material master records with all attributes
    - Pricing with currency and date validity
    - Supplier relationships and lead times
    """
    
    def __init__(self):
        self.system_name = "SAP_ERP"
        
        # Base oil data
        self.base_oils = [
            {
                'material_code': 'BO-GRP2-001',
                'description': 'Group II Base Oil - 150N',
                'viscosity_grade': '150N',
                'api_group': 'Group II',
                'sulphur_content_ppm': 50,
                'viscosity_index': 105,
                'price_per_liter_inr': 52.50,
                'stock_qty_liters': 25000,
                'lead_time_days': 7,
                'preferred_supplier': 'IndianOil Corporation'
            },
            {
                'material_code': 'BO-PAO4-003',
                'description': 'PAO 4 Synthetic Base Oil',
                'viscosity_grade': 'PAO4',
                'api_group': 'Group IV',
                'sulphur_content_ppm': 0,
                'viscosity_index': 130,
                'price_per_liter_inr': 125.00,
                'stock_qty_liters': 5000,
                'lead_time_days': 21,
                'preferred_supplier': 'Chevron Phillips Chemical'
            }
        ]
        
        # Additive packages
        self.additives = [
            {
                'material_code': 'ADD-ZDDP-001',
                'description': 'Zinc Dialkyl Dithiophosphate (ZDDP)',
                'functional_group': 'Anti-wear',
                'active_ingredient_percent': 8.5,
                'price_per_kg_inr': 420.00,
                'stock_qty_kg': 2500,
                'treat_rate_percent': 0.08
            },
            {
                'material_code': 'ADD-PIB-003',
                'description': 'Polyisobutylene Viscosity Modifier',
                'functional_group': 'Viscosity Modifier',
                'active_ingredient_percent': 100.0,
                'price_per_kg_inr': 95.75,
                'stock_qty_kg': 3500,
                'treat_rate_percent': 12.0
            }
        ]
    
    async def query_materials(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query material master data from SAP. This simulates the MM (Material Management)
        module's API responses.
        """
        # Simulate network and processing delay
        await asyncio.sleep(random.uniform(0.05, 0.15))  # 50-150ms
        
        material_type = query_params.get('material_type', 'all')
        
        results = []
        if material_type in ['base_oil', 'all']:
            results.extend(self.base_oils)
        if material_type in ['additive', 'all']:
            results.extend(self.additives)
        
        response = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'query_params': query_params,
            'results_count': len(results),
            'materials': results,
            'data_source': 'SAP ERP - Material Master (MM module)'
        }
        
        return response
    
    async def get_material_costs(self, material_codes: List[str]) -> Dict[str, Any]:
        """
        Get current pricing for materials. This simulates SAP's pricing condition
        records and reflects real market dynamics.
        """
        await asyncio.sleep(random.uniform(0.05, 0.12))
        
        # Find materials by code
        all_materials = self.base_oils + self.additives
        found_materials = [
            m for m in all_materials 
            if m['material_code'] in material_codes
        ]
        
        # Build pricing response
        pricing_data = []
        for material in found_materials:
            # Add some price variance to simulate market fluctuations
            price_key = 'price_per_liter_inr' if 'price_per_liter_inr' in material else 'price_per_kg_inr'
            base_price = material[price_key]
            # +/- 5% variation
            current_price = base_price * random.uniform(0.95, 1.05)
            
            pricing_data.append({
                'material_code': material['material_code'],
                'description': material['description'],
                'price': round(current_price, 2),
                'currency': 'INR',
                'unit': 'per liter' if 'liter' in price_key else 'per kg',
                'valid_from': datetime.now().isoformat(),
                'valid_to': (datetime.now() + timedelta(days=90)).isoformat(),
                'price_trend': random.choice(['stable', 'increasing', 'decreasing'])
            })
        
        response = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'pricing_data': pricing_data,
            'data_source': 'SAP ERP - Pricing Conditions'
        }
        
        return response
    
    async def check_supplier_availability(self, material_codes: List[str]) -> Dict[str, Any]:
        """
        Check supplier availability and lead times. This simulates integration
        with SAP's supplier relationship management.
        """
        await asyncio.sleep(random.uniform(0.08, 0.18))
        
        all_materials = self.base_oils + self.additives
        availability_data = []
        
        for code in material_codes:
            material = next((m for m in all_materials if m['material_code'] == code), None)
            if material:
                # Simulate availability status
                is_available = random.random() > 0.1  # 90% availability
                
                availability_data.append({
                    'material_code': code,
                    'supplier': material.get('preferred_supplier', material.get('supplier')),
                    'available': is_available,
                    'stock_level': material.get('stock_qty_liters', material.get('stock_qty_kg', 0)),
                    'lead_time_days': material.get('lead_time_days', 7),
                    'min_order_quantity': random.choice([100, 200, 500, 1000]),
                    'delivery_reliability': random.uniform(0.85, 0.98)
                })
        
        response = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'availability_data': availability_data,
            'data_source': 'SAP ERP - Supplier Management'
        }
        
        return response


class MockLIMSSystem:
    """
    Simulates Laboratory Information Management System responses.
    
    LIMS manages all laboratory test data, sample tracking, and quality control.
    In the lubricant R&D world, this includes viscosity tests, wear tests,
    oxidation stability, and dozens of other measurements.
    
    Our simulation includes 30+ years of TCAP Mumbai historical data to make
    recommendations more credible and realistic.
    """
    
    def __init__(self):
        self.system_name = "LIMS"
        
        # Sample historical formulation tests
        self.historical_tests = self._generate_historical_data()
    
    def _generate_historical_data(self) -> List[Dict[str, Any]]:
        """Generate realistic historical test data spanning 30+ years"""
        tests = []
        
        # Generate tests from 1995 to present
        for year in range(1995, 2025):
            # 50-100 tests per year
            num_tests = random.randint(50, 100)
            for i in range(num_tests):
                test_date = datetime(year, random.randint(1, 12), random.randint(1, 28))
                
                # Generate realistic test results
                test = {
                    'test_id': f'TCAP-{year}-{i:04d}',
                    'test_date': test_date.isoformat(),
                    'product_type': random.choice([
                        '5W-30', '10W-30', '15W-40', '20W-50',
                        '5W-40', '0W-20', '0W-30'
                    ]),
                    'base_oil_type': random.choice([
                        'Group I', 'Group II', 'Group III', 'PAO'
                    ]),
                    'viscosity_40c': random.uniform(40, 120),
                    'viscosity_100c': random.uniform(8, 18),
                    'viscosity_index': random.randint(100, 160),
                    'pour_point_c': random.randint(-35, -10),
                    'flash_point_c': random.randint(200, 240),
                    'tbn': random.uniform(6, 12),
                    'wear_scar_mm': random.uniform(0.3, 0.8),
                    'noack_volatility_pct': random.uniform(8, 15),
                    'performance_score': random.uniform(65, 95),
                    'cost_per_liter_inr': random.uniform(45, 180),
                    'passed_specs': random.random() > 0.25  # 75% pass rate
                }
                tests.append(test)
        
        return tests
    
    async def query_historical_tests(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query historical test data. This is like searching through decades of
        lab notebooks, but instant and structured.
        """
        await asyncio.sleep(random.uniform(0.08, 0.20))  # LIMS can be slower
        
        product_type = query_params.get('product_type')
        base_oil = query_params.get('base_oil_type')
        min_vi = query_params.get('min_viscosity_index', 0)
        
        # Filter tests based on criteria
        filtered_tests = self.historical_tests
        
        if product_type:
            filtered_tests = [t for t in filtered_tests if t['product_type'] == product_type]
        if base_oil:
            filtered_tests = [t for t in filtered_tests if t['base_oil_type'] == base_oil]
        if min_vi:
            filtered_tests = [t for t in filtered_tests if t['viscosity_index'] >= min_vi]
        
        # Get the most relevant/recent tests
        filtered_tests = sorted(filtered_tests, key=lambda x: x['test_date'], reverse=True)[:50]
        
        # Calculate statistics
        if filtered_tests:
            avg_vi = sum(t['viscosity_index'] for t in filtered_tests) / len(filtered_tests)
            avg_cost = sum(t['cost_per_liter_inr'] for t in filtered_tests) / len(filtered_tests)
            success_rate = sum(1 for t in filtered_tests if t['passed_specs']) / len(filtered_tests)
        else:
            avg_vi = avg_cost = success_rate = 0
        
        response = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'query_params': query_params,
            'tests_found': len(filtered_tests),
            'tests': filtered_tests[:10],  # Return top 10
            'statistics': {
                'average_viscosity_index': round(avg_vi, 1),
                'average_cost_per_liter': round(avg_cost, 2),
                'success_rate': round(success_rate, 3),
                'total_tests_in_database': len(self.historical_tests),
                'date_range': '1995-01-01 to 2025-01-31'
            },
            'data_source': 'TCAP Mumbai LIMS - 30+ years historical data'
        }
        
        return response
    
    async def get_test_protocols(self, test_type: str) -> Dict[str, Any]:
        """
        Retrieve standard test protocols from LIMS. Each test has specific
        procedures, equipment requirements, and acceptance criteria.
        """
        await asyncio.sleep(random.uniform(0.05, 0.12))
        
        protocols = {
            'viscosity': {
                'test_method': 'ASTM D445',
                'equipment': ['Automated Viscosity Bath', 'Capillary Viscometers'],
                'temperature_points': ['40°C', '100°C'],
                'sample_size_ml': 15,
                'test_duration_minutes': 45,
                'precision': '±0.5%'
            },
            'wear': {
                'test_method': 'ASTM D4172 (Four-Ball Wear Test)',
                'equipment': ['Four-Ball Wear Tester'],
                'test_conditions': '1200 rpm, 75°C, 1 hour',
                'load_kg': 40,
                'test_duration_minutes': 60,
                'acceptance_criteria': 'Wear scar < 0.6mm'
            },
            'oxidation': {
                'test_method': 'ASTM D943 (TOST)',
                'equipment': ['Turbine Oil Oxidation Stability Tester'],
                'test_temperature_c': 95,
                'test_duration_hours': 1000,
                'acceptance_criteria': 'TAN increase < 2.0 mgKOH/g'
            }
        }
        
        protocol = protocols.get(test_type, {})
        
        response = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'test_type': test_type,
            'protocol': protocol,
            'data_source': 'LIMS Protocol Library'
        }
        
        return response


class MockPLMSystem:
    """
    Simulates Product Lifecycle Management system (Siemens Teamcenter at TotalEnergies).
    
    PLM manages product specifications, bills of materials, version control, and
    change management. It's the single source of truth for product definitions.
    """
    
    def __init__(self):
        self.system_name = "PLM"
        
        # Product specifications
        self.product_specs = {
            '5W-30': {
                'product_code': 'QTZ-5W30-SN-001',
                'product_name': 'Quartz 9000 5W-30',
                'specification_version': 'v3.2',
                'target_properties': {
                    'viscosity_40c': {'min': 61.7, 'max': 70.0},
                    'viscosity_100c': {'min': 10.8, 'max': 12.5},
                    'viscosity_index': {'min': 150, 'max': None},
                    'pour_point_c': {'min': None, 'max': -35},
                    'flash_point_c': {'min': 220, 'max': None},
                    'tbn_fresh': {'min': 7.0, 'max': None}
                },
                'performance_standards': ['API SN Plus', 'ACEA C3', 'ILSAC GF-6A'],
                'oem_approvals': ['MB 229.52', 'VW 504.00/507.00', 'BMW LL-04'],
                'status': 'active',
                'last_updated': '2024-06-15'
            },
            '10W-40': {
                'product_code': 'HIX-10W40-SL-001',
                'product_name': 'Hi-Perf 10W-40',
                'specification_version': 'v2.8',
                'target_properties': {
                    'viscosity_40c': {'min': 95.0, 'max': 110.0},
                    'viscosity_100c': {'min': 14.0, 'max': 16.5},
                    'viscosity_index': {'min': 140, 'max': None},
                    'pour_point_c': {'min': None, 'max': -30},
                    'flash_point_c': {'min': 210, 'max': None}
                },
                'performance_standards': ['API SL', 'ACEA A3/B4'],
                'status': 'active',
                'last_updated': '2023-11-20'
            }
        }
    
    async def get_product_specification(self, product_type: str) -> Dict[str, Any]:
        """
        Retrieve official product specification from PLM. This is the master
        definition that R&D must meet.
        """
        await asyncio.sleep(random.uniform(0.06, 0.14))
        
        spec = self.product_specs.get(product_type, {})
        
        response = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'product_type': product_type,
            'specification': spec,
            'data_source': 'Siemens Teamcenter PLM'
        }
        
        return response
    
    async def create_bom(self, formulation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a Bill of Materials in PLM. This converts a formulation into
        a structured manufacturing document.
        """
        await asyncio.sleep(random.uniform(0.10, 0.25))
        
        bom_id = f"BOM-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        response = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'bom_id': bom_id,
            'product_code': formulation_data.get('product_code', 'TBD'),
            'version': '1.0',
            'status': 'draft',
            'approval_workflow_initiated': True,
            'estimated_approval_days': random.randint(5, 15),
            'data_source': 'Siemens Teamcenter PLM'
        }
        
        return response


class MockRegulatorySystem:
    """
    Simulates regulatory database queries for Indian and international standards.
    
    This includes BIS (Bureau of Indian Standards), PESO (Petroleum and Explosives
    Safety Organisation), API (American Petroleum Institute), and ACEA (European
    standards).
    """
    
    def __init__(self):
        self.system_name = "Regulatory_DB"
        
        # Regulatory requirements database
        self.standards = {
            'API SN Plus': {
                'issuing_body': 'American Petroleum Institute',
                'current_version': 'API 1509 (2020)',
                'applicable_to': 'Passenger car motor oils',
                'key_requirements': [
                    'LSPI (Low Speed Pre-Ignition) protection',
                    'Timing chain wear protection',
                    'Oxidation resistance',
                    'Deposit control'
                ],
                'mandatory_tests': [
                    'Sequence III timing chain wear',
                    'Sequence VH oxidation and wear',
                    'Sequence IX LSPI'
                ],
                'licensing_required': True,
                'license_fee_usd': 10000
            },
            'ACEA C3': {
                'issuing_body': 'European Automobile Manufacturers Association',
                'current_version': 'ACEA 2021',
                'applicable_to': 'Catalyst compatible oils',
                'key_requirements': [
                    'Mid SAPS (Sulfated Ash, Phosphorus, Sulfur)',
                    'Catalyst protection',
                    'High temperature stability',
                    'Fuel economy'
                ],
                'ash_limit_pct': 0.8,
                'phosphorus_limit_pct': 0.09,
                'sulfur_limit_pct': 0.3,
                'licensing_required': False
            },
            'BIS IS 13656': {
                'issuing_body': 'Bureau of Indian Standards',
                'current_version': 'IS 13656:2011 (Reaffirmed 2021)',
                'applicable_to': 'Internal combustion engine oils',
                'certification_required': True,
                'certification_process_days': 45,
                'certification_cost_inr': 25000,
                'renewal_years': 2
            }
        }
    
    async def check_compliance(self, formulation_data: Dict[str, Any], standards: List[str]) -> Dict[str, Any]:
        """
        Check if a formulation meets regulatory requirements. This simulates
        querying multiple regulatory databases and standards.
        """
        await asyncio.sleep(random.uniform(0.04, 0.10))  # External APIs are usually fast
        
        compliance_results = []
        
        for standard in standards:
            standard_info = self.standards.get(standard, {})
            
            # Simulate compliance check (in reality, this would be complex)
            is_compliant = random.random() > 0.15  # 85% pass rate
            
            result = {
                'standard': standard,
                'compliant': is_compliant,
                'standard_info': standard_info,
                'gaps_identified': [] if is_compliant else ['Requires additional testing'],
                'estimated_certification_time_days': standard_info.get('certification_process_days', 30)
            }
            compliance_results.append(result)
        
        overall_compliant = all(r['compliant'] for r in compliance_results)
        
        response = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'overall_compliant': overall_compliant,
            'standards_checked': len(standards),
            'compliance_results': compliance_results,
            'data_source': 'Multi-source Regulatory Database'
        }
        
        return response


class MockSupplierSystem:
    """
    Simulates supplier portal integration for real-time availability and pricing.
    
    In production, this would integrate with supplier EDI systems or B2B portals.
    For the demo, we simulate realistic supplier responses with market dynamics.
    """
    
    def __init__(self):
        self.system_name = "Supplier_Portal"
        
        self.suppliers = {
            'IndianOil Corporation': {
                'supplier_code': 'SUP-IOC-001',
                'rating': 4.5,
                'reliability_score': 0.92,
                'payment_terms': 'Net 45',
                'min_order_value_inr': 50000
            },
            'SK Lubricants': {
                'supplier_code': 'SUP-SKL-002',
                'rating': 4.7,
                'reliability_score': 0.95,
                'payment_terms': 'Net 60',
                'min_order_value_inr': 100000
            },
            'Lubrizol India': {
                'supplier_code': 'SUP-LUB-003',
                'rating': 4.8,
                'reliability_score': 0.97,
                'payment_terms': 'Net 30',
                'min_order_value_inr': 75000
            }
        }
    
    async def check_availability(self, materials: List[str]) -> Dict[str, Any]:
        """
        Check real-time availability from suppliers. In production, this might
        query multiple supplier systems simultaneously.
        """
        await asyncio.sleep(random.uniform(0.15, 0.30))  # External systems are slowest
        
        availability_data = []
        
        for material in materials:
            # Simulate availability
            is_available = random.random() > 0.10
            lead_time = random.randint(7, 21)
            price_change = random.uniform(-0.05, 0.10)  # -5% to +10%
            
            availability_data.append({
                'material': material,
                'available': is_available,
                'lead_time_days': lead_time,
                'price_trend': 'up' if price_change > 0 else 'down',
                'price_change_pct': round(price_change * 100, 1),
                'last_updated': datetime.now().isoformat()
            })
        
        response = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'materials_checked': len(materials),
            'availability_data': availability_data,
            'data_source': 'Integrated Supplier Portal'
        }
        
        return response


# Create singleton instances for use in the application
mock_sap = MockSAPSystem()
mock_lims = MockLIMSSystem()
mock_plm = MockPLMSystem()
mock_regulatory = MockRegulatorySystem()
mock_supplier = MockSupplierSystem()
