from datetime import timedelta

from app.merchants.normalizer import MerchantNormalizer



class RecurringDetector:

    def __init__(self):
        self.normalizer = MerchantNormalizer()

    def detect(self, transactions):

        grouped = {}

        for transaction in transactions:

            merchant = self.normalizer.normalize(
                transaction.merchant,
                transaction.description,
            )

            grouped.setdefault(
                merchant,
                [],
            ).append(transaction)

        recurring = []

        for merchant, txns in grouped.items():

            if len(txns) < 3:
                continue

            txns.sort(
                key=lambda t: t.transaction_date
            )

            gaps = []

            for i in range(1, len(txns)):
                gaps.append(
                    (
                        txns[i].transaction_date
                        - txns[i - 1].transaction_date
                    ).days
                )

            average_gap = sum(gaps) / len(gaps)

            if 27 <= average_gap <= 33:
                frequency = "monthly"
            elif 6 <= average_gap <= 8:
                frequency = "weekly"
            elif 360 <= average_gap <= 370:
                frequency = "yearly"
            else:
                continue

            average_amount = (
                sum(t.amount for t in txns)
                / len(txns)
            )

            recurring.append(
                {
                    "merchant": merchant,
                    "description": txns[-1].description,
                    "transaction_type": txns[-1].transaction_type.value,
                    "average_amount": average_amount,
                    "occurrences": len(txns),
                    "last_seen": txns[-1].transaction_date,
                    "estimated_next": (
                        txns[-1].transaction_date
                        + timedelta(
                            days=round(average_gap)
                        )
                    ),
                    "confidence": min(
                        len(txns) / 6,
                        1.0,
                    ),
                    "frequency": frequency,
                }
            )

        return recurring