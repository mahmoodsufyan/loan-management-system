import calendar
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from typing import List, Dict, Any, Tuple
from app.core.enums import CalculationMethod, PaymentFrequency

def round_money(val: Decimal) -> Decimal:
    return val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def add_months(source_date: date, months: int) -> date:
    """Accurately adds months to a date, clamping day to end-of-month if necessary."""
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1
    day = min(source_date.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)

class AmortizationCalculator:
    """
    High-precision Financial Amortization & Loan Schedule Engine.
    Implements Equal Installments (Annuity), Reducing Balance, and Islamic Murabaha.
    """

    @staticmethod
    def _get_frequency_factor(frequency: PaymentFrequency) -> Tuple[int, int]:
        """Returns (periods_per_year, months_step)"""
        if frequency == PaymentFrequency.MONTHLY:
            return 12, 1
        elif frequency == PaymentFrequency.QUARTERLY:
            return 4, 3
        elif frequency == PaymentFrequency.SEMI_ANNUALLY:
            return 2, 6
        elif frequency == PaymentFrequency.ANNUALLY:
            return 1, 12
        return 12, 1

    @classmethod
    def calculate_schedule(
        cls,
        principal: Decimal,
        annual_rate: Decimal,
        tenor_months: int,
        start_date: date,
        method: CalculationMethod = CalculationMethod.EQUAL_INSTALLMENTS,
        frequency: PaymentFrequency = PaymentFrequency.MONTHLY,
        grace_period_months: int = 0
    ) -> Dict[str, Any]:
        """
        Calculates full payment breakdown and summary.
        """
        if isinstance(method, str):
            method = CalculationMethod(method)
        if isinstance(frequency, str):
            frequency = PaymentFrequency(frequency)

        if principal <= Decimal("0"):
            raise ValueError("Principal must be greater than 0.")
        if annual_rate < Decimal("0"):
            raise ValueError("Annual rate cannot be negative.")
        if tenor_months <= 0:
            raise ValueError("Tenor months must be positive.")

        periods_per_year, months_step = cls._get_frequency_factor(frequency)

        total_installments = tenor_months // months_step
        grace_installments = grace_period_months // months_step
        active_installments = total_installments - grace_installments

        if active_installments <= 0:
            raise ValueError("Tenor must be greater than grace period.")

        periodic_rate = (annual_rate / Decimal("100")) / Decimal(periods_per_year)

        schedule: List[Dict[str, Any]] = []
        current_balance = Decimal(principal)
        current_date = start_date
        total_profit_paid = Decimal("0.00")
        total_principal_paid = Decimal("0.00")

        if method == CalculationMethod.FLAT_RATE_MURABAHA:
            years = Decimal(tenor_months) / Decimal("12")
            total_murabaha_profit = round_money(principal * (annual_rate / Decimal("100")) * years)
            total_payable = principal + total_murabaha_profit
            
            fixed_installment = round_money(total_payable / Decimal(total_installments))
            profit_per_installment = round_money(total_murabaha_profit / Decimal(total_installments))
            principal_per_installment = fixed_installment - profit_per_installment

            for i in range(1, total_installments + 1):
                current_date = add_months(current_date, months_step)
                
                if i == total_installments:
                    p_amount = current_balance
                    prof_amount = total_murabaha_profit - total_profit_paid
                    inst_amount = p_amount + prof_amount
                else:
                    p_amount = principal_per_installment
                    prof_amount = profit_per_installment
                    inst_amount = fixed_installment

                closing_balance = round_money(current_balance - p_amount)
                if closing_balance < Decimal("0"):
                    closing_balance = Decimal("0.00")

                schedule.append({
                    "installment_number": i,
                    "due_date": current_date,
                    "opening_balance": round_money(current_balance),
                    "principal": round_money(p_amount),
                    "profit": round_money(prof_amount),
                    "total_installment": round_money(inst_amount),
                    "closing_balance": closing_balance
                })

                total_principal_paid += p_amount
                total_profit_paid += prof_amount
                current_balance = closing_balance

        elif method == CalculationMethod.EQUAL_INSTALLMENTS:
            if periodic_rate > 0:
                r_float = float(periodic_rate)
                n_float = active_installments
                pmt_factor = (r_float * (1 + r_float)**n_float) / ((1 + r_float)**n_float - 1)
                fixed_pmt = round_money(principal * Decimal(str(pmt_factor)))
            else:
                fixed_pmt = round_money(principal / Decimal(active_installments))

            inst_num = 1
            for _ in range(grace_installments):
                current_date = add_months(current_date, months_step)
                profit_amount = round_money(current_balance * periodic_rate)
                schedule.append({
                    "installment_number": inst_num,
                    "due_date": current_date,
                    "opening_balance": round_money(current_balance),
                    "principal": Decimal("0.00"),
                    "profit": profit_amount,
                    "total_installment": profit_amount,
                    "closing_balance": round_money(current_balance),
                    "is_grace_period": True
                })
                total_profit_paid += profit_amount
                inst_num += 1

            for i in range(1, active_installments + 1):
                current_date = add_months(current_date, months_step)
                profit_amount = round_money(current_balance * periodic_rate)

                if i == active_installments:
                    principal_amount = current_balance
                    installment_amount = round_money(principal_amount + profit_amount)
                else:
                    principal_amount = round_money(fixed_pmt - profit_amount)
                    installment_amount = fixed_pmt

                closing_balance = round_money(current_balance - principal_amount)
                if closing_balance < Decimal("0"):
                    closing_balance = Decimal("0.00")

                schedule.append({
                    "installment_number": inst_num,
                    "due_date": current_date,
                    "opening_balance": round_money(current_balance),
                    "principal": principal_amount,
                    "profit": profit_amount,
                    "total_installment": installment_amount,
                    "closing_balance": closing_balance,
                    "is_grace_period": False
                })

                total_principal_paid += principal_amount
                total_profit_paid += profit_amount
                current_balance = closing_balance
                inst_num += 1

        elif method == CalculationMethod.REDUCING_BALANCE:
            principal_per_inst = round_money(principal / Decimal(active_installments))
            inst_num = 1

            for _ in range(grace_installments):
                current_date = add_months(current_date, months_step)
                profit_amount = round_money(current_balance * periodic_rate)
                schedule.append({
                    "installment_number": inst_num,
                    "due_date": current_date,
                    "opening_balance": round_money(current_balance),
                    "principal": Decimal("0.00"),
                    "profit": profit_amount,
                    "total_installment": profit_amount,
                    "closing_balance": round_money(current_balance),
                    "is_grace_period": True
                })
                total_profit_paid += profit_amount
                inst_num += 1

            for i in range(1, active_installments + 1):
                current_date = add_months(current_date, months_step)
                profit_amount = round_money(current_balance * periodic_rate)

                if i == active_installments:
                    p_amount = current_balance
                else:
                    p_amount = principal_per_inst

                inst_total = round_money(p_amount + profit_amount)
                closing_balance = round_money(current_balance - p_amount)
                if closing_balance < Decimal("0"):
                    closing_balance = Decimal("0.00")

                schedule.append({
                    "installment_number": inst_num,
                    "due_date": current_date,
                    "opening_balance": round_money(current_balance),
                    "principal": p_amount,
                    "profit": profit_amount,
                    "total_installment": inst_total,
                    "closing_balance": closing_balance,
                    "is_grace_period": False
                })

                total_principal_paid += p_amount
                total_profit_paid += profit_amount
                current_balance = closing_balance
                inst_num += 1

        total_payable = round_money(total_principal_paid + total_profit_paid)

        return {
            "principal": round_money(principal),
            "annual_rate": annual_rate,
            "tenor_months": tenor_months,
            "method": method.value,
            "frequency": frequency.value,
            "total_installments": len(schedule),
            "total_profit": round_money(total_profit_paid),
            "total_payable": total_payable,
            "schedule": schedule
        }

    @classmethod
    def calculate_early_settlement(
        cls,
        remaining_principal: Decimal,
        unearned_profit: Decimal,
        rebate_percentage: Decimal = Decimal("100.00"),
        settlement_fee: Decimal = Decimal("0.00")
    ) -> Dict[str, Any]:
        rebate_amount = round_money(unearned_profit * (rebate_percentage / Decimal("100")))
        net_payoff = round_money(remaining_principal + (unearned_profit - rebate_amount) + settlement_fee)

        return {
            "remaining_principal": round_money(remaining_principal),
            "unearned_profit": round_money(unearned_profit),
            "rebate_percentage": rebate_percentage,
            "rebate_amount": rebate_amount,
            "settlement_fee": round_money(settlement_fee),
            "net_payoff_amount": net_payoff
        }
