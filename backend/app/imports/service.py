from app.imports.detector import detect_parser


class ImportService:

    def preview(
        self,
        file_path: str,
    ):
        parser = detect_parser(file_path)

        return parser.parse(file_path)