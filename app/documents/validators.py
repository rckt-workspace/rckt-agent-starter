from pathlib import Path
from fastapi import HTTPException, UploadFile
from app.core.config import settings

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".csv"}

ALLOWED_MIME_TYPES = {
    ".pdf": {
        "application/pdf",
        "application/x-pdf",
        "binary/octet-stream",
        "application/octet-stream",
    },
    ".docx": {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/zip",
        "application/octet-stream",
        "application/x-zip-compressed",
    },
    ".txt": {
        "text/plain",
        "application/octet-stream",
    },
    ".md": {
        "text/markdown",
        "text/x-markdown",
        "text/plain",
        "application/octet-stream",
    },
    ".csv": {
        "text/csv",
        "application/vnd.ms-excel",
        "text/plain",
        "application/csv",
        "text/comma-separated-values",
        "application/octet-stream",
    },
}

CHUNK_SIZE = 64 * 1024  # 64 KB


async def validate_document_file(file: UploadFile) -> bytes:
    """
    Validates uploaded file extension, MIME type, size limit, and basic magic signatures.
    Reads file content in memory (does not persist to disk).
    Returns file bytes if valid, or raises HTTPException (413, 415, 422).
    """
    filename = file.filename or ""
    suffix = Path(filename).suffix.lower()

    # 1. Extension validation
    if not suffix or suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file format '{suffix or 'unknown'}'. Supported formats: .pdf, .docx, .txt, .md, .csv",
        )

    # 2. MIME type validation (when reasonable and provided)
    raw_content_type = (file.content_type or "").lower().split(";")[0].strip()
    if raw_content_type:
        expected_mimes = ALLOWED_MIME_TYPES.get(suffix, set())
        if expected_mimes and raw_content_type not in expected_mimes:
            raise HTTPException(
                status_code=415,
                detail=f"Unsupported content type '{file.content_type}' for {suffix} file.",
            )

    # 3. Size check while reading in chunks to prevent reading massive files into memory
    chunks = []
    total_bytes = 0
    max_bytes = settings.max_file_size_bytes

    while True:
        chunk = await file.read(CHUNK_SIZE)
        if not chunk:
            break
        total_bytes += len(chunk)
        if total_bytes > max_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"File exceeds maximum allowed size of {settings.max_file_size_mb}MB.",
            )
        chunks.append(chunk)

    content_bytes = b"".join(chunks)

    # 4. Empty check
    if len(content_bytes) == 0:
        raise HTTPException(
            status_code=422,
            detail="The uploaded file is empty.",
        )

    # 5. Magic byte / content signature verification
    if suffix == ".pdf":
        if not content_bytes.startswith(b"%PDF-"):
            raise HTTPException(
                status_code=415,
                detail="Invalid PDF file format: missing PDF signature.",
            )
    elif suffix == ".docx":
        # DOCX is an Office Open XML package stored as a ZIP
        if not content_bytes.startswith(b"PK\x03\x04"):
            raise HTTPException(
                status_code=415,
                detail="Invalid DOCX file format: missing ZIP package signature.",
            )
    elif suffix in {".txt", ".md", ".csv"}:
        # Text files should not contain null bytes in their leading bytes
        sample = content_bytes[:8192]
        if b"\x00" in sample:
            raise HTTPException(
                status_code=415,
                detail="Invalid text file format: file appears to contain binary data.",
            )

    return content_bytes
