from sqlalchemy.orm import Session
from models import Report
from schemas.report import ReportCreate


def create_report(db: Session, report_data: ReportCreate):
    report = Report(**report_data.dict())
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def get_reports(db: Session):
    return db.query(Report).all()


def get_reports_by_owner_id(db: Session, owner_id: int):
    return db.query(Report).filter(Report.owner_id == owner_id).all()
