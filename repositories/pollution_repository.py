from sqlalchemy.orm import Session
from models.pollution_data import PollutionData
from logger import logger
from math import ceil
from typing import Dict, List, Any
from datetime import datetime

class PollutionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_historical_data(self, start_date: str, end_date: str) -> Dict[str, Any]:
     try:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')

        items = self.db.query(PollutionData)\
            .filter(
                PollutionData.date >= start_date_obj,
                PollutionData.date <= end_date_obj
            )\
            .order_by(PollutionData.date.asc())\
            .all()
        
        total_items = len(items)
        
        return {
            "items": items,
            "total_items": total_items,
            "start_date": start_date,
            "end_date": end_date
        }
            
     except ValueError as ve:
        logger.error(f"Invalid date format: {ve}")
        raise ValueError("Dates must be in YYYY-MM-DD format")
     except Exception as e:
        logger.error(f"Error fetching historical data: {e}")
        raise

