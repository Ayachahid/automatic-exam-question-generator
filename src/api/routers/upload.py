import shutil
import uuid
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from src.api.schemas.response import UploadResponse
from src.core.logger import get_logger

router = APIRouter()
logger = get_logger("api.upload")


UPLOAD_DIR = Path("data/raw")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".txt", ".pdf", ".docx"}


@router.post("/", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file (TXT, PDF, DOCX) to be used for question generation.
    """
    filename = file.filename
    extension = Path(filename).suffix.lower()

    logger.info(f"Upload request: filename={filename} extension={extension}")

    if extension not in ALLOWED_EXTENSIONS:
        logger.warning(f"Rejected unsupported extension: {extension}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension '{extension}' is not supported. Allowed: {ALLOWED_EXTENSIONS}",
        )

    file_id = str(uuid.uuid4())
    safe_filename = Path(filename).name  # simple sanitization
    saved_filename = f"{file_id}_{safe_filename}"
    file_path = UPLOAD_DIR / saved_filename

    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"File saved: {file_path}")

    except Exception as e:
        logger.error(f"Could not save file {filename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {str(e)}",
        )
    finally:
        file.file.close()

    return UploadResponse(
        filename=filename, file_path=str(file_path.absolute()), file_id=file_id
    )
