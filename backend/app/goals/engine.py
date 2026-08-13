from datetime import date
from decimal import Decimal


class GoalEngine:

    def project(
        self,
        *,
        current_amount: Decimal,
        target_amount: Decimal,
        monthly_contribution: Decimal,
        target_date: date,
        today: date | None = None,
    ) -> dict:

        if today is None:
            today = date.today()

        months_remaining = (
            (target_date.year - today.year) * 12
            + target_date.month
            - today.month
        )

        months_remaining = max(
            1,
            months_remaining,
        )

        projected_amount = (
            current_amount
            + monthly_contribution * months_remaining
        )

        will_reach = (
            projected_amount >= target_amount
        )

        if current_amount >= target_amount:
            required_monthly = Decimal("0.00")
        else:
            required_monthly = (
                target_amount - current_amount
            ) / months_remaining

            required_monthly = required_monthly.quantize(
                Decimal("0.01")
            )

        return {
            "will_reach": will_reach,
            "projected_amount": projected_amount,
            "required_monthly": required_monthly,
            "months_remaining": months_remaining,
        }