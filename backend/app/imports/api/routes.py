from fastapi import APIRouter, UploadFile, File, HTTPException
from tempfile import NamedTemporaryFile
import shutil

from app.imports.service import ImportService
from app.imports.schemas import ImportedTransactionResponse

router = APIRouter(
    prefix="/imports",
    tags=["Imports"],
)

@router.post("/preview")
async def preview_import(
    file: UploadFile = File(...),
):

    with NamedTemporaryFile(delete=False) as tmp:

        shutil.copyfileobj(file.file, tmp)

        tmp_path = tmp.name

    try:

        rows = ImportService().preview(tmp_path)

        return {
            "bank": "GTBank",
            "count": len(rows),
            "transactions": [
                ImportedTransactionResponse.model_validate(row)
                for row in rows
            ],
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )