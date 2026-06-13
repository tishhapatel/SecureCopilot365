"""
Azure Entra ID SSO & OAuth 2.0 helper operations for SecureCopilot 365.
"""
import os
import httpx
from typing import Optional

class EntraIDAuth:
    def __init__(self):
        self.tenant_id = os.getenv("ENTRA_TENANT_ID")
        self.client_id = os.getenv("ENTRA_CLIENT_ID")
        self.client_secret = os.getenv("ENTRA_CLIENT_SECRET")
        self.redirect_uri = os.getenv("ENTRA_REDIRECT_URI", "http://localhost:5173/login")
        
    def get_authorization_url(self) -> str:
        """Get the Microsoft Entra ID authorization redirect URL."""
        if not self.client_id or not self.tenant_id:
            # Fallback mock SSO redirect endpoint
            return "http://localhost:5173/login?mock_sso=true"
        
        # Standard Microsoft OAuth authorize redirect URL
        return (
            f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/authorize"
            f"?client_id={self.client_id}"
            f"&response_type=code"
            f"&redirect_uri={self.redirect_uri}"
            f"&response_mode=query"
            f"&scope=User.Read"
        )

    async def exchange_code_for_user(self, code: str) -> Optional[dict]:
        """Exchange authorization code for Microsoft Graph user profile details."""
        if not self.client_id or not self.client_secret or not self.tenant_id or code == "mock-code":
            # Return developer mock user context
            return {
                "entra_id": "mock-entra-id-123",
                "display_name": "Tisha Patel",
                "email": "tisha.patel@enterprise.com",
                "department": "Finance",
                "job_title": "Billing Specialist",
                "tenant_id": "tenant-alpha"
            }
            
        async with httpx.AsyncClient() as client:
            token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": code,
                "redirect_uri": self.redirect_uri,
                "grant_type": "authorization_code",
                "scope": "User.Read"
            }
            try:
                res = await client.post(token_url, data=data)
                if res.status_code != 200:
                    return None
                tokens = res.json()
                access_token = tokens.get("access_token")
                
                # Retrieve user details from Microsoft Graph API
                graph_res = await client.get(
                    "https://graph.microsoft.com/v1.0/me",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                if graph_res.status_code != 200:
                    return None
                profile = graph_res.json()
                return {
                    "entra_id": profile.get("id"),
                    "display_name": profile.get("displayName"),
                    "email": profile.get("mail") or profile.get("userPrincipalName"),
                    "department": profile.get("department") or "General",
                    "job_title": profile.get("jobTitle") or "Employee",
                    "tenant_id": self.tenant_id
                }
            except Exception:
                return None
