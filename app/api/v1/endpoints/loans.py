from fastapi import APIRouter, HTTPException, Response, status
from typing import List
from datetime import date
from app.schemas.loan import (
    LoanCreateSchema,
    LoanResponseSchema,
    LoanStatusUpdateSchema
)
from app.services.loan_store import LoanStore
from app.core.calculator import AmortizationCalculator
from app.core.workflow import InvalidStateTransitionError
from app.services.pdf_service import LoanPDFService

router = APIRouter()

@router.post(
    "",
    response_model=LoanResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create Loan Application",
    description="Initializes a new loan record in DRAFT status."
)
def create_loan(payload: LoanCreateSchema):
    return LoanStore.create(payload)

@router.get(
    "",
    response_model=List[LoanResponseSchema],
    summary="List All Loan Applications"
)
def list_loans():
    return LoanStore.list_all()

@router.get(
    "/{loan_id}",
    response_model=LoanResponseSchema,
    summary="Get Loan Details by ID"
)
def get_loan(loan_id: str):
    loan = LoanStore.get(loan_id)
    if not loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Loan '{loan_id}' not found.")
    return loan

@router.patch(
    "/{loan_id}/status",
    response_model=LoanResponseSchema,
    summary="Transition Loan Lifecycle Status",
    description="Transitions loan through the credit state machine (DRAFT -> SUBMITTED -> CREDIT_REVIEW -> APPROVED -> DISBURSED -> ACTIVE -> SETTLED)."
)
def update_loan_status(loan_id: str, payload: LoanStatusUpdateSchema):
    try:
        return LoanStore.update_status(loan_id, payload.target_status, payload.notes)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Loan '{loan_id}' not found.")
    except InvalidStateTransitionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get(
    "/{loan_id}/export-pdf",
    summary="Export Loan Repayment Schedule as PDF",
    description="Generates a downloadable PDF repayment schedule document."
)
def export_loan_schedule_pdf(loan_id: str):
    loan = LoanStore.get(loan_id)
    if not loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Loan '{loan_id}' not found.")
    
    schedule_data = AmortizationCalculator.calculate_schedule(
        principal=loan["principal"],
        annual_rate=loan["annual_rate"],
        tenor_months=loan["tenor_months"],
        start_date=date.today(),
        method=loan["method"],
        frequency=loan["frequency"],
        grace_period_months=loan.get("grace_period_months", 0)
    )

    pdf_bytes = LoanPDFService.generate_schedule_pdf(schedule_data, applicant_name=loan["applicant_name"])
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=loan_schedule_{loan_id}.pdf"}
    )
