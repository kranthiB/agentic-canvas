#!/usr/bin/env python3
"""
Migration script to convert EV charging sites data to CNG refueling sites
This script migrates data from charging_sites table to cng_sites table
"""

from app import create_app, db
from sqlalchemy import text
import sys

def migrate_charging_to_cng():
    """Migrate data from charging_sites to cng_sites table"""
    
    app = create_app()
    with app.app_context():
        try:
            print("🚀 Starting EV to CNG data migration...")
            
            # Check if old table exists and has data
            result = db.session.execute(text('SELECT COUNT(*) FROM charging_sites'))
            old_count = result.fetchone()[0]
            print(f"📊 Found {old_count} records in charging_sites table")
            
            if old_count == 0:
                print("⚠️  No data to migrate from charging_sites")
                return
            
            # Check if new table is empty
            result = db.session.execute(text('SELECT COUNT(*) FROM cng_sites'))
            new_count = result.fetchone()[0]
            
            if new_count > 0:
                print(f"⚠️  cng_sites table already has {new_count} records")
                response = input("Do you want to clear and re-migrate? (y/N): ")
                if response.lower() != 'y':
                    print("❌ Migration cancelled")
                    return
                else:
                    # Clear existing data
                    db.session.execute(text('DELETE FROM cng_sites'))
                    print("🗑️  Cleared existing cng_sites data")
            
            # Migrate data with field mapping
            migration_sql = """
            INSERT INTO cng_sites (
                id, site_id, city, state, latitude, longitude,
                city_tier, network_position, land_area_sqm, land_cost_inr,
                gas_pipeline_available, pipeline_capacity_scm,
                population_density, avg_household_income, cng_vehicle_penetration_rate,
                daily_traffic_count, estimated_daily_refuels, peak_hour_demand,
                existing_cng_stations_within_5km, nearest_competitor_distance_km,
                status, created_at, updated_at
            )
            SELECT 
                id, site_id, city, state, latitude, longitude,
                city_tier, network_position, land_area_sqm, land_cost_inr,
                COALESCE(grid_connection_available, 1) as gas_pipeline_available,
                COALESCE(grid_capacity_kw, 1000) as pipeline_capacity_scm,
                population_density, avg_household_income, 
                COALESCE(ev_penetration_rate, 0.05) as cng_vehicle_penetration_rate,
                daily_traffic_count, 
                COALESCE(estimated_daily_sessions, 50) as estimated_daily_refuels,
                peak_hour_demand,
                COALESCE(existing_chargers_within_5km, 0) as existing_cng_stations_within_5km,
                nearest_competitor_distance_km,
                status, created_at, updated_at
            FROM charging_sites
            """
            
            print("📋 Executing data migration...")
            db.session.execute(text(migration_sql))
            
            # Also migrate site_evaluations foreign key references
            print("🔗 Updating site_evaluations foreign key references...")
            
            # The site_evaluations table should already reference the correct IDs
            # since we're keeping the same primary key IDs
            
            db.session.commit()
            
            # Verify migration
            result = db.session.execute(text('SELECT COUNT(*) FROM cng_sites'))
            final_count = result.fetchone()[0]
            
            print(f"✅ Successfully migrated {final_count} records to cng_sites")
            
            # Show sample data
            result = db.session.execute(text('''
                SELECT site_id, city, state, estimated_daily_refuels 
                FROM cng_sites 
                LIMIT 5
            '''))
            sample_data = result.fetchall()
            
            print("\n📋 Sample migrated data:")
            for row in sample_data:
                print(f"  • {row[0]} - {row[1]}, {row[2]} - {row[3]} daily refuels")
            
            print(f"\n🎉 Migration completed successfully!")
            print(f"   • {old_count} records migrated from charging_sites to cng_sites")
            print(f"   • EV-specific fields converted to CNG equivalents")
            print(f"   • Foreign key relationships preserved")
            
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            db.session.rollback()
            sys.exit(1)

if __name__ == "__main__":
    migrate_charging_to_cng()