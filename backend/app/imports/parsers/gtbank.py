import csv
from datetime import datetime
from decimal import Decimal

from app.imports.schemas import ImportedTransaction
from app.common.enums import TransactionType


class GTBankParser:
    """
    Parser for GTBank CSV statements.
    """

    REQUIRED_HEADERS = {
        "Trans. Date",
        "Debits",
        "Credits",
        "Balance",
        "Remarks",
    }

    def can_parse(self, headers: list[str]) -> bool:
        headers = {h.strip() for h in headers if h.strip()}
        return self.REQUIRED_HEADERS.issubset(headers)

    def parse(self, file_path: str) -> list[ImportedTransaction]:
        transactions: list[ImportedTransaction] = []

        with open(
            file_path,
            newline="",
            encoding="utf-8-sig",
        ) as file:

            reader = csv.reader(file)

            header = None

            # Find the actual transaction header
            for row in reader:
                row = [column.strip() for column in row]

                if self.can_parse(row):
                    header = row
                    break

            if header is None:
                raise ValueError(
                    "Could not locate GTBank transaction header."
                )

            dict_reader = csv.DictReader(
                file,
                fieldnames=header,
            )

            for row in dict_reader:

                # Skip blank rows
                if not any(row.values()):
                    continue

                debit = (
                    row["Debits"]
                    .replace(",", "")
                    .strip()
                )

                credit = (
                    row["Credits"]
                    .replace(",", "")
                    .strip()
                )

                balance = (
                    row["Balance"]
                    .replace(",", "")
                    .strip()
                )

                if debit:
                    amount = Decimal(debit)
                    transaction_type = TransactionType.DEBIT
                elif credit:
                    amount = Decimal(credit)
                    transaction_type = TransactionType.CREDIT
                else:
                    continue

                transactions.append(
                    ImportedTransaction(
                        transaction_date=datetime.strptime(
                            row["Trans. Date"],
                            "%d-%b-%Y",
                        ),
                        description=row["Remarks"].strip(),
                        amount=amount,
                        balance=Decimal(balance),
                        transaction_type=transaction_type,
                        merchant=None,
                    )
                )

        return transactions