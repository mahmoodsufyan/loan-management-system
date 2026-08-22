from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date
from decimal import Decimal
from app.core.enums import CalculationMethod, PaymentFrequency, LoanStatus

class ScheduleItemSchema(BaseModel):
    installment_number: int
    due_date: date
    opening_balance: Decimal
    principal: Decimal
    profit: Decimal
    total_installment: Decimal
    closing_balance: Decimal
    is_grace_period: Optional[bool] = False

class CalculationRequestSchema(BaseModel):
    principal: Decimal = Field(..., gt=0, description="Loan principal amount (e.g. 50000.00)")
    annual_rate: Decimal = Field(..., ge=0, description="Annual profit or interest rate in % (e.g. 12.5)")
    tenor_months: int = Field(..., gt=0, le=360, description="Loan term in months (e.g. 24)")
    start_date: Optional[date] = Field(default_factory=date.today, description="First disbursement / start date")
    method: CalculationMethod = Field(default=CalculationMethod.EQUAL_INSTALLMENTS, description="Amortization calculation strategy")
    frequency: PaymentFrequency = Field(default=PaymentFrequency.MONTHLY, description="Repayment interval")
    grace_period_months: int = Field(default=0, ge=0, description="Grace period in months")

class CalculationResponseSchema(BaseModel):
    principal: Decimal
    annual_rate: Decimal
    tenor_months: int
    method: str
    frequency: str
    total_installments: int
    total_profit: Decimal
    total_payable: Decimal
    schedule: List[ScheduleItemSchema]

class EarlySettlementRequestSchema(BaseModel):
    remaining_principal: Decimal = Field(..., ge=0)
    unearned_profit: Decimal = Field(..., ge=0)
    rebate_percentage: Decimal = Field(default=Decimal("100.00"), ge=0, le=100)
    settlement_fee: Decimal = Field(default=Decimal("0.00"), ge=0)

class EarlySettlementResponseSchema(BaseModel):
    remaining_principal: Decimal
    unearned_profit: Decimal
    rebate_percentage: Decimal
    rebate_amount: Decimal
    settlement_fee: Decimal
    net_payoff_amount: Decimal

class LoanCreateSchema(BaseModel):
    applicant_name: str = Field(..., min_length=3, max_length=100)
    national_id: str = Field(..., min_length=5, max_length=30)
    product_type: str = Field(default="Microfinance / SME")
    principal: Decimal = Field(..., gt=0)
    annual_rate: Decimal = Field(..., ge=0)
    tenor_months: int = Field(..., gt=0)
    method: CalculationMethod = Field(default=CalculationMethod.EQUAL_INSTALLMENTS)
    frequency: PaymentFrequency = Field(default=PaymentFrequency.MONTHLY)
    grace_period_months: int = Field(default=0, ge=0)

class LoanStatusUpdateSchema(BaseModel):
    target_status: LoanStatus
    notes: Optional[str] = None

class LoanResponseSchema(BaseModel):
    id: str
    applicant_name: str
    national_id: str
    product_type: str
    status: LoanStatus
    principal: Decimal
    annual_rate: Decimal
    tenor_months: int
    method: CalculationMethod
    frequency: PaymentFrequency
    created_at: str
    status_history: List[Dict[str, Any]]
