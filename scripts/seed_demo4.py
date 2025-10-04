"""
Seed Demo 4: Mobility Maestro with Realistic Indian EV Charging Data
"""
import sys
import os
import random
from datetime import datetime, timedelta, date

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db
from app.models.demo4_models import (
    ChargingSite, SiteEvaluation, NetworkConfiguration,
    DemandForecast, CityTier, NetworkPosition, SiteStatus
)
from app.models.demo4_extended_models import (
    TEPermit, TEGovernmentAgency, TEAgentActivity, TEEventTrace,
    TEScenario, TEChargingSession, TEStationStatus, TEGridMetrics,
    TEMarketTrends, TECompetitorAnalysis,
    PermitType, PermitStatus
)


# Realistic Indian Cities Data
CITIES_DATA = [
    # Tier 1 Cities
    {"city": "Mumbai", "state": "Maharashtra", "tier": CityTier.TIER_1, 
     "lat": 19.0760, "lng": 72.8777, "sites": 15, "avg_traffic": 25000, 
     "ev_penetration": 3.2, "population": 12442373, "avg_income": 1200000},
    
    {"city": "Delhi", "state": "Delhi", "tier": CityTier.TIER_1,
     "lat": 28.7041, "lng": 77.1025, "sites": 12, "avg_traffic": 22000,
     "ev_penetration": 2.8, "population": 11034555, "avg_income": 1150000},
    
    {"city": "Bengaluru", "state": "Karnataka", "tier": CityTier.TIER_1,
     "lat": 12.9716, "lng": 77.5946, "sites": 18, "avg_traffic": 20000,
     "ev_penetration": 4.1, "population": 8443675, "avg_income": 1300000},
    
    {"city": "Hyderabad", "state": "Telangana", "tier": CityTier.TIER_1,
     "lat": 17.3850, "lng": 78.4867, "sites": 12, "avg_traffic": 18000,
     "ev_penetration": 3.0, "population": 6809970, "avg_income": 1000000},
    
    {"city": "Chennai", "state": "Tamil Nadu", "tier": CityTier.TIER_1,
     "lat": 13.0827, "lng": 80.2707, "sites": 10, "avg_traffic": 19000,
     "ev_penetration": 2.5, "population": 7088000, "avg_income": 950000},
    
    # Tier 2 Cities
    {"city": "Pune", "state": "Maharashtra", "tier": CityTier.TIER_2,
     "lat": 18.5204, "lng": 73.8567, "sites": 10, "avg_traffic": 15000,
     "ev_penetration": 2.8, "population": 3124458, "avg_income": 900000},
    
    {"city": "Ahmedabad", "state": "Gujarat", "tier": CityTier.TIER_2,
     "lat": 23.0225, "lng": 72.5714, "sites": 8, "avg_traffic": 14000,
     "ev_penetration": 2.2, "population": 5577940, "avg_income": 850000},
    
    {"city": "Kolkata", "state": "West Bengal", "tier": CityTier.TIER_1,
     "lat": 22.5726, "lng": 88.3639, "sites": 8, "avg_traffic": 16000,
     "ev_penetration": 1.8, "population": 4496694, "avg_income": 800000},
    
    {"city": "Surat", "state": "Gujarat", "tier": CityTier.TIER_2,
     "lat": 21.1702, "lng": 72.8311, "sites": 6, "avg_traffic": 12000,
     "ev_penetration": 2.0, "population": 4467797, "avg_income": 750000},
    
    {"city": "Jaipur", "state": "Rajasthan", "tier": CityTier.TIER_2,
     "lat": 26.9124, "lng": 75.7873, "sites": 7, "avg_traffic": 11000,
     "ev_penetration": 1.9, "population": 3046163, "avg_income": 720000},
    
    {"city": "Lucknow", "state": "Uttar Pradesh", "tier": CityTier.TIER_2,
     "lat": 26.8467, "lng": 80.9462, "sites": 6, "avg_traffic": 10000,
     "ev_penetration": 1.5, "population": 2817105, "avg_income": 680000},
    
    {"city": "Kanpur", "state": "Uttar Pradesh", "tier": CityTier.TIER_2,
     "lat": 26.4499, "lng": 80.3319, "sites": 5, "avg_traffic": 9500,
     "ev_penetration": 1.3, "population": 2767348, "avg_income": 650000},
    
    # Tier 3 Cities
    {"city": "Indore", "state": "Madhya Pradesh", "tier": CityTier.TIER_3,
     "lat": 22.7196, "lng": 75.8577, "sites": 5, "avg_traffic": 8000,
     "ev_penetration": 1.2, "population": 1960631, "avg_income": 600000},
    
    {"city": "Chandigarh", "state": "Chandigarh", "tier": CityTier.TIER_3,
     "lat": 30.7333, "lng": 76.7794, "sites": 6, "avg_traffic": 7500,
     "ev_penetration": 2.5, "population": 1055450, "avg_income": 950000},
    
    {"city": "Kochi", "state": "Kerala", "tier": CityTier.TIER_2,
     "lat": 9.9312, "lng": 76.2673, "sites": 5, "avg_traffic": 7000,
     "ev_penetration": 2.8, "population": 677381, "avg_income": 780000},
    
    {"city": "Coimbatore", "state": "Tamil Nadu", "tier": CityTier.TIER_2,
     "lat": 11.0168, "lng": 76.9558, "sites": 4, "avg_traffic": 6500,
     "ev_penetration": 1.8, "population": 1061447, "avg_income": 700000},
]

# Highway Corridors
HIGHWAY_DATA = [
    {"name": "Mumbai-Pune Expressway", "state": "Maharashtra", "sites": 8,
     "start_lat": 19.0760, "start_lng": 72.8777, "end_lat": 18.5204, "end_lng": 73.8567},
    
    {"name": "Delhi-Jaipur Highway (NH48)", "state": "Multiple", "sites": 12,
     "start_lat": 28.7041, "start_lng": 77.1025, "end_lat": 26.9124, "end_lng": 75.7873},
    
    {"name": "Bengaluru-Mysuru Highway", "state": "Karnataka", "sites": 6,
     "start_lat": 12.9716, "start_lng": 77.5946, "end_lat": 12.2958, "end_lng": 76.6394},
    
    {"name": "Ahmedabad-Vadodara Expressway", "state": "Gujarat", "sites": 5,
     "start_lat": 23.0225, "start_lng": 72.5714, "end_lat": 22.3072, "end_lng": 73.1812},
    
    {"name": "Chennai-Bengaluru Highway", "state": "Multiple", "sites": 10,
     "start_lat": 13.0827, "start_lng": 80.2707, "end_lat": 12.9716, "end_lng": 77.5946},
]

# Competitor Networks
COMPETITORS = [
    {"name": "Tata Power EZ Charge", "stations": 450, "market_share": 25.5,
     "avg_price": 18.50, "cities": ["Mumbai", "Delhi", "Bengaluru", "Pune", "Hyderabad"]},
    
    {"name": "Fortum Charge & Drive", "stations": 280, "market_share": 15.2,
     "avg_price": 19.00, "cities": ["Delhi", "Bengaluru", "Chennai", "Hyderabad"]},
    
    {"name": "Ather Grid", "stations": 320, "market_share": 18.1,
     "avg_price": 17.80, "cities": ["Bengaluru", "Chennai", "Hyderabad", "Pune"]},
    
    {"name": "Magenta ChargeGrid", "stations": 200, "market_share": 11.3,
     "avg_price": 18.00, "cities": ["Delhi", "Mumbai", "Pune", "Ahmedabad"]},
    
    {"name": "ChargeZone", "stations": 150, "market_share": 8.5,
     "avg_price": 17.50, "cities": ["Bengaluru", "Hyderabad", "Chennai"]},
]


def seed_demo4():
    """Main seed function"""
    print("🚀 Starting Demo 4 Seeding...")
    
    # Clear existing data
    print("Clearing existing data...")
    clear_demo4_data()
    
    # Seed in order
    print("\n1️⃣ Seeding Government Agencies...")
    seed_government_agencies()
    
    print("\n2️⃣ Seeding Charging Sites...")
    seed_charging_sites()
    
    print("\n3️⃣ Seeding Site Evaluations...")
    seed_site_evaluations()
    
    print("\n4️⃣ Seeding Permits...")
    seed_permits()
    
    print("\n5️⃣ Seeding Market Trends...")
    seed_market_trends()
    
    print("\n6️⃣ Seeding Competitor Analysis...")
    seed_competitor_analysis()
    
    print("\n7️⃣ Seeding Scenarios...")
    seed_scenarios()
    
    print("\n8️⃣ Seeding Operational Data...")
    seed_operational_data()
    
    print("\n9️⃣ Seeding Network Configurations...")
    seed_network_configurations()
    
    print("\n✅ Demo 4 Seeding Complete!")
    print_summary_stats()


def clear_demo4_data():
    """Clear existing Demo 4 data"""
    TEEventTrace.query.delete()
    TEAgentActivity.query.delete()
    TEChargingSession.query.delete()
    TEStationStatus.query.delete()
    TEGridMetrics.query.delete()
    TEPermit.query.delete()
    DemandForecast.query.delete()
    NetworkConfiguration.query.delete()
    SiteEvaluation.query.delete()
    ChargingSite.query.delete()
    TEMarketTrends.query.delete()
    TECompetitorAnalysis.query.delete()
    TEScenario.query.delete()
    TEGovernmentAgency.query.delete()
    db.session.commit()


def seed_government_agencies():
    """Seed government agencies for permit processing"""
    agencies = [
        # Maharashtra
        {"name": "Municipal Corporation of Greater Mumbai (MCGM)", "type": "municipal",
         "state": "Maharashtra", "url": "https://portal.mcgm.gov.in",
         "avg_days": 45, "digital": True, "approval_rate": 78.5},
        
        {"name": "Maharashtra State Pollution Control Board", "type": "state",
         "state": "Maharashtra", "url": "https://mpcb.gov.in",
         "avg_days": 60, "digital": True, "approval_rate": 82.3},
        
        {"name": "Maharashtra State Electricity Distribution Co. (MSEDCL)", "type": "state",
         "state": "Maharashtra", "url": "https://www.mahadiscom.in",
         "avg_days": 30, "digital": True, "approval_rate": 91.2},
        
        # Karnataka
        {"name": "Bruhat Bengaluru Mahanagara Palike (BBMP)", "type": "municipal",
         "state": "Karnataka", "url": "https://bbmp.gov.in",
         "avg_days": 50, "digital": True, "approval_rate": 75.8},
        
        {"name": "Karnataka State Pollution Control Board", "type": "state",
         "state": "Karnataka", "url": "https://kspcb.gov.in",
         "avg_days": 55, "digital": False, "approval_rate": 79.1},
        
        {"name": "Bangalore Electricity Supply Company (BESCOM)", "type": "state",
         "state": "Karnataka", "url": "https://bescom.org",
         "avg_days": 35, "digital": True, "approval_rate": 88.5},
        
        # Delhi
        {"name": "New Delhi Municipal Council (NDMC)", "type": "municipal",
         "state": "Delhi", "url": "https://ndmc.gov.in",
         "avg_days": 40, "digital": True, "approval_rate": 84.2},
        
        {"name": "Delhi Pollution Control Committee", "type": "state",
         "state": "Delhi", "url": "https://dpcc.delhigovt.nic.in",
         "avg_days": 50, "digital": True, "approval_rate": 81.7},
        
        {"name": "BSES Rajdhani Power Limited", "type": "state",
         "state": "Delhi", "url": "https://www.bsesdelhi.com",
         "avg_days": 28, "digital": True, "approval_rate": 92.5},
        
        # Central Agencies
        {"name": "Petroleum and Explosives Safety Organisation (PESO)", "type": "central",
         "state": "All India", "url": "https://peso.gov.in",
         "avg_days": 90, "digital": False, "approval_rate": 88.9},
        
        {"name": "Central Electricity Authority (CEA)", "type": "central",
         "state": "All India", "url": "https://cea.nic.in",
         "avg_days": 75, "digital": True, "approval_rate": 85.3},
        
        {"name": "Bureau of Indian Standards (BIS)", "type": "central",
         "state": "All India", "url": "https://bis.gov.in",
         "avg_days": 120, "digital": True, "approval_rate": 90.1},
    ]
    
    for agency_data in agencies:
        agency = TEGovernmentAgency(
            agency_name=agency_data["name"],
            agency_type=agency_data["type"],
            state=agency_data["state"],
            portal_url=agency_data["url"],
            avg_processing_days=agency_data["avg_days"],
            digital_submission=agency_data["digital"],
            approval_rate=agency_data["approval_rate"]
        )
        db.session.add(agency)
    
    db.session.commit()
    print(f"   ✓ Created {len(agencies)} government agencies")


def seed_charging_sites():
    """Seed charging sites across Indian cities and highways"""
    site_count = 0
    
    # City sites
    for city_data in CITIES_DATA:
        for i in range(city_data["sites"]):
            # Generate location with small random offset
            lat_offset = random.uniform(-0.05, 0.05)
            lng_offset = random.uniform(-0.05, 0.05)
            
            # Determine network position
            if random.random() < 0.7:
                position = NetworkPosition.URBAN
            else:
                position = NetworkPosition.SUBURBAN
            
            site = ChargingSite(
                site_id=f"{city_data['city'][:3].upper()}-{i+1:03d}",
                city=city_data["city"],
                state=city_data["state"],
                latitude=city_data["lat"] + lat_offset,
                longitude=city_data["lng"] + lng_offset,
                city_tier=city_data["tier"],
                network_position=position,
                
                # Site characteristics
                land_area_sqm=random.uniform(200, 500),
                land_cost_inr=random.uniform(5000000, 15000000),
                grid_connection_available=random.random() > 0.1,
                grid_capacity_kw=random.choice([250, 500, 750, 1000]),
                
                # Demographics
                population_density=city_data["population"] / 500,  # Simplified
                avg_household_income=city_data["avg_income"] * random.uniform(0.8, 1.2),
                ev_penetration_rate=city_data["ev_penetration"] * random.uniform(0.8, 1.3),
                
                # Traffic & Demand
                daily_traffic_count=city_data["avg_traffic"] * random.uniform(0.7, 1.3),
                estimated_daily_sessions=int(city_data["avg_traffic"] * city_data["ev_penetration"] / 100 * 0.15),
                peak_hour_demand=random.uniform(50, 150),
                
                # Competition
                existing_chargers_within_5km=random.randint(0, 5),
                nearest_competitor_distance_km=random.uniform(0.5, 8.0),
                
                status=SiteStatus.CANDIDATE
            )
            db.session.add(site)
            site_count += 1
    
    # Highway sites
    for highway_data in HIGHWAY_DATA:
        for i in range(highway_data["sites"]):
            # Interpolate between start and end points
            t = i / highway_data["sites"]
            lat = highway_data["start_lat"] + t * (highway_data["end_lat"] - highway_data["start_lat"])
            lng = highway_data["start_lng"] + t * (highway_data["end_lng"] - highway_data["start_lng"])
            
            site = ChargingSite(
                site_id=f"HW-{highway_data['name'][:3].upper()}-{i+1:03d}",
                city=highway_data["name"],
                state=highway_data["state"],
                latitude=lat + random.uniform(-0.01, 0.01),
                longitude=lng + random.uniform(-0.01, 0.01),
                city_tier=CityTier.TIER_2,
                network_position=NetworkPosition.HIGHWAY,
                
                land_area_sqm=random.uniform(300, 800),
                land_cost_inr=random.uniform(3000000, 8000000),
                grid_connection_available=random.random() > 0.2,
                grid_capacity_kw=random.choice([500, 750, 1000]),
                
                population_density=random.uniform(100, 500),
                avg_household_income=random.uniform(600000, 900000),
                ev_penetration_rate=random.uniform(1.5, 3.0),
                
                daily_traffic_count=random.randint(8000, 15000),
                estimated_daily_sessions=random.randint(50, 150),
                peak_hour_demand=random.uniform(100, 250),
                
                existing_chargers_within_5km=random.randint(0, 2),
                nearest_competitor_distance_km=random.uniform(5.0, 25.0),
                
                status=SiteStatus.CANDIDATE
            )
            db.session.add(site)
            site_count += 1
    
    db.session.commit()
    print(f"   ✓ Created {site_count} charging sites")


def seed_site_evaluations():
    """Seed site evaluations for a subset of sites"""
    sites = ChargingSite.query.limit(80).all()  # Evaluate 80% of sites
    
    for site in sites:
        # Calculate scores based on site characteristics
        traffic_score = min(100, (site.daily_traffic_count / 10000) * 100)
        demographics_score = min(100, (site.avg_household_income / 1500000) * 50 + 
                                      (site.ev_penetration_rate / 5) * 50)
        grid_score = 100 if site.grid_connection_available else 50
        competition_score = max(0, 100 - (site.existing_chargers_within_5km * 15))
        accessibility_score = random.uniform(70, 95)
        
        overall_score = (traffic_score * 0.30 + demographics_score * 0.25 + 
                        grid_score * 0.20 + competition_score * 0.15 + 
                        accessibility_score * 0.10)
        
        # Financial projections
        capex = random.uniform(2500000, 3500000)
        opex_annual = random.uniform(400000, 600000)
        daily_sessions = site.estimated_daily_sessions or random.randint(30, 100)
        revenue_year1 = daily_sessions * 365 * 250 * 0.7
        revenue_year5 = revenue_year1 * 1.5
        
        # NPV calculation
        discount_rate = 0.12
        years = 7
        total_cf = sum((revenue_year1 * (1.08 ** year) - opex_annual) / 
                      ((1 + discount_rate) ** (year + 1)) for year in range(years))
        npv = total_cf - capex
        irr = ((total_cf / capex) ** (1 / years) - 1) * 100
        
        # Recommendation
        if overall_score >= 80 and npv > 5000000:
            recommendation = 'strong_select'
        elif overall_score >= 65 and npv > 2000000:
            recommendation = 'select'
        elif overall_score >= 50:
            recommendation = 'consider'
        else:
            recommendation = 'reject'
        
        evaluation = SiteEvaluation(
            site_id=site.id,
            traffic_score=traffic_score,
            demographics_score=demographics_score,
            grid_infrastructure_score=grid_score,
            competition_score=competition_score,
            accessibility_score=accessibility_score,
            overall_score=overall_score,
            
            capex_inr=capex,
            opex_annual_inr=opex_annual,
            revenue_year1_inr=revenue_year1,
            revenue_year5_inr=revenue_year5,
            npv_inr=npv,
            irr_percentage=irr,
            payback_years=capex / (revenue_year1 - opex_annual) if revenue_year1 > opex_annual else 10,
            
            evaluated_by_agent='network-optimizer-001',
            confidence_score=random.uniform(0.82, 0.95),
            reasoning=f"Site evaluation for {site.city}",
            recommendation=recommendation,
            risk_factors=["Competition risk"] if competition_score < 60 else [],
            opportunities=["First mover advantage"] if competition_score > 80 else []
        )
        db.session.add(evaluation)
        
        # Update site status
        site.status = SiteStatus.EVALUATED
    
    db.session.commit()
    print(f"   ✓ Created {len(sites)} site evaluations")


def seed_permits():
    """Seed permit applications"""
    evaluated_sites = ChargingSite.query.filter_by(status=SiteStatus.EVALUATED).limit(30).all()
    
    permit_count = 0
    for site in evaluated_sites:
        # Create multiple permits per site
        permit_types = [PermitType.LAND_USE, PermitType.ENVIRONMENTAL, 
                       PermitType.FIRE_SAFETY, PermitType.ELECTRICAL]
        
        for permit_type in permit_types:
            # Get appropriate agency
            if site.state == "Maharashtra":
                if permit_type == PermitType.LAND_USE:
                    agency_name = "Municipal Corporation of Greater Mumbai (MCGM)"
                elif permit_type == PermitType.ENVIRONMENTAL:
                    agency_name = "Maharashtra State Pollution Control Board"
                else:
                    agency_name = "Maharashtra State Electricity Distribution Co. (MSEDCL)"
            elif site.state == "Karnataka":
                if permit_type == PermitType.LAND_USE:
                    agency_name = "Bruhat Bengaluru Mahanagara Palike (BBMP)"
                else:
                    agency_name = "Karnataka State Pollution Control Board"
            else:
                agency_name = "New Delhi Municipal Council (NDMC)"
            
            # Random status
            status = random.choice([
                PermitStatus.SUBMITTED,
                PermitStatus.UNDER_REVIEW,
                PermitStatus.APPROVED,
                PermitStatus.ADDITIONAL_INFO_REQUIRED
            ])
            
            submitted_date = datetime.now().date() - timedelta(days=random.randint(10, 120))
            expected_approval = submitted_date + timedelta(days=random.randint(30, 90))
            
            permit = TEPermit(
                site_id=site.id,
                permit_type=permit_type,
                permit_number=f"P-{site.site_id}-{permit_type.value[:3].upper()}-{random.randint(1000, 9999)}",
                agency_name=agency_name,
                agency_state=site.state,
                status=status,
                submitted_date=submitted_date,
                expected_approval_date=expected_approval,
                processing_days_estimated=random.randint(30, 90),
                application_fee_inr=random.uniform(5000, 25000),
                managed_by_agent='permit-manager-001'
            )
            
            if status == PermitStatus.APPROVED:
                permit.actual_approval_date = submitted_date + timedelta(days=random.randint(25, 80))
                permit.processing_days_actual = (permit.actual_approval_date - submitted_date).days
            
            db.session.add(permit)
            permit_count += 1
    
    db.session.commit()
    print(f"   ✓ Created {permit_count} permit applications")


def seed_market_trends():
    """Seed market trends for cities"""
    for city_data in CITIES_DATA:
        trend = TEMarketTrends(
            city=city_data["city"],
            state=city_data["state"],
            total_ev_registrations=int(city_data["population"] * city_data["ev_penetration"] / 100),
            monthly_ev_registrations=int(city_data["population"] * city_data["ev_penetration"] / 100 / 12),
            ev_growth_rate=random.uniform(15, 45),
            total_vehicles=int(city_data["population"] * 0.25),
            ev_penetration_rate=city_data["ev_penetration"],
            avg_household_income=city_data["avg_income"],
            population=city_data["population"],
            existing_charging_stations=random.randint(20, 150),
            public_chargers=random.randint(100, 800),
            private_chargers=random.randint(500, 3000),
            forecasted_ev_count_1yr=int(city_data["population"] * city_data["ev_penetration"] / 100 * 1.3),
            forecasted_ev_count_3yr=int(city_data["population"] * city_data["ev_penetration"] / 100 * 2.0),
            forecasted_ev_count_5yr=int(city_data["population"] * city_data["ev_penetration"] / 100 * 3.5),
            data_source="VAHAN Database + Census 2021",
            data_date=date.today()
        )
        db.session.add(trend)
    
    db.session.commit()
    print(f"   ✓ Created market trends for {len(CITIES_DATA)} cities")


def seed_competitor_analysis():
    """Seed competitor analysis"""
    for comp in COMPETITORS:
        analysis = TECompetitorAnalysis(
            competitor_name=comp["name"],
            total_stations=comp["stations"],
            cities_present=comp["cities"],
            estimated_market_share=comp["market_share"],
            pricing_strategy="Dynamic pricing" if random.random() > 0.5 else "Fixed pricing",
            avg_price_inr_kwh=comp["avg_price"],
            strengths=["Wide network", "Brand recognition"],
            weaknesses=["Limited highway presence"],
            analysis_date=date.today(),
            analyzed_by_agent='market-intelligence-001'
        )
        db.session.add(analysis)
    
    db.session.commit()
    print(f"   ✓ Created competitor analysis for {len(COMPETITORS)} competitors")


def seed_scenarios():
    """Seed pre-defined scenarios"""
    scenarios = [
        {
            "name": "Mumbai Metro Line 3 - EV Charging Opportunity",
            "type": "expansion",
            "description": "Evaluate 15 sites near new Mumbai Metro Line 3 stations for EV charging network expansion",
            "city": "Mumbai",
            "state": "Maharashtra",
            "site_count": 15,
            "agents": ["GeographicIntelligence", "MarketIntelligence", "Financial", "Permit"],
            "systems": ["VAHAN_API", "Census_DB", "MumbaiMunicipal", "MSEDCL", "TotalEnergies_ERP"],
            "flow": [
                {"from": "UI", "to": "Orchestrator", "event": "expansion_request", "delay": 300},
                {"from": "Orchestrator", "to": "GeographicIntelligence", "event": "analyze_sites", "delay": 500},
                {"from": "GeographicIntelligence", "to": "VAHAN_API", "event": "fetch_ev_data", "delay": 800},
                {"from": "GeographicIntelligence", "to": "Census_DB", "event": "fetch_demographics", "delay": 600},
                {"from": "MarketIntelligence", "to": "CompetitorDB", "event": "analyze_competition", "delay": 700},
                {"from": "Financial", "to": "TotalEnergies_ERP", "event": "budget_check", "delay": 400},
                {"from": "Permit", "to": "MumbaiMunicipal", "event": "check_permits", "delay": 900},
                {"from": "Orchestrator", "to": "UI", "event": "recommendations_ready", "delay": 500}
            ],
            "duration": 4800,
            "difficulty": "medium"
        },
        {
            "name": "Delhi-Jaipur Highway - Fast Charging Network",
            "type": "optimization",
            "description": "Optimize 50 candidate sites along 280km Delhi-Jaipur highway for maximum coverage",
            "city": "Multiple",
            "state": "Multiple",
            "site_count": 50,
            "agents": ["NetworkEvaluation", "Geographic", "Financial", "Operations"],
            "systems": ["GIS_System", "GridCapacity", "TrafficAnalysis", "TotalEnergies_ERP"],
            "flow": [
                {"from": "UI", "to": "Orchestrator", "event": "optimization_request", "delay": 300},
                {"from": "NetworkEvaluation", "to": "GIS_System", "event": "spatial_analysis", "delay": 1200},
                {"from": "Geographic", "to": "TrafficAnalysis", "event": "highway_traffic_data", "delay": 900},
                {"from": "Financial", "to": "TotalEnergies_ERP", "event": "capex_analysis", "delay": 700},
                {"from": "Operations", "to": "GridCapacity", "event": "grid_availability", "delay": 800},
                {"from": "NetworkEvaluation", "to": "Optimization_Engine", "event": "run_optimization", "delay": 2000},
                {"from": "Orchestrator", "to": "UI", "event": "optimal_configuration", "delay": 500}
            ],
            "duration": 6400,
            "difficulty": "hard"
        },
        {
            "name": "Bengaluru Permit Crisis - Multi-Agency Resolution",
            "type": "crisis",
            "description": "Track and resolve permit delays across 6 government agencies for 10 Bengaluru sites",
            "city": "Bengaluru",
            "state": "Karnataka",
            "site_count": 10,
            "agents": ["PermitManagement", "Regulatory", "Operations"],
            "systems": ["BBMP", "BESCOM", "KSPCB", "FireDept", "BuildingDept", "SingleWindow"],
            "flow": [
                {"from": "UI", "to": "Orchestrator", "event": "permit_crisis", "delay": 200},
                {"from": "PermitManagement", "to": "BBMP", "event": "land_use_status", "delay": 600},
                {"from": "PermitManagement", "to": "BESCOM", "event": "grid_connection_status", "delay": 700},
                {"from": "PermitManagement", "to": "KSPCB", "event": "environmental_clearance", "delay": 800},
                {"from": "Regulatory", "to": "SingleWindow", "event": "escalation_request", "delay": 1000},
                {"from": "Operations", "to": "FollowUp_System", "event": "automated_followup", "delay": 500},
                {"from": "Orchestrator", "to": "UI", "event": "resolution_plan", "delay": 400}
            ],
            "duration": 4200,
            "difficulty": "hard"
        },
        {
            "name": "Chennai Heat Wave - Grid Load Management",
            "type": "crisis",
            "description": "Real-time load balancing across 30 Chennai stations during extreme heat wave",
            "city": "Chennai",
            "state": "Tamil Nadu",
            "site_count": 30,
            "agents": ["Operations", "Network", "Financial"],
            "systems": ["GridMonitoring", "StationIoT", "PricingEngine", "CustomerApp"],
            "flow": [
                {"from": "GridMonitoring", "to": "Orchestrator", "event": "grid_overload_alert", "delay": 100},
                {"from": "Operations", "to": "StationIoT", "event": "current_load_query", "delay": 300},
                {"from": "Network", "to": "LoadBalancer", "event": "redistribute_load", "delay": 600},
                {"from": "Financial", "to": "PricingEngine", "event": "dynamic_pricing", "delay": 400},
                {"from": "Operations", "to": "CustomerApp", "event": "customer_notification", "delay": 500},
                {"from": "Orchestrator", "to": "UI", "event": "crisis_mitigated", "delay": 300}
            ],
            "duration": 2200,
            "difficulty": "medium"
        }
    ]
    
    for scenario_data in scenarios:
        scenario = TEScenario(
            scenario_name=scenario_data["name"],
            scenario_type=scenario_data["type"],
            description=scenario_data["description"],
            target_city=scenario_data["city"],
            target_state=scenario_data["state"],
            site_count=scenario_data["site_count"],
            agents_involved=scenario_data["agents"],
            systems_involved=scenario_data["systems"],
            event_flow=scenario_data["flow"],
            expected_duration_ms=scenario_data["duration"],
            difficulty_level=scenario_data["difficulty"],
            is_active=True
        )
        db.session.add(scenario)
    
    db.session.commit()
    print(f"   ✓ Created {len(scenarios)} scenarios")


def seed_operational_data():
    """Seed operational data for evaluated sites"""
    operational_sites = ChargingSite.query.filter_by(status=SiteStatus.EVALUATED).limit(20).all()
    
    session_count = 0
    for site in operational_sites:
        # Create station status
        status = TEStationStatus(
            site_id=site.id,
            is_operational=random.random() > 0.1,
            total_chargers=random.choice([4, 6, 8, 10]),
            available_chargers=random.randint(1, 6),
            in_use_chargers=random.randint(1, 4),
            faulty_chargers=random.randint(0, 1),
            current_load_kw=random.uniform(50, 300),
            max_capacity_kw=site.grid_capacity_kw or 500,
            utilization_percentage=random.uniform(40, 85),
            grid_voltage_v=random.uniform(395, 415),
            grid_frequency_hz=random.uniform(49.8, 50.2),
            grid_connection_status="connected",
            temperature_celsius=random.uniform(25, 42),
            last_heartbeat=datetime.now()
        )
        db.session.add(status)
        
        # Create charging sessions
        for _ in range(random.randint(5, 15)):
            start = datetime.now() - timedelta(hours=random.randint(1, 168))
            duration = random.randint(20, 180)
            energy = random.uniform(10, 60)
            
            session = TEChargingSession(
                site_id=site.id,
                session_id=f"CS-{site.site_id}-{random.randint(10000, 99999)}",
                start_time=start,
                end_time=start + timedelta(minutes=duration),
                duration_minutes=duration,
                energy_delivered_kwh=energy,
                peak_power_kw=random.uniform(50, 150),
                battery_soc_start=random.uniform(10, 30),
                battery_soc_end=random.uniform(70, 95),
                price_per_kwh=random.uniform(16, 22),
                total_amount_inr=energy * random.uniform(16, 22),
                payment_method=random.choice(["UPI", "Card", "Wallet"]),
                vehicle_type=random.choice(["Sedan", "SUV", "Two-Wheeler"]),
                connector_type=random.choice(["CCS2", "CHAdeMO", "Type 2"])
            )
            db.session.add(session)
            session_count += 1
        
        # Create grid metrics
        grid_metrics = TEGridMetrics(
            site_id=site.id,
            connection_capacity_kw=site.grid_capacity_kw or 500,
            transformer_capacity_kva=random.uniform(500, 1000),
            peak_demand_kw=random.uniform(200, 400),
            average_demand_kw=random.uniform(100, 250),
            power_factor=random.uniform(0.90, 0.98),
            electricity_rate_inr_kwh=random.uniform(7, 12),
            demand_charge_inr_kw=random.uniform(150, 250),
            uptime_percentage=random.uniform(95, 99.9),
            outage_count=random.randint(0, 3),
            metric_date=date.today()
        )
        db.session.add(grid_metrics)
    
    db.session.commit()
    print(f"   ✓ Created operational data: {len(operational_sites)} stations, {session_count} sessions")


def seed_network_configurations():
    """Seed sample network configurations"""
    evaluated_sites = SiteEvaluation.query.filter(
        SiteEvaluation.recommendation.in_(['strong_select', 'select'])
    ).all()
    
    if len(evaluated_sites) < 20:
        print("   ⚠ Not enough evaluated sites for network configurations")
        return
    
    # Create 3 sample configurations
    configs = [
        {
            "name": "Phase 1: Tier 1 Cities Expansion",
            "description": "Focus on Mumbai, Delhi, Bengaluru with 30 high-ROI sites",
            "budget": 100000000,
            "target": 30
        },
        {
            "name": "Phase 2: Highway Corridors",
            "description": "Strategic highway sites for intercity travel",
            "budget": 50000000,
            "target": 20
        },
        {
            "name": "Balanced National Network",
            "description": "Mix of urban and highway sites across India",
            "budget": 150000000,
            "target": 50
        }
    ]
    
    for config_data in configs:
        # Select top sites
        sorted_sites = sorted(evaluated_sites, 
                            key=lambda x: (x.overall_score, x.npv_inr), 
                            reverse=True)[:config_data["target"]]
        
        selected_ids = [e.site.site_id for e in sorted_sites]
        total_capex = sum(e.capex_inr for e in sorted_sites)
        total_revenue = sum(e.revenue_year1_inr for e in sorted_sites)
        avg_npv = sum(e.npv_inr for e in sorted_sites) / len(sorted_sites)
        
        config = NetworkConfiguration(
            config_name=config_data["name"],
            description=config_data["description"],
            total_budget_inr=config_data["budget"],
            target_sites_count=config_data["target"],
            selected_site_ids=selected_ids,
            total_capex_inr=total_capex,
            total_annual_revenue_inr=total_revenue,
            network_coverage_percentage=random.uniform(65, 85),
            population_served=random.randint(5000000, 15000000),
            optimization_objective="balanced",
            optimization_algorithm="multi_criteria_optimization",
            optimization_time_ms=random.randint(500, 2000),
            network_npv_inr=avg_npv * len(sorted_sites),
            network_irr_percentage=random.uniform(18, 28),
            optimized_by_agent='network-optimizer-001'
        )
        db.session.add(config)
    
    db.session.commit()
    print(f"   ✓ Created {len(configs)} network configurations")


def print_summary_stats():
    """Print summary statistics"""
    print("\n" + "="*60)
    print("📊 DEMO 4 DATABASE SUMMARY")
    print("="*60)
    print(f"🏢 Government Agencies: {TEGovernmentAgency.query.count()}")
    print(f"📍 Charging Sites: {ChargingSite.query.count()}")
    print(f"   ├─ Tier 1: {ChargingSite.query.filter_by(city_tier=CityTier.TIER_1).count()}")
    print(f"   ├─ Tier 2: {ChargingSite.query.filter_by(city_tier=CityTier.TIER_2).count()}")
    print(f"   ├─ Tier 3: {ChargingSite.query.filter_by(city_tier=CityTier.TIER_3).count()}")
    print(f"   ├─ Urban: {ChargingSite.query.filter_by(network_position=NetworkPosition.URBAN).count()}")
    print(f"   ├─ Highway: {ChargingSite.query.filter_by(network_position=NetworkPosition.HIGHWAY).count()}")
    print(f"   └─ Suburban: {ChargingSite.query.filter_by(network_position=NetworkPosition.SUBURBAN).count()}")
    print(f"⭐ Site Evaluations: {SiteEvaluation.query.count()}")
    print(f"   ├─ Strong Select: {SiteEvaluation.query.filter_by(recommendation='strong_select').count()}")
    print(f"   ├─ Select: {SiteEvaluation.query.filter_by(recommendation='select').count()}")
    print(f"   ├─ Consider: {SiteEvaluation.query.filter_by(recommendation='consider').count()}")
    print(f"   └─ Reject: {SiteEvaluation.query.filter_by(recommendation='reject').count()}")
    print(f"📋 Permits: {TEPermit.query.count()}")
    print(f"   ├─ Approved: {TEPermit.query.filter_by(status=PermitStatus.APPROVED).count()}")
    print(f"   ├─ Under Review: {TEPermit.query.filter_by(status=PermitStatus.UNDER_REVIEW).count()}")
    print(f"   └─ Submitted: {TEPermit.query.filter_by(status=PermitStatus.SUBMITTED).count()}")
    print(f"📈 Market Trends: {TEMarketTrends.query.count()} cities")
    print(f"🏆 Competitor Analysis: {TECompetitorAnalysis.query.count()} competitors")
    print(f"🎬 Scenarios: {TEScenario.query.count()}")
    print(f"⚡ Charging Sessions: {TEChargingSession.query.count()}")
    print(f"🔌 Station Status: {TEStationStatus.query.count()}")
    print(f"🌐 Network Configurations: {NetworkConfiguration.query.count()}")
    print("="*60)


if __name__ == '__main__':
    from app import create_app
    app = create_app()
    with app.app_context():
        seed_demo4()
