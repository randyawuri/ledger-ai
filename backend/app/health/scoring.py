from decimal import Decimal


class FinancialHealthScorer:

    def score(
        self,
        income: Decimal,
        expenses: Decimal,
        budget_used: float,
        emergency_months: float,
    ):

        score = 0

        #
        # Savings Rate (30)
        #

        if income > 0:
            savings_rate = float(
                (income - expenses) / income
            )
        else:
            savings_rate = 0

        if savings_rate >= 0.30:
            savings_points = 30
        elif savings_rate >= 0.20:
            savings_points = 25
        elif savings_rate >= 0.10:
            savings_points = 18
        elif savings_rate >= 0:
            savings_points = 10
        else:
            savings_points = 0

        score += savings_points

        #
        # Budget (25)
        #

        if budget_used <= 80:
            budget_points = 25
        elif budget_used <= 100:
            budget_points = 18
        elif budget_used <= 120:
            budget_points = 10
        else:
            budget_points = 0

        score += budget_points

        #
        # Cash Flow (20)
        #

        cash_points = 20 if income >= expenses else 0

        score += cash_points

        #
        # Spending Stability (15)
        #

        spending_points = 15

        score += spending_points

        #
        # Emergency Fund (10)
        #

        if emergency_months >= 6:
            emergency_points = 10
        elif emergency_months >= 3:
            emergency_points = 7
        elif emergency_months >= 1:
            emergency_points = 4
        else:
            emergency_points = 0

        score += emergency_points

        #
        # Grade
        #

        if score >= 90:
            grade = "A"
        elif score >= 80:
            grade = "B"
        elif score >= 70:
            grade = "C"
        elif score >= 60:
            grade = "D"
        else:
            grade = "F"

        if score >= 80:
            summary = (
                "Excellent financial health. "
                "Keep investing and saving."
            )
        elif score >= 60:
            summary = (
                "Your finances are stable but "
                "there is room for improvement."
            )
        else:
            summary = (
                "Your finances need attention. "
                "Focus on reducing expenses."
            )

        return {
            "score": score,
            "grade": grade,
            "summary": summary,
            "savings_rate": savings_rate * 100,
            "budget_score": budget_points,
            "cash_flow_score": cash_points,
            "spending_score": spending_points,
            "emergency_score": emergency_points,
        }