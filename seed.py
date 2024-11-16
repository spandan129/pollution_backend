import random
from datetime import date, timedelta
from sqlalchemy.orm import Session
from models.pollution_data import PollutionData
from config.database_config import SessionLocal

def generate_random_pollution_data(start_date: date, num_days: int):
    data = []
    for i in range(num_days):
        current_date = start_date + timedelta(days=i)
        air_quality_index = random.randint(50, 200) 
        water_quality_index = random.randint(50, 100) 
        ph_level = round(random.uniform(6.5, 8.5), 1) 
        temperature = round(random.uniform(18.0, 30.0), 1) 
        data.append(PollutionData(
            date=current_date,
            air_quality_index=air_quality_index,
            water_quality_index=water_quality_index,
            ph_level=ph_level,
            temperature=temperature
        ))
    return data

def seed_data(db: Session):
    start_date = date(2024, 1, 1) 
    num_days = 365
    random_pollution_data = generate_random_pollution_data(start_date, num_days)
    db.add_all(random_pollution_data)
    db.commit()

def main():
    db = SessionLocal()
    seed_data(db)
    db.close()

if __name__ == "__main__":
    main()
