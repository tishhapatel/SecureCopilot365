"""
File upload validation and security scanner for SecureCopilot 365.
Inspects file extensions, scans for active macros/scripts, and checks for malware signatures (EICAR).
"""
from fastapi import HTTPException, status
import zipfile
import io
import logging

logger = logging.getLogger(__name__)

# Standard EICAR Antivirus Test Signature
EICAR_SIGNATURE = b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"

# Safe list of extensions allowed for processing
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".csv", ".txt", ".json"}

# Rejected extensions indicating executable or script scripts
BLOCKED_EXTENSIONS = {
    ".exe", ".msi", ".bat", ".cmd", ".vbs", ".js", ".py", 
    ".sh", ".ps1", ".com", ".scr", ".pif", ".dll"
}

def scan_file_for_malware(content: bytes) -> bool:
    """
    Scans the file contents for malware signatures.
    Returns True if malware is detected.
    """
    # 1. Check for standard EICAR test string
    if EICAR_SIGNATURE in content:
        logger.critical("Malware Scanner: EICAR malware signature detected!")
        return True
    
    # In production, we integrate with an Azure Defender endpoint or a ClamAV stream scanner.
    return False

def check_active_macros_in_office_doc(content: bytes, file_name: str) -> bool:
    """
    Scans Office OpenXML documents (.docx, .xlsx) for embedded macros (VBA).
    Returns True if active macros are found.
    """
    # Office OpenXML documents are zip files. VBA macros are stored inside a binary file 'vbaProject.bin'
    if zipfile.is_zipfile(io.BytesIO(content)):
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as z:
                # Look for the presence of vbaProject.bin
                for info in z.infolist():
                    if "vbaProject.bin" in info.filename:
                        logger.warning(f"File Security Blocked: Active VBA macro project found in office document: {file_name}")
                        return True
        except Exception as e:
            logger.error(f"Error checking office doc zip structure: {e}")
    return False

def check_pdf_scripts(content: bytes, file_name: str) -> bool:
    """
    Scans PDF files for raw embedded Javascript actions.
    Returns True if scripting objects are detected.
    """
    # PDFs with active JS have tags like '/JavaScript' or '/JS'
    if b"/JavaScript" in content or b"/JS" in content:
        logger.warning(f"File Security Blocked: PDF file contains embedded JavaScript actions: {file_name}")
        return True
    return False

def validate_file_upload(file_name: str, content: bytes):
    """
    Orchestrates full file safety verification:
    1. Extension verification
    2. Malware signature scan
    3. Active code/macro scan
    """
    if not file_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File upload validation failed. File name is missing."
        )

    # 1. Extension Verification
    dot_idx = file_name.rfind(".")
    if dot_idx == -1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File upload validation failed. Extension is missing."
        )
    
    ext = file_name[dot_idx:].lower()
    
    if ext in BLOCKED_EXTENSIONS:
        logger.error(f"File Security Blocked: Executable/script block triggered for: {file_name}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security policy: Executable files, scripts, and code binaries are blocked from upload."
        )

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Security policy: File extension '{ext}' is not supported. Supported: PDF, DOCX, XLSX, CSV, TXT, JSON."
        )

    # 2. Malware Signature Scan
    if scan_file_for_malware(content):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security policy: File contains signatures associated with malicious software (Malware Blocked)."
        )

    # 3. Code/Macro verification
    if ext in [".docx", ".xlsx"] and check_active_macros_in_office_doc(content, file_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security policy: Office documents containing embedded VBA macros are blocked for safety."
        )

    if ext == ".pdf" and check_pdf_scripts(content, file_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security policy: PDF files containing active JavaScript elements are blocked for safety."
        )

    logger.info(f"File Security Approved: {file_name} passed all validation gates.")
    return True
