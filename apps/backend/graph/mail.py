"""
Microsoft Graph Client — Mail Operations
"""
import httpx
import logging
from graph.client import GraphClient, MOCK_TOKEN

logger = logging.getLogger(__name__)

class GraphMail(GraphClient):
    async def get_message(self, user_id: str, message_id: str) -> dict:
        """
        Retrieves a specific email body and headers.
        Falls back to realistic mock phishing email.
        """
        token = await self.get_access_token()
        if token == MOCK_TOKEN:
            return self._mock_message(message_id)

        headers = {"Authorization": f"Bearer {token}"}
        url = f"{self.base_url}/users/{user_id}/messages/{message_id}"
        
        async with httpx.AsyncClient() as client:
            try:
                res = await client.get(url, headers=headers)
                if res.status_code == 200:
                    return res.json()
            except Exception as e:
                logger.error(f"Error fetching message from Graph: {e}")
                
        return self._mock_message(message_id)

    def _mock_message(self, message_id: str) -> dict:
        return {
            "id": message_id,
            "subject": "URGENT: Verify your billing account password immediately",
            "bodyPreview": "Dear employee, we detected a login from a new IP address. Please click here immediately to verify.",
            "body": {
                "contentType": "html",
                "content": "Dear customer, <p>We detected suspicious activity. Please click <a href='http://micros0ft-billing-check.com/login'>here</a> to resolve.</p>"
            },
            "sender": {
                "emailAddress": {
                    "name": "Microsoft Support Desk",
                    "address": "support@micros0ft-billing-check.com"
                }
            },
            "from": {
                "emailAddress": {
                    "name": "Microsoft Support Desk",
                    "address": "support@micros0ft-billing-check.com"
                }
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "name": "Tisha Patel",
                        "address": "tisha.patel@enterprise.com"
                    }
                }
            ],
            "replyTo": [
                {
                    "emailAddress": {
                        "name": "Support Mismatch",
                        "address": "attacker-inbox@gmail.com"
                    }
                }
            ],
            "hasAttachments": True
        }
