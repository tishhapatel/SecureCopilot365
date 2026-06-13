import os
import sys
import pytest
import zipfile
import io
from datetime import datetime, timedelta
from fastapi import HTTPException

# Adjust path to import backend modules
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "apps", "backend"))

from utils.scoring import calculate_phishing_risk_score, calculate_vendor_risk_score
from utils.upload_scanner import validate_file_upload, EICAR_SIGNATURE

def test_calculate_phishing_risk_score():
    # Test empty indicators
    assert calculate_phishing_risk_score([]) == 0.0
    assert calculate_phishing_risk_score(None) == 0.0

    # Test individual severities
    assert calculate_phishing_risk_score([{"severity": "critical"}]) == 45.0
    assert calculate_phishing_risk_score([{"severity": "high"}]) == 25.0
    assert calculate_phishing_risk_score([{"severity": "medium"}]) == 10.0
    assert calculate_phishing_risk_score([{"severity": "low"}]) == 5.0
    assert calculate_phishing_risk_score([{"severity": "unknown"}]) == 5.0  # fallback to low

    # Test score capping at 100.0
    indicators = [
        {"severity": "critical"},
        {"severity": "critical"},
        {"severity": "high"},
        {"severity": "medium"}
    ]
    # 45 + 45 + 25 + 10 = 125, capped at 100
    assert calculate_phishing_risk_score(indicators) == 100.0

def test_calculate_vendor_risk_score_simple():
    # Clean case
    score = calculate_vendor_risk_score(
        cert_score=100.0,
        data_score=0.0,
        questionnaire_responses={"mfa": True, "sso": "yes", "encryption": "True"},
        pen_test_date_str=datetime.utcnow().strftime("%Y-%m-%d"),
        incidents=[],
        dpa_signed=True
    )
    assert score == 0.0

def test_calculate_vendor_risk_score_medium_risk():
    # Partially compliant case
    score = calculate_vendor_risk_score(
        cert_score=80.0,  # cert_risk = 20.0 (wt=0.25) => 5.0
        data_score=50.0,  # data_risk = 50.0 (wt=0.20) => 10.0
        questionnaire_responses={"mfa": True, "sso": "no", "encryption": False},  # 1/3 yes = 33.3% => q_risk = 66.7 (wt=0.20) => 13.34
        pen_test_date_str=(datetime.utcnow() - timedelta(days=200)).strftime("%Y-%m-%d"),  # 180-365 days => pen_test_risk = 30.0 (wt=0.15) => 4.5
        incidents=[{"id": 1}],  # 1 incident => incident_risk = 35.0 (wt=0.10) => 3.5
        dpa_signed=True  # dpa_risk = 0.0 (wt=0.10) => 0.0
    )
    # Expected weighted score: 5.0 + 10.0 + 13.34 + 4.5 + 3.5 + 0.0 = 36.34 -> rounded to 36.3
    assert score == 36.3

def test_calculate_vendor_risk_score_high_risk():
    # Highly non-compliant, old pen test, DPA not signed
    score = calculate_vendor_risk_score(
        cert_score=40.0,  # cert_risk = 60.0 (wt=0.25) => 15.0
        data_score=90.0,  # data_risk = 90.0 (wt=0.20) => 18.0
        questionnaire_responses={},  # q_score = 50.0 => q_risk = 50.0 (wt=0.20) => 10.0
        pen_test_date_str=(datetime.utcnow() - timedelta(days=400)).strftime("%Y-%m-%d"),  # >365 days => pen_test_risk = 60.0 (wt=0.15) => 9.0
        incidents=[{"id": 1}, {"id": 2}, {"id": 3}],  # 3 incidents => incident_risk = 100.0 (wt=0.10) => 10.0
        dpa_signed=False  # dpa_risk = 80.0 (wt=0.10) => 8.0
    )
    # Expected weighted score: 15.0 + 18.0 + 10.0 + 9.0 + 10.0 + 8.0 = 70.0
    assert score == 70.0

def test_calculate_vendor_risk_score_invalid_date():
    # Test invalid date formatting
    score = calculate_vendor_risk_score(
        cert_score=100.0,
        data_score=0.0,
        questionnaire_responses={"mfa": True},
        pen_test_date_str="invalid-date-format",  # triggers ValueError/TypeError => pen_test_risk = 80.0 (wt=0.15) => 12.0
        incidents=[],
        dpa_signed=True
    )
    assert score == 12.0

def test_upload_scanner_missing_filename():
    with pytest.raises(HTTPException) as exc:
        validate_file_upload("", b"content")
    assert exc.value.status_code == 400
    assert "File name is missing" in exc.value.detail

def test_upload_scanner_missing_extension():
    with pytest.raises(HTTPException) as exc:
        validate_file_upload("file_without_ext", b"content")
    assert exc.value.status_code == 400
    assert "Extension is missing" in exc.value.detail

def test_upload_scanner_unsupported_extension():
    with pytest.raises(HTTPException) as exc:
        validate_file_upload("file.png", b"content")
    assert exc.value.status_code == 400
    assert "is not supported" in exc.value.detail

def test_upload_scanner_office_doc_macros():
    # Create an in-memory zip file representing a .docx containing a vbaProject.bin
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("word/vbaProject.bin", b"mock macro content")
        zip_file.writestr("word/document.xml", b"mock document body")
    
    macro_docx_content = zip_buffer.getvalue()
    
    with pytest.raises(HTTPException) as exc:
        validate_file_upload("malicious_doc.docx", macro_docx_content)
    assert exc.value.status_code == 400
    assert "Office documents containing embedded VBA macros are blocked" in exc.value.detail

def test_upload_scanner_office_doc_safe():
    # Create an in-memory zip file representing a safe .docx
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("word/document.xml", b"mock document body")
    
    safe_docx_content = zip_buffer.getvalue()
    assert validate_file_upload("safe_doc.docx", safe_docx_content) is True
