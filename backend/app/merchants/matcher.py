import re


class MerchantMatcher:

    RULES = {
        "SHOPRITE": "Shoprite",
        "UBER": "Uber",
        "BOLT": "Bolt",
        "NETFLIX": "Netflix",
        "SPOTIFY": "Spotify",
        "APPLE": "Apple",
        "AMAZON": "Amazon",
        "JUMIA": "Jumia",
        "KFC": "KFC",
        "DOMINOS": "Domino's",
        "GTBANK": "GTBank",
        "OPAY": "OPay",
        "MONIEPOINT": "Moniepoint",
        "PAYPAL": "PayPal",
        "OPENAI": "OpenAI",
        "PAYSTACK": "Paystack",
        "FLUTTERWAVE": "Flutterwave",
        "GOOGLE": "Google",
        
    }

    def normalize(self, text: str | None) -> str:

        if not text:
            return "Unknown"

        cleaned = re.sub(r"[^A-Z0-9 ]", "", text.upper())

        for keyword, merchant in self.RULES.items():
            if keyword in cleaned:
                return merchant

        return text.title()