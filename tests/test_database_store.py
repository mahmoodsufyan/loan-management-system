import unittest
from decimal import Decimal
from app.services.loan_store import LoanStore
from app.schemas.loan import LoanCreateSchema
from app.core.enums import CalculationMethod, PaymentFrequency, LoanStatus

class TestDatabaseStore(unittest.TestCase):
    def test_create_and_query_loan(self):
        data = LoanCreateSchema(
            applicant_name="Tariq Mansoor",
            national_id="NID-998877",
            product_type="Agricultural Micro-Facility",
            principal=Decimal("45000.00"),
            annual_rate=Decimal("11.50"),
            tenor_months=18,
            method=CalculationMethod.REDUCING_BALANCE,
            frequency=PaymentFrequency.MONTHLY,
            grace_period_months=2
        )
        created = LoanStore.create(data)
        self.assertIsNotNone(created["id"])
        self.assertEqual(created["status"], LoanStatus.DRAFT.value)
        self.assertGreaterEqual(len(created["status_history"]), 1)

        # Retrieve
        retrieved = LoanStore.get(created["id"])
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["applicant_name"], "Tariq Mansoor")
        self.assertEqual(retrieved["grace_period_months"], 2)

    def test_state_machine_audit_logging(self):
        data = LoanCreateSchema(
            applicant_name="Sarah Al-Ahmadi",
            national_id="NID-112233",
            product_type="Commercial SME",
            principal=Decimal("100000.00"),
            annual_rate=Decimal("10.00"),
            tenor_months=24
        )
        loan = LoanStore.create(data)
        loan_id = loan["id"]

        # Transition: DRAFT -> SUBMITTED
        updated = LoanStore.update_status(loan_id, LoanStatus.SUBMITTED, "Submitted by branch officer")
        self.assertEqual(updated["status"], LoanStatus.SUBMITTED.value)
        self.assertGreaterEqual(len(updated["status_history"]), 2)

        # Transition: SUBMITTED -> CREDIT_REVIEW
        updated = LoanStore.update_status(loan_id, LoanStatus.CREDIT_REVIEW, "Assigned to risk committee", actor="Risk Officer")
        self.assertEqual(updated["status"], LoanStatus.CREDIT_REVIEW.value)
        self.assertGreaterEqual(len(updated["status_history"]), 3)
        self.assertEqual(updated["status_history"][-1]["actor"], "Risk Officer")

if __name__ == "__main__":
    unittest.main()
