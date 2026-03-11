from fastapi import APIRouter
from src.db.database import SessionLocal
from src.db.models import Lease
from sqlalchemy import func

router = APIRouter()

@router.get("/portfolio/summary")
def portfolio_summary():

    db = SessionLocal()

    total_leases = db.query(Lease).count()

    avg_rent = db.query(func.avg(Lease.base_rent)).scalar()

    high_risk = db.query(Lease).filter(
        Lease.renewal_risk_score > 0.5
    ).count()

    db.close()

    return {
        "total_leases": total_leases,
        "average_rent": avg_rent,
        "high_risk_leases": high_risk
    }