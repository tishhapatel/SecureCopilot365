# REST API Reference — SecureCopilot 365

This document details the REST API endpoints exposed by the FastAPI backend service.

---

## 1. Authentication Routes

### 1.1 Standard Login
*   **Endpoint**: `POST /api/v1/auth/login`
*   **Request Body**:
    ```json
    {
      "username": "email@enterprise.com",
      "password": "userpassword"
    }
    ```
*   **Response**:
    ```json
    {
      "access_token": "jwt_token_string",
      "token_type": "bearer"
    }
    ```

### 1.2 Entra ID SSO Callback
*   **Endpoint**: `GET /api/v1/auth/entra/callback`
*   **Query Parameters**:
    *   `code`: Entra authorization code token.
*   **Description**: Exchanges the auth code for access tokens, registers new profiles via SCIM, and issues a session JWT.

---

## 2. Agent Operations

### 2.1 Orchestrator Chat Interface
*   **Endpoint**: `POST /api/v1/agents/chat`
*   **Headers**: Requires `Authorization: Bearer <token>` and `X-Device-Compliant: true` (for admin roles).
*   **Request Body**:
    ```json
    {
      "query": "Is there a compliance gap in our information security policy?"
    }
    ```
*   **Response**:
    ```json
    {
      "routing": {
        "selected_agent": "compliance",
        "confidence": 0.95,
        "routing_rationale": "Request asks to scan a policy document for gaps."
      },
      "agent_executed": "compliance",
      "analysis": {
        "finding": "Compliance Gap Identified...",
        "reasoning": "The uploaded Information Security Policy draft lacks...",
        "evidence": [...],
        "sources": [...],
        "confidence_score": 0.88
      }
    }
    ```

---

## 3. Threat Assessment Endpoints

### 3.1 Phishing Analysis
*   **Endpoint**: `POST /api/v1/phishing/analyze`
*   **Request Body**:
    ```json
    {
      "email_content": "Dear Billing Specialist, please update this contractor payment invoice...",
      "email_subject": "URGENT: Verify Wire Transfer",
      "sender_email": "external.cfo.office@gmail.com"
    }
    ```
*   **Response**: Returns the explainable AI format detailing threat scoring, indicators, and recommended actions.

### 3.2 File Upload & Scanning
*   **Endpoint**: `POST /api/v1/compliance/upload`
*   **Request**: `Multipart/form-data` with `file` payload.
*   **Behavior**: Validates file signatures, runs safety checks, and returns gap assessments.
*   **Status Codes**:
    *   `200 OK`: File accepted and processed.
    *   `400 Bad Request`: Blocked due to file signature mismatch, scripting indicators, or malware detection.

---

## 4. Audit & GRC Management

### 4.1 Ledger Forensic Verification
*   **Endpoint**: `GET /api/v1/audit/verify`
*   **Headers**: Requires `Authorization: Bearer <token>`.
*   **Response**:
    ```json
    {
      "status": "success",
      "verified": true,
      "logs_processed": 45,
      "ledger_integrity": "valid"
    }
    ```
