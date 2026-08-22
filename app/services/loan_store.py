import uuid
from datetime import datetime
from typing import Dict, List, Optional
from app.schemas.loan import LoanCreateSchema
from app.core.enums import LoanStatus
from app.core.workflow import LoanWorkflowStateMachine
from app.db.session import SessionLocal, init_db
from app.db.models import LoanApplicationModel, AuditLogModel

# Initialize database schema on module load
init_db()

class LoanStore:
    """SQLAlchemy-backed repository with thread-safe ACID persistence."""

    @classmethod
    def create(cls, data: LoanCreateSchema) -> dict:
        loan_id = f"LN-{uuid.uuid4().hex[:8].upper()}"
        now = datetime.utcnow()

        db = SessionLocal()
        try:
            loan = LoanApplicationModel(
                id=loan_id,
                applicant_name=data.applicant_name,
                national_id=data.national_id,
                product_type=data.product_type,
                status=LoanStatus.DRAFT.value,
                principal=data.principal,
                annual_rate=data.annual_rate,
                tenor_months=data.tenor_months,
                method=data.method.value if hasattr(data.method, "value") else str(data.method),
                frequency=data.frequency.value if hasattr(data.frequency, "value") else str(data.frequency),
                grace_period_months=data.grace_period_months,
                created_at=now,
                updated_at=now
            )
            db.add(loan)

            audit_log = AuditLogModel(
                loan_id=loan_id,
                from_status=None,
                to_status=LoanStatus.DRAFT.value,
                actor="Applicant / Branch Officer",
                notes="Loan application initialized in DRAFT state.",
                timestamp=now
            )
            db.add(audit_log)
            db.commit()
            db.refresh(loan)
            return loan.to_dict()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    @classmethod
    def get(cls, loan_id: str) -> Optional[dict]:
        db = SessionLocal()
        try:
            loan = db.query(LoanApplicationModel).filter(LoanApplicationModel.id == loan_id).first()
            if not loan:
                return None
            return loan.to_dict()
        finally:
            db.close()

    @classmethod
    def list_all(cls) -> List[dict]:
        db = SessionLocal()
        try:
            loans = db.query(LoanApplicationModel).order_by(LoanApplicationModel.created_at.desc()).all()
            return [loan.to_dict() for loan in loans]
        finally:
            db.close()

    @classmethod
    def update_status(cls, loan_id: str, target_status: LoanStatus, notes: Optional[str] = None, actor: str = "Authorized Officer") -> dict:
        db = SessionLocal()
        try:
            loan = db.query(LoanApplicationModel).filter(LoanApplicationModel.id == loan_id).first()
            if not loan:
                raise KeyError(f"Loan with ID '{loan_id}' not found.")

            current_status = LoanStatus(loan.status)
            target_status_enum = LoanStatus(target_status) if isinstance(target_status, str) else target_status
            LoanWorkflowStateMachine.validate_transition(current_status, target_status_enum)

            now = datetime.utcnow()
            loan.status = target_status_enum.value
            loan.updated_at = now

            audit = AuditLogModel(
                loan_id=loan_id,
                from_status=current_status.value,
                to_status=target_status_enum.value,
                actor=actor,
                notes=notes or f"Transitioned to {target_status_enum.value}",
                timestamp=now
            )
            db.add(audit)
            db.commit()
            db.refresh(loan)
            return loan.to_dict()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

