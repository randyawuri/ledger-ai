import re

from app.merchants.aliases import MERCHANT_ALIASES


class MerchantNormalizer:

    def normalize(
        self,
        merchant: str | None,
        description: str,
    ) -> str:

        text = merchant or description

        text = text.upper()

        text = re.sub(
            r"\d+",
            "",
            text,
        )

        text = re.sub(
            r"[^A-Z ]",
            " ",
            text,
        )

        text = " ".join(
            text.split()
        )

        for alias, canonical in MERCHANT_ALIASES.items():

            if alias in text:

                return canonical

        return text.title()