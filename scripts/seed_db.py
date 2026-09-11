"""Seed database with master schemes and initial test fixture data."""
import json
import os
import sys

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.database import SessionLocal, Base, engine
from app.models.scheme import Scheme


def seed():
    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        seed_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "seeds", "schemes.json"))
        if not os.path.exists(seed_path):
            print(f"Seed file not found at {seed_path}")
            return

        with open(seed_path, "r", encoding="utf-8") as f:
            schemes_data = json.load(f)

        for item in schemes_data:
            existing = db.query(Scheme).filter(Scheme.scheme_code == item["scheme_code"]).first()
            if not existing:
                scheme = Scheme(
                    scheme_code=item["scheme_code"],
                    scheme_name=item["scheme_name"],
                    ministry_or_dept=item.get("ministry_or_dept"),
                    max_loan_amount=item.get("max_loan_amount", 0.0),
                    subsidy_percentage_general=item.get("subsidy_percentage_general", 0.0),
                    subsidy_percentage_special=item.get("subsidy_percentage_special", 0.0),
                    interest_subvention_pct=item.get("interest_subvention_pct", 0.0),
                    eligibility_criteria=item.get("eligibility_criteria", {}),
                    required_documents=item.get("required_documents", []),
                    official_portal_url=item.get("official_portal_url")
                )
                db.add(scheme)
                print(f"  + Added scheme: {item['scheme_name']} ({item['scheme_code']})")
        
        db.commit()
        print("Database seeding completed successfully!")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
