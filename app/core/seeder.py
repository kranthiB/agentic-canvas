"""
Database Seeding Script
Populate database with realistic mock data for all demos
"""
import random
from datetime import datetime, timedelta
from faker import Faker
import logging

from app import db
from app.models.user import User
from app.models.demo1_models import CarbonBudget, EmissionReading, CarbonAction, ActionType, EmissionStatus
from app.models.demo2_models import PlantState, AgentDecision, AgentType, PlantStatus
from app.models.demo3_models import PermitToWork, GasSensorReading, PermitType, PermitStatus, RiskLevel, AlertLevel
from app.models.demo4_models import ChargingSite, SiteEvaluation, CityTier, NetworkPosition, SiteStatus
from app.models.demo5_models import (
    ResearchPaper, FormulationTrial, FormulationRequest,
    DocumentType, TrialStatus
)

logger = logging.getLogger(__name__)
fake = Faker('en_IN')


def seed_users():
    """Seed default users"""
    logger.info("Seeding users...")
    
    users_data = [
        {'username': 'demo', 'email': 'demo@totalenergies.com', 'password': 'demo', 'role': 'admin'},
        {'username': 'engineer', 'email': 'engineer@totalenergies.com', 'password': 'engineer123', 'role': 'engineer'},
        {'username': 'operator', 'email': 'operator@totalenergies.com', 'password': 'operator123', 'role': 'operator'},
    ]
    
    for user_data in users_data:
        if not User.query.filter_by(username=user_data['username']).first():
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                role=user_data['role']
            )
            user.set_password(user_data['password'])
            db.session.add(user)
    
    db.session.commit()
    logger.info("Users seeded successfully")


def seed_demo1_carbon():
    """Seed Demo 1 - Carbon Compass data"""
    logger.info("Seeding Demo 1 - Carbon Compass...")
    
    # Create current year budget
    current_year = datetime.now().year
    if not CarbonBudget.query.filter_by(year=current_year).first():
        budget = CarbonBudget(
            year=current_year,
            total_budget_mt=100000,
            consumed_mt=45234.56,
            remaining_mt=54765.44,
            status=EmissionStatus.NORMAL
        )
        db.session.add(budget)
        db.session.commit()
        
        # Create emission readings (last 48 hours)
        for i in range(48):
            reading = EmissionReading(
                budget_id=budget.id,
                emissions_rate_kg_hr=random.uniform(200, 300),
                production_rate=random.uniform(900, 1000),
                intensity=random.uniform(0.2, 0.3),
                facility='Refinery Unit 1',
                unit='CDU',
                status=EmissionStatus.NORMAL,
                created_at=datetime.now() - timedelta(hours=48-i)
            )
            db.session.add(reading)
        
        # Create some actions
        action_types = [ActionType.OPTIMIZE_PROCESS, ActionType.REDUCE_RATE, ActionType.SWITCH_FUEL]
        for i, action_type in enumerate(action_types):
            action = CarbonAction(
                budget_id=budget.id,
                action_type=action_type,
                description=f"Action {i+1}: {action_type.value.replace('_', ' ').title()}",
                expected_reduction_kg_hr=random.uniform(10, 50),
                expected_cost=random.uniform(30000, 150000),
                reasoning="AI-recommended action based on current conditions",
                confidence_score=random.uniform(0.8, 0.95),
                agent_id='carbon-optimizer-001',
                priority=i+1,
                implemented=(i == 0)
            )
            db.session.add(action)
        
        db.session.commit()
    
    logger.info("Demo 1 seeded successfully")


def seed_demo2_grid():
    """Seed Demo 2 - GridMind AI data"""
    logger.info("Seeding Demo 2 - GridMind AI...")
    
    # Create plant states (last 24 hours)
    for i in range(24):
        hour = i
        solar_factor = max(0, 0.8 * (1 - abs((hour - 12) / 12)))
        
        state = PlantState(
            solar_generation_mw=20000 * solar_factor + random.uniform(-1000, 1000),
            wind_generation_mw=random.uniform(8000, 11000),
            total_generation_mw=0,
            battery_soc=random.uniform(0.5, 0.8),
            battery_power_mw=random.uniform(-1000, 1000),
            grid_frequency_hz=50.0 + random.gauss(0, 0.05),
            market_price_inr_mwh=random.uniform(2800, 3800),
            status=PlantStatus.NORMAL,
            created_at=datetime.now() - timedelta(hours=24-i)
        )
        state.total_generation_mw = state.solar_generation_mw + state.wind_generation_mw
        db.session.add(state)
    
    db.session.commit()
    logger.info("Demo 2 seeded successfully")


def seed_demo3_safety():
    """Seed Demo 3 - Safety Guardian data"""
    logger.info("Seeding Demo 3 - Safety Guardian...")
    
    areas = ['CDU', 'FCC', 'Hydrocracker', 'Storage', 'Loading', 'Utilities']
    
    # Create gas sensor readings
    for area in areas:
        for i in range(20):
            reading = GasSensorReading(
                sensor_id=f'GAS-{area}-001',
                area=area,
                coordinates_x=random.uniform(10, 90),
                coordinates_y=random.uniform(10, 90),
                coordinates_z=random.uniform(0, 10),
                o2_percentage=random.uniform(20.5, 21.0),
                lel_percentage=random.uniform(0, 3),
                h2s_ppm=random.uniform(0, 2),
                co_ppm=random.uniform(0, 15),
                alert_level=AlertLevel.NORMAL,
                threshold_exceeded=False,
                created_at=datetime.now() - timedelta(hours=20-i)
            )
            db.session.add(reading)
    
    # Create some active permits
    permit_types = [PermitType.HOT_WORK, PermitType.CONFINED_SPACE, PermitType.ELECTRICAL]
    for i, permit_type in enumerate(permit_types):
        permit = PermitToWork(
            permit_number=f'PTW-{datetime.now().strftime("%Y%m%d")}-{1000+i}',
            permit_type=permit_type,
            status=PermitStatus.ACTIVE,
            work_description=f'{permit_type.value.replace("_", " ").title()} work in progress',
            area=random.choice(areas),
            coordinates_x=random.uniform(20, 80),
            coordinates_y=random.uniform(20, 80),
            coordinates_z=random.uniform(0, 8),
            worker_name=fake.name(),
            worker_id=f'EMP-{random.randint(1000, 9999)}',
            supervisor_name=fake.name(),
            start_time=datetime.now() - timedelta(hours=random.randint(1, 4)),
            end_time=datetime.now() + timedelta(hours=random.randint(2, 6)),
            risk_score=random.uniform(30, 70),
            risk_level=RiskLevel.MEDIUM
        )
        db.session.add(permit)
    
    db.session.commit()
    logger.info("Demo 3 seeded successfully")


def seed_demo4_mobility():
    """Seed Demo 4 - Mobility Maestro data"""
    logger.info("Seeding Demo 4 - Mobility Maestro...")
    
    # Indian cities
    cities_tier1 = [
        ('Mumbai', 'Maharashtra', 19.0760, 72.8777),
        ('Delhi', 'Delhi', 28.7041, 77.1025),
        ('Bangalore', 'Karnataka', 12.9716, 77.5946),
        ('Hyderabad', 'Telangana', 17.3850, 78.4867),
        ('Chennai', 'Tamil Nadu', 13.0827, 80.2707)
    ]
    
    cities_tier2 = [
        ('Pune', 'Maharashtra', 18.5204, 73.8567),
        ('Ahmedabad', 'Gujarat', 23.0225, 72.5714),
        ('Jaipur', 'Rajasthan', 26.9124, 75.7873),
        ('Lucknow', 'Uttar Pradesh', 26.8467, 80.9462),
        ('Coimbatore', 'Tamil Nadu', 11.0168, 76.9558)
    ]
    
    site_counter = 1
    
    # Create Tier 1 sites
    for city, state, lat, lng in cities_tier1:
        for i in range(random.randint(3, 5)):
            site = ChargingSite(
                site_id=f'SITE-T1-{site_counter:03d}',
                city=city,
                state=state,
                latitude=lat + random.uniform(-0.1, 0.1),
                longitude=lng + random.uniform(-0.1, 0.1),
                city_tier=CityTier.TIER_1,
                network_position=random.choice([NetworkPosition.URBAN, NetworkPosition.SUBURBAN]),
                land_area_sqm=random.uniform(1000, 3000),
                land_cost_inr=random.uniform(5000000, 15000000),
                grid_connection_available=True,
                grid_capacity_kw=random.uniform(400, 1000),
                population_density=random.uniform(3000, 8000),
                avg_household_income=random.uniform(800000, 2000000),
                ev_penetration_rate=random.uniform(2.5, 5.0),
                daily_traffic_count=random.randint(8000, 15000),
                estimated_daily_sessions=random.randint(30, 80),
                existing_chargers_within_5km=random.randint(0, 3),
                status=SiteStatus.CANDIDATE
            )
            db.session.add(site)
            site_counter += 1
    
    # Create Tier 2 sites
    for city, state, lat, lng in cities_tier2:
        for i in range(random.randint(2, 4)):
            site = ChargingSite(
                site_id=f'SITE-T2-{site_counter:03d}',
                city=city,
                state=state,
                latitude=lat + random.uniform(-0.1, 0.1),
                longitude=lng + random.uniform(-0.1, 0.1),
                city_tier=CityTier.TIER_2,
                network_position=random.choice([NetworkPosition.URBAN, NetworkPosition.HIGHWAY]),
                land_area_sqm=random.uniform(800, 2000),
                land_cost_inr=random.uniform(2000000, 8000000),
                grid_connection_available=True,
                grid_capacity_kw=random.uniform(300, 600),
                population_density=random.uniform(1500, 4000),
                avg_household_income=random.uniform(500000, 1200000),
                ev_penetration_rate=random.uniform(1.5, 3.5),
                daily_traffic_count=random.randint(4000, 9000),
                estimated_daily_sessions=random.randint(15, 45),
                existing_chargers_within_5km=random.randint(0, 2),
                status=SiteStatus.CANDIDATE
            )
            db.session.add(site)
            site_counter += 1
    
    db.session.commit()
    logger.info("Demo 4 seeded successfully")


def seed_demo5_copilot():
    """Seed Demo 5 - Engineer's Copilot data"""
    logger.info("Seeding Demo 5 - Engineer's Copilot...")
    
    # Research papers
    paper_titles = [
        'Advanced Synthetic Esters for High-Temperature Engine Oils',
        'Zinc-Free Antiwear Additives: Performance Evaluation',
        'Viscosity Index Improvers for Multi-grade Oils',
        'Oxidation Stability Enhancement in Hydraulic Fluids',
        'Biodegradable Lubricants for Marine Applications',
        'Nanomaterials in Tribology: A Comprehensive Review',
        'Friction Modifiers for Fuel Economy Improvement',
        'Low-Temperature Performance of Automotive Lubricants'
    ]
    
    for i, title in enumerate(paper_titles):
        paper = ResearchPaper(
            paper_id=f'TCAP-{random.randint(2018, 2024)}-{1000+i:04d}',
            title=title,
            authors=[fake.name() for _ in range(random.randint(1, 3))],
            publication_date=fake.date_between(start_date='-5y', end_date='today'),
            source=random.choice(['Internal Report', 'Journal', 'Conference', 'IIT Mumbai']),
            document_type=DocumentType.PAPER,
            abstract=f'This study investigates {title.lower()} with focus on performance characteristics...',
            keywords=['lubricants', 'performance', 'testing'],
            research_area=random.choice(['engine_oils', 'industrial_lubricants', 'additives']),
            language='en'
        )
        db.session.add(paper)
    
    # Formulation trials
    base_oils = ['Group II', 'Group III', 'PAO', 'Ester']
    for i in range(20):
        trial = FormulationTrial(
            trial_id=f'TCAP-T-{datetime.now().year}-{1000+i:04d}',
            trial_name=f'{random.choice(["10W-30", "15W-40", "5W-40"])} {random.choice(["Engine Oil", "Hydraulic Oil"])}',
            base_oil=random.choice(base_oils),
            base_oil_percentage=random.uniform(75, 90),
            additive_package={'additives': []},
            product_type=random.choice(['Engine Oil', 'Hydraulic Oil', 'Gear Oil']),
            target_viscosity_grade=random.choice(['10W-30', '15W-40', '5W-40']),
            viscosity_40c=random.uniform(90, 110),
            viscosity_100c=random.uniform(13, 16),
            viscosity_index=random.randint(120, 160),
            wear_resistance_score=random.uniform(80, 95),
            oxidation_stability_hours=random.uniform(180, 250),
            performance_score=random.uniform(75, 95),
            meets_specifications=random.choice([True, True, True, False]),
            cost_per_liter_inr=random.uniform(180, 350),
            status=TrialStatus.COMPLETED,
            researcher_name=fake.name()
        )
        db.session.add(trial)
    
    db.session.commit()
    logger.info("Demo 5 seeded successfully")


def seed_all_demos():
    """Seed all demos"""
    logger.info("Starting database seeding...")
    
    try:
        seed_users()
        seed_demo1_carbon()
        seed_demo2_grid()
        seed_demo3_safety()
        seed_demo4_mobility()
        seed_demo5_copilot()
        
        logger.info("All demos seeded successfully!")
        print("✅ Database seeded successfully!")
        
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.session.rollback()
        raise


if __name__ == '__main__':
    from app import create_app
    app = create_app()
    with app.app_context():
        seed_all_demos()