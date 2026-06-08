from fastapi import Depends, Request
from sqlalchemy.orm import Session
from db.database import get_db

def get_current_user(request: Request):
    """
    Returns the authenticated user injected by EntraIDMiddleware.
    """
    return getattr(request.state, "user", None)
