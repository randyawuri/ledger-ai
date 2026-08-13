from datetime import timedelta


class ForecastEngine:

    def forecast(
        self,
        current_balance,
        average_daily_income,
        average_daily_expense,
        days=30,
    ):

        balance = current_balance

        results = []

        from datetime import date

        today = date.today()

        for i in range(days):

            balance += average_daily_income
            balance -= average_daily_expense

            results.append(
                {
                    "date": today + timedelta(days=i + 1),
                    "projected_balance": balance,
                }
            )

        return results