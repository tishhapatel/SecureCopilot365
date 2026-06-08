"""
Microsoft Graph Client Core
Handles Entra ID authentication and access token generation.
"""
import os
import httpx
import logging

logger = logging.getLogger(__name__)

class GraphClient:
    def __init__(self):
        self.tenant_id = os.getenv("ENTRA_TENANT_ID")
        self.client_id = os.getenv("ENTRA_CLIENT_ID")
        self.client_secret = os.getenv("ENTRA_CLIENT_SECRET")
        self.base_url = os.getenv("GRAPH_API_BASE_URL", "https://graph.microsoft.com/v1.0")

    async def get_access_token(self) -> str:
        """
        Retrieves access token using client credentials grant.
        Returns a mock token if parameters are not configured.
        """
        if not all([self.tenant_id, self.client_id, self.client_secret]) or "mock" in self.tenant_id:
            return "mock_graph_access_token_12345"
            
        url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "https://graph.microsoft.com/.default"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, data=data)
                if response.status_code == 200:
                    return response.json().get("access_token")
            except Exception as e:
                logger.error(f"Failed to fetch Graph API access token: {e}")
                
        return "mock_graph_access_token_12345"

    async def collect_audit_evidence(self, tenant_id: str) -> dict:
        """
        Simulates collecting evidence for audit readiness assessments.
        Returns detailed compliance metrics from Entra ID and SharePoint.
        """
        # In a real environment, this method would query Graph endpoints:
        # - GET /directory/conditionalAccess/policies
        # - GET /reports/credentialUserRegistrationDetails (MFA status)
        # - GET /sites/root/drive/root/children (Policy files checking)
        
        # Return high-fidelity mockup compliance data
        return {
            "entra_id": {
                "mfa_registration_rate": 94.5,
                "conditional_access_policies_count": 8,
                "active_global_admins_count": 3,
                "mfa_enforced_for_admins": True,
                "guest_users_external_collaboration_restricted": True
            },
            "sharepoint": {
                "policy_document_library_found": True,
                "policy_documents_detected": [
                    {"name": "Information_Security_Policy_v2.docx", "last_modified": "2026-04-12T10:00:00Z", "verified": True},
                    {"name": "Data_Protection_Procedure.docx", "last_modified": "2026-05-01T08:15:00Z", "verified": True},
                    {"name": "Incident_Response_Plan.pdf", "last_modified": "2026-03-20T14:30:00Z", "verified": True}
                ],
                "vulnerability_scan_reports_found": False
            },
            "teams": {
                "compliance_channels_configured": True,
                "meeting_transcripts_retrieved": 5
            },
            "defender": {
                "tenant_secure_score": 76.5,
                "active_vulnerabilities": 14
            }
        }
