from app import create_app
from app.extensions import db
import time

def create_all_tables():
    """Ensures all tables exist"""
    app = create_app()
    with app.app_context():
        print("Creating all database tables...")
        db.create_all()
        print("All tables created successfully!")

if __name__ == "__main__":
    print("Starting to ensure all tables exist...")
    start_time = time.time()
    
    create_all_tables()
    
    end_time = time.time()
    print(f"Operation completed in {end_time - start_time:.2f} seconds")
