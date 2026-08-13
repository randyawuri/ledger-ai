import csv

from app.imports.parsers.gtbank import GTBankParser

PARSERS = [
    GTBankParser(),
]


def detect_parser(file_path: str):
    """
    Detects which bank parser can handle a statement by scanning
    the CSV until it finds a recognizable header row.
    """

    with open(file_path, newline="", encoding="utf-8-sig") as file:
        reader = csv.reader(file)

        for row in reader:
            headers = [column.strip() for column in row]

            # Ignore completely empty rows
            if not any(headers):
                continue

            for parser in PARSERS:
                if parser.can_parse(headers):
                    return parser

    raise ValueError("Unsupported statement format")