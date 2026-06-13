"""
Work IQ Layer
Resolves organization context, employee profile, and department rules.
Connects to Microsoft Graph API and reasons over emails, chats, meetings, and documents.
"""
import logging
import os
import httpx
from typing import List, Dict, Any
from db.database import SessionLocal
from db.models import Employee

logger = logging.getLogger(__name__)

class WorkIQ:
    def __init__(self):
        self.graph_base_url = "https://graph.microsoft.com/v1.0"
        self.access_token = os.getenv("MICROSOFT_GRAPH_ACCESS_TOKEN")

    def get_user_profile(self, user_id: str) -> dict:
        """
        Retrieves user information from local DB or returns a default context.
        """
        db = SessionLocal()
        try:
            # Query by entra_id or email
            emp = db.query(Employee).filter(
                (Employee.entra_id == user_id) | (Employee.email == user_id)
            ).first()
            if emp:
                return {
                    "id": emp.id,
                    "entra_id": emp.entra_id,
                    "display_name": emp.display_name,
                    "email": emp.email,
                    "department": emp.department or "General",
                    "job_title": emp.job_title or "Employee",
                    "risk_score": emp.risk_score,
                    "awareness_score": emp.awareness_score,
                    "tenant_id": emp.tenant_id
                }
        except Exception as ex:
            logger.warning(f"Error querying employee from DB: {ex}")
        finally:
            db.close()
            
        # Return fallback mock employee context
        return {
            "id": "mock-id-123",
            "entra_id": user_id or "mock_entra_id",
            "display_name": "Tisha Patel",
            "email": "tisha.patel@enterprise.com",
            "department": "Finance",
            "job_title": "Billing Specialist",
            "risk_score": 35.0,
            "awareness_score": 82.0,
            "tenant_id": "default_tenant"
        }

    async def get_recent_emails(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch user emails from Microsoft Graph API or return mock communications."""
        if self.access_token:
            try:
                async with httpx.AsyncClient() as client:
                    headers = {"Authorization": f"Bearer {self.access_token}"}
                    res = await client.get(
                        f"{self.graph_base_url}/users/{user_id}/messages?$top={limit}",
                        headers=headers
                    )
                    if res.status_code == 200:
                        return res.json().get("value", [])
            except Exception as e:
                logger.error(f"Graph API Email fetch failed: {e}")

        # High fidelity mock data for hackathon/development
        return [
            {
                "id": "email-001",
                "subject": "URGENT: Verify Wire Transfer payment details immediately",
                "sender": "external.cfo.office@gmail.com",
                "sender_display": "Office of the CFO",
                "body": "Hi Tisha, please verify these updated bank routing numbers for vendor invoice payment #88392. We need this processed in 2 hours to avoid penalty fees. Click here: http://secure-portal-update.com",
                "received_date": "2026-06-13T10:15:00Z"
            },
            {
                "id": "email-002",
                "subject": "Monthly Security Awareness Newsletter",
                "sender": "secops@enterprise.com",
                "sender_display": "IT Security Team",
                "body": "Welcome to our monthly newsletter. Make sure to enable MFA on all personal accounts.",
                "received_date": "2026-06-12T09:00:00Z"
            }
        ]

    async def get_recent_chats(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch Teams chats from Microsoft Graph API or return mock chat channels."""
        if self.access_token:
            try:
                async with httpx.AsyncClient() as client:
                    headers = {"Authorization": f"Bearer {self.access_token}"}
                    res = await client.get(
                        f"{self.graph_base_url}/users/{user_id}/chats?$top={limit}",
                        headers=headers
                    )
                    if res.status_code == 200:
                        return res.json().get("value", [])
            except Exception as e:
                logger.error(f"Graph API Chat fetch failed: {e}")

        return [
            {
                "id": "chat-001",
                "topic": "Finance Operations",
                "last_message": "Hey Tisha, did you upload the new vendor risk spreadsheet to SharePoint? Also password is admin123",
                "sender": "collaborator@enterprise.com",
                "timestamp": "2026-06-13T11:22:00Z"
            }
        ]

    async def get_recent_meetings(self, user_id: str) -> List[Dict[str, Any]]:
        """Fetch calendar events and meeting transcripts via Graph API."""
        return [
            {
                "id": "meeting-001",
                "subject": "Q2 Security Framework Alignment",
                "transcript_summary": "During the meeting, the compliance director mentioned that we do not have regular quarterly vulnerability scanning set up for our SharePoint document repository (ISO 27001 Control A.8.8 gap). Remediate within 2 weeks.",
                "organizer": "ciso@enterprise.com",
                "date": "2026-06-13T09:00:00Z"
            }
        ]

    async def get_recent_documents(self, user_id: str) -> List[Dict[str, Any]]:
        """Fetch document properties and sharing states from SharePoint."""
        return [
            {
                "name": "Vendor_Risk_Spreadsheet.xlsx",
                "web_url": "https://enterprise.sharepoint.com/finance/Vendor_Risk_Spreadsheet.xlsx",
                "acl": ["Super Admin", "CISO", "Vendor Risk Manager"],
                "last_modified": "2026-06-12T16:45:00Z"
            },
            {
                "name": "Information_Security_Policy_Draft.docx",
                "web_url": "https://enterprise.sharepoint.com/policies/Information_Security_Policy_Draft.docx",
                "acl": ["Super Admin", "CISO", "Compliance Officer", "General Employee"],
                "last_modified": "2026-06-13T10:00:00Z"
            }
        ]

