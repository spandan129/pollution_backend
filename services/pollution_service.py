from repositories.pollution_repository import PollutionRepository
from models.pollution_data import PollutionData
from sqlalchemy.orm import Session
import requests
import random
from datetime import datetime
from models.sensor_data import SensorData
from typing import Dict, Any
from logger import logger

class PollutionService:
    def __init__(self, db: Session):
        self.repository = PollutionRepository(db)

    #combine all the data source
    def get_all_data(self, start_date, end_date) -> Dict[str, Any]:
        try:
            historical_data = self.get_historical_data(start_date, end_date)
            live_sensor_data = self.fetch_live_sensor_data()
            weather_data = self.fetch_weather_data()
            
            return {
                "historical_data": {
                    "items": historical_data["items"],
                    "total_items": historical_data["total_items"],
                    "start_date": historical_data["start_date"],
                    "end_date": historical_data["end_date"]
                },
                "live_sensor_data": live_sensor_data,
                "weather_data": weather_data
            }
        except Exception as e:
            logger.error("Error combining data sources in get_all_data", exc_info=True)
            raise e

    
    #fetch historical  data from the database
    def get_historical_data(self, start_date, end_date):
        try:
            return self.repository.get_historical_data(start_date=start_date, end_date=end_date)
        except Exception as e:
            logger.error("Error fetching historical data from the database", exc_info=True)
            raise e

    def fetch_weather_data(self):
        try:
            # Fetch weather data from OpenWeatherMap API
            response = requests.get("http://api.openweathermap.org/data/2.5/weather?q=Pokhara&appid=5796abbde9106b7da4febfae8c44c232")
            response.raise_for_status()  
            return response.json()
        except requests.RequestException as e:
            logger.error("Error fetching weather data from OpenWeatherMap API", exc_info=True)
            raise e
    
    #fetch random sensor data 
    def fetch_live_sensor_data(self):
        try:
            data = SensorData(
                sensor_id="phewa-001",
                timestamp=datetime.utcnow().isoformat(),
                air_quality_index=random.randint(50, 200),
                water_quality_index=random.randint(30, 70),
                ph_level=round(random.uniform(6.5, 8.5), 2)
            )
            return data
        except Exception as e:
            logger.error("Error generating live sensor data", exc_info=True)
            raise e