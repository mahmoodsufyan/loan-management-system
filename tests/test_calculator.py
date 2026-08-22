import unittest
from decimal import Decimal
from datetime import date
from app.core.calculator import AmortizationCalculator
from app.core.enums import CalculationMethod, PaymentFrequency

class TestAmortizationCalculator(unittest.TestCase):
    def test_equal_installments_schedule(self):
        principal = Decimal("10000.00")
        rate = Decimal("12.00") # 1% monthly
        tenor = 12
        
        result = AmortizationCalculator.calculate_schedule(
            principal=principal,
            annual_rate=rate,
            tenor_months=tenor,
            start_date=date(2026, 1, 1),
            method=CalculationMethod.EQUAL_INSTALLMENTS
        )
        
        self.assertEqual(result["total_installments"], 12)
        self.assertEqual(len(result["schedule"]), 12)
        self.assertEqual(result["schedule"][-1]["closing_balance"], Decimal("0.00"))
        self.assertGreater(result["total_profit"], Decimal("0.00"))
        self.assertEqual(result["total_payable"], result["principal"] + result["total_profit"])

    def test_reducing_balance_schedule(self):
        principal = Decimal("12000.00")
        rate = Decimal("10.00")
        tenor = 12
        
        result = AmortizationCalculator.calculate_schedule(
            principal=principal,
            annual_rate=rate,
            tenor_months=tenor,
            start_date=date(2026, 1, 1),
            method=CalculationMethod.REDUCING_BALANCE
        )
        
        self.assertEqual(result["total_installments"], 12)
        self.assertEqual(result["schedule"][0]["principal"], Decimal("1000.00"))
        self.assertEqual(result["schedule"][-1]["closing_balance"], Decimal("0.00"))

    def test_flat_rate_murabaha(self):
        principal = Decimal("10000.00")
        rate = Decimal("10.00") # 10% per year = 1000 profit for 1 year
        tenor = 12
        
        result = AmortizationCalculator.calculate_schedule(
            principal=principal,
            annual_rate=rate,
            tenor_months=tenor,
            start_date=date(2026, 1, 1),
            method=CalculationMethod.FLAT_RATE_MURABAHA
        )
        
        self.assertEqual(result["total_profit"], Decimal("1000.00"))
        self.assertEqual(result["total_payable"], Decimal("11000.00"))
        self.assertEqual(result["schedule"][-1]["closing_balance"], Decimal("0.00"))

    def test_early_settlement_calculation(self):
        res = AmortizationCalculator.calculate_early_settlement(
            remaining_principal=Decimal("5000.00"),
            unearned_profit=Decimal("600.00"),
            rebate_percentage=Decimal("100.00")
        )
        self.assertEqual(res["net_payoff_amount"], Decimal("5000.00"))
        self.assertEqual(res["rebate_amount"], Decimal("600.00"))

if __name__ == "__main__":
    unittest.main()

