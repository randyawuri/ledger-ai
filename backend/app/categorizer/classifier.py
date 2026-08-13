from app.categorizer.rules import CATEGORY_RULES


class TransactionClassifier:

    def predict(
        self,
        merchant: str,
        description: str,
    ):

        text = (
            merchant
            + " "
            + description
        ).upper()

        for category, keywords in CATEGORY_RULES.items():

            for keyword in keywords:

                if keyword in text:

                    return category

        return None