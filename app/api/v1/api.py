from fastapi import APIRouter
from app.api.v1.endpoints import calculator, loans

api_router = APIRouter()
api_router.include_router(calculator.router, prefix="/calculator", tags=["Amortization & Calculation Engine"])
api_router.include_router(loans.router, prefix="/loans", tags=["Loan Origination & Lifecycle Workflow"])
