from sqlalchemy import Column, Integer, Float, Date
from config.database_config import Base

class PollutionData(Base):
    __tablename__ = 'pollution_data'
  
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    air_quality_index = Column(Integer)
    water_quality_index = Column(Integer)
    ph_level = Column(Float)
    temperature = Column(Float)