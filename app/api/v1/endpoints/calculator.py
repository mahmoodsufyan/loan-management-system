from fastapi import APIRouter, HTTPException, status
from app.schemas.loan import (
    CalculationRequestSchema,
    CalculationResponseSchema,
    EarlySettlementRequestSchema,
    EarlySettlementResponseSchema
)
from app.core.calculator import AmortizationCalculator

router = APIRouter()

@router.post(
    "/schedule",
    response_model=CalculationResponseSchema,
    summary="Calculate Full Amortization Schedule",
    description="Computes precise period-by-period principal, profit/interest, and remaining balances across Equal Installments, Reducing Balance, and Islamic Murabaha methods."
)
def calculate_loan_schedule(payload: CalculationRequestSchema):
    try:
        result = AmortizationCalculator.calculate_schedule(
            principal=payload.principal,
            annual_rate=payload.annual_rate,
            tenor_months=payload.tenor_months,
            start_date=payload.start_date,
            method=payload.method,
            frequency=payload.frequency,
            grace_period_months=payload.grace_period_months
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

@router.post(
    "/early-settlement",
    response_model=EarlySettlementResponseSchema,
    summary="Calculate Early Settlement & Rebate",
    description="Computes net payoff amount and unearned profit rebate when a loan is settled ahead of schedule."
)
def calculate_early_settlement(payload: EarlySettlementRequestSchema):
    result = AmortizationCalculator.calculate_early_settlement(
        remaining_principal=payload.remaining_principal,
        unearned_profit=payload.unearned_profit,
        rebate_percentage=payload.rebate_percentage,
        settlement_fee=payload.settlement_fee
    )
    return result
