import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from migration_scripts.seed_base import clear_all_tables
from migration_scripts.seed_core import run_core_migration
from migration_scripts.seed_users import run_users_migration
from migration_scripts.seed_clubs import run_clubs_migration
from migration_scripts.seed_events import run_events_migration
from migration_scripts.seed_operations import run_operations_migration
from migration_scripts.seed_systems import run_systems_migration

def run_all():
    print("=== STARTING FULL DATABASE MIGRATION ===")
    
    # 0. Clear Tables
    clear_all_tables()
    
    # 1. Core
    run_core_migration()
    
    # 2. Users
    run_users_migration()
    
    # 3. Clubs
    run_clubs_migration()
    
    # 4. Events
    run_events_migration()
    
    # 5. Operations
    run_operations_migration()
    
    # 6. Systems
    run_systems_migration()
    
    print("=== MIGRATION COMPLETELY FINISHED SUCCESSFULLY ===")

if __name__ == "__main__":
    run_all()
