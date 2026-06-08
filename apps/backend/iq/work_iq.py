"""
Work IQ Layer
Resolves organization context, employee profile, and department rules.
"""
import logging
from db.database import SessionLocal
from db.models import Employee

logger = logging.getLogger(__name__)

class WorkIQ:
    def get_user_profile(self, user_id: str) -> dict:
        """
        Retrieves user information from local DB or returns a default context.
        """
        db = SessionLocal()
        try:
            emp = db.query(Employee).filter(Employee.entra_id == user_id).first()
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
                    "tenant_id": "default_tenant"
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
