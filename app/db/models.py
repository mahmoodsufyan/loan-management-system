from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.db.session import Base

class LoanApplicationModel(Base):
    __tablename__ = "loan_applications"

    id = Column(String(30), primary_key=True, index=True)
    applicant_name = Column(String(150), nullable=False)
    national_id = Column(String(50), nullable=False, index=True)
    product_type = Column(String(80), nullable=False, default="Microfinance / SME")
    status = Column(String(40), nullable=False, default="DRAFT", index=True)
    principal = Column(Numeric(14, 2), nullable=False)
    annual_rate = Column(Numeric(6, 2), nullable=False)
    tenor_months = Column(Integer, nullable=False)
    method = Column(String(50), nullable=False, default="EQUAL_INSTALLMENTS")
    frequency = Column(String(30), nullable=False, default="MONTHLY")
    grace_period_months = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    audit_logs = relationship("AuditLogModel", back_populates="loan", cascade="all, delete-orphan", order_by="AuditLogModel.timestamp.asc()")

    def to_dict(self):
        return {
            "id": self.id,
            "applicant_name": self.applicant_name,
            "national_id": self.national_id,
            "product_type": self.product_type,
            "status": self.status,
            "principal": Decimal(str(self.principal)),
            "annual_rate": Decimal(str(self.annual_rate)),
            "tenor_months": self.tenor_months,
            "method": self.method,
            "frequency": self.frequency,
            "grace_period_months": self.grace_period_months,
            "created_at": self.created_at.isoformat() if self.created_at else "",
            "status_history": [log.to_dict() for log in self.audit_logs]
        }

class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    loan_id = Column(String(30), ForeignKey("loan_applications.id", ondelete="CASCADE"), nullable=False, index=True)
    from_status = Column(String(40), nullable=True)
    to_status = Column(String(40), nullable=False)
    actor = Column(String(80), default="System", nullable=False)
    notes = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    loan = relationship("LoanApplicationModel", back_populates="audit_logs")

    def to_dict(self):
        return {
            "status": self.to_status,
            "from_status": self.from_status,
            "actor": self.actor,
            "timestamp": self.timestamp.isoformat() if self.timestamp else "",
            "notes": self.notes or f"Status transitioned to {self.to_status}"
        }

class DynamicRBACRuleModel(Base):
    __tablename__ = "dynamic_rbac_rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String(50), nullable=False, index=True)
    component_name = Column(String(100), nullable=False)
    action_name = Column(String(50), nullable=False)
    is_allowed = Column(Boolean, default=True, nullable=False)
