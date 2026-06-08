"""
Role-Based Access Control (RBAC)
"""
from fastapi import HTTPException, Request

class RoleChecker:
    def __init__(self, allowed_departments: list = None, allowed_titles: list = None):
        self.allowed_departments = allowed_departments
        self.allowed_titles = allowed_titles

    def __call__(self, request: Request):
        user = getattr(request.state, "user", None)
        if not user:
            raise HTTPException(status_code=401, detail="User not authenticated")
            
        dept = user.get("department", "").lower()
        title = user.get("job_title", "").lower()
        
        # Admin bypass
        if "admin" in title or "ciso" in title:
            return user

        if self.allowed_departments:
            dept_matches = any(d.lower() in dept for d in self.allowed_departments)
            if not dept_matches:
                raise HTTPException(status_code=403, detail="Access denied: departmental restriction")
                
        if self.allowed_titles:
            title_matches = any(t.lower() in title for t in self.allowed_titles)
            if not title_matches:
                raise HTTPException(status_code=403, detail="Access denied: job title restriction")
                
        return user
