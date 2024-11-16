from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://avnadmin:AVNS_Nwvrgp4_f3jc2fi1i7a@pg-c0e0cfa-spandanbhattarai79-89ea.h.aivencloud.com:13699/defaultdb?sslmode=require"  

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()