from enum import Enum

class CalculationMethod(str, Enum):
    EQUAL_INSTALLMENTS = "equal_installments"       # Annuity / French Method (القسط الثابت)
    REDUCING_BALANCE = "reducing_balance"           # Declining Principal (القسط المتناقص)
    FLAT_RATE_MURABAHA = "flat_rate_murabaha"       # Fixed Profit / Islamic Murabaha (المرابحة الإسلامية)

class PaymentFrequency(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUALLY = "semi_annually"
    ANNUALLY = "annually"

class LoanStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    CREDIT_REVIEW = "credit_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    DISBURSED = "disbursed"
    ACTIVE = "active"
    SETTLED = "settled"
    DEFAULTED = "defaulted"
