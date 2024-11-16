from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from services.pollution_service import PollutionService
from config.database_config import get_db
from typing import Optional
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/get_all_data_of_pollution")
def get_live_data(
    start_date: Optional[str] = Query(
        default=None,
        description="Start date in YYYY-MM-DD format",
        regex=r"^\d{4}-\d{2}-\d{2}$"
    ),
    end_date: Optional[str] = Query(
        default=None,
        description="End date in YYYY-MM-DD format",
        regex=r"^\d{4}-\d{2}-\d{2}$"
    ),
    db: Session = Depends(get_db)
):

    if not start_date or not end_date:
        end_date_obj = datetime.now()
        start_date_obj = end_date_obj - timedelta(days=30)
        start_date = start_date_obj.strftime('%Y-%m-%d')
        end_date = end_date_obj.strftime('%Y-%m-%d')

    service = PollutionService(db)
    return service.get_all_data(start_date=start_date, end_date=end_date)

@router.get("/history-data")
def get_live_data(
    start_date: Optional[str] = Query(
        default=None,
        description="Start date in YYYY-MM-DD format",
        regex=r"^\d{4}-\d{2}-\d{2}$"
    ),
    end_date: Optional[str] = Query(
        default=None,
        description="End date in YYYY-MM-DD format",
        regex=r"^\d{4}-\d{2}-\d{2}$"
    ),
    db: Session = Depends(get_db)
):

    if not start_date or not end_date:
        end_date_obj = datetime.now()
        start_date_obj = end_date_obj - timedelta(days=30)
        start_date = start_date_obj.strftime('%Y-%m-%d')
        end_date = end_date_obj.strftime('%Y-%m-%d')

    service = PollutionService(db)
    return service.get_historical_data(start_date=start_date, end_date=end_date)
     