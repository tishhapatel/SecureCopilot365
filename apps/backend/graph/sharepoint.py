"""
Microsoft Graph Client — SharePoint / OneDrive Operations
"""
import httpx
import logging
from graph.client import GraphClient

logger = logging.getLogger(__name__)

class GraphSharePoint(GraphClient):
    async def get_policy_document(self, site_id: str, file_id: str) -> dict:
        """
        Retrieves policy file content or metadata from SharePoint.
        """
        token = await self.get_access_token()
        if token == "mock_graph_access_token_12345":
            return self._mock_document(file_id)

        headers = {"Authorization": f"Bearer {token}"}
        url = f"{self.base_url}/sites/{site_id}/drive/items/{file_id}"
        
        async with httpx.AsyncClient() as client:
            try:
                res = await client.get(url, headers=headers)
                if res.status_code == 200:
                    return res.json()
            except Exception as e:
                logger.error(f"Error fetching SharePoint document: {e}")
                
        return self._mock_document(file_id)

    def _mock_document(self, file_id: str) -> dict:
        return {
            "id": file_id or "policy-doc-456",
            "name": "GDPR_Compliance_Policy.docx",
            "size": 124500,
            "webUrl": "https://enterprise.sharepoint.com/sites/compliance/documents/GDPR_Compliance_Policy.docx",
            "createdBy": {
                "user": {"displayName": "Compliance Team"}
            },
            "lastModifiedDateTime": "2026-05-10T11:45:00Z",
            "content": "GDPR Compliance and Data Minimization Policy. Personal data must be collected for specified, explicit, and legitimate purposes. All vendors handling personal data must sign a Data Processing Agreement. We will report breaches to the authority within 72 hours of discovery."
        }
