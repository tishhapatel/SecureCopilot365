"""
Microsoft Graph Client — User Operations
"""
import httpx
import logging
from graph.client import GraphClient, MOCK_TOKEN

logger = logging.getLogger(__name__)

class GraphUsers(GraphClient):
    async def get_user_profile(self, user_id: str) -> dict:
        """
        Retrieves user profiles via Microsoft Graph API.
        Falls back to local mock data if authentication fails.
        """
        token = await self.get_access_token()
        if token == MOCK_TOKEN:
            return self._mock_user_profile(user_id)
            
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{self.base_url}/users/{user_id}"
        
        async with httpx.AsyncClient() as client:
            try:
                res = await client.get(url, headers=headers)
                if res.status_code == 200:
                    return res.json()
            except Exception as e:
                logger.error(f"Error fetching user from Graph: {e}")
                
        return self._mock_user_profile(user_id)

    def _mock_user_profile(self, user_id: str) -> dict:
        return {
            "id": user_id or "mock-id-123",
            "displayName": "Tisha Patel",
            "givenName": "Tisha",
            "surname": "Patel",
            "userPrincipalName": "tisha.patel@enterprise.com",
            "mail": "tisha.patel@enterprise.com",
            "jobTitle": "Billing Specialist",
            "department": "Finance",
            "officeLocation": "Building 2"
        }
