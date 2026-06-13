import os
import sys
import pytest
from fastapi.testclient import TestClient

# Set test database URL before importing backend modules
os.environ["DATABASE_URL"] = "sqlite:///./test_securecop365_scim.db"

# Adjust path to import backend modules
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "apps", "backend"))

from main import app
from db.database import engine, SessionLocal
from db.models import Base

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    # Clean up and recreate database tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    from db import models
    from auth.roles import ALL_ROLES
    from auth.permissions import ALL_PERMISSIONS, ROLE_PERMISSIONS
    from auth.jwt_handler import hash_password
    
    # Seed permissions
    permission_map = {}
    for perm in ALL_PERMISSIONS:
        db_perm = models.Permission(permission_name=perm["name"], module=perm["module"])
        db.add(db_perm)
        db.flush()
        permission_map[perm["name"]] = db_perm
        
    # Seed roles
    role_map = {}
    for r_name in ALL_ROLES:
        db_role = models.Role(role_name=r_name, description=f"{r_name} system role")
        db.add(db_role)
        db.flush()
        role_map[r_name] = db_role
        
        target_perms = ROLE_PERMISSIONS.get(r_name, [])
        db_role.permissions = [permission_map[p] for p in target_perms if p in permission_map]
    db.commit()

    # Seed CISO User for admin permissions
    ciso_role = role_map["CISO"]
    user_obj = models.User(
        email="ciso@securecop.com",
        display_name="CISO User",
        password_hash=hash_password("password123"),
        role_id=ciso_role.id,
        department="Security",
        tenant_id="tenant-alpha",
        is_active=True
    )
    db.add(user_obj)
    db.commit()
    db.close()
    yield
    
    # Clean up database files
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    try:
        if os.path.exists("./test_securecop365_scim.db"):
            os.remove("./test_securecop365_scim.db")
    except Exception:
        pass

def get_auth_headers(email: str, password: str = "password123") -> dict:
    """Helper to authenticate a user and return request headers."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_scim_endpoints_flow():
    headers = get_auth_headers("ciso@securecop.com")
    
    # 1. List SCIM users (should contain at least our CISO)
    list_res = client.get("/api/v1/scim/v2/Users", headers=headers)
    assert list_res.status_code == 200
    data = list_res.json()
    assert data["totalResults"] == 1
    assert data["Resources"][0]["userName"] == "ciso@securecop.com"

    # 2. Create SCIM user
    new_user_payload = {
        "userName": "scim_user@securecop.com",
        "name": {
            "formatted": "Scim Employee"
        },
        "emails": [
            {
                "value": "scim_user@securecop.com",
                "primary": True
            }
        ],
        "department": "Engineering"
    }
    create_res = client.post("/api/v1/scim/v2/Users", json=new_user_payload, headers=headers)
    assert create_res.status_code == 201
    created_data = create_res.json()
    assert created_data["userName"] == "scim_user@securecop.com"
    user_id = created_data["id"]

    # 3. Create SCIM user again (should raise 409 conflict)
    create_conflict_res = client.post("/api/v1/scim/v2/Users", json=new_user_payload, headers=headers)
    assert create_conflict_res.status_code == 409

    # 4. Patch user active state to False
    patch_payload = {
        "Operations": [
            {
                "op": "replace",
                "value": {
                    "active": False
                }
            }
        ]
    }
    patch_res = client.patch(f"/api/v1/scim/v2/Users/{user_id}", json=patch_payload, headers=headers)
    assert patch_res.status_code == 204

    # 5. Delete SCIM user
    delete_res = client.delete(f"/api/v1/scim/v2/Users/{user_id}", headers=headers)
    assert delete_res.status_code == 204

    # 6. Delete SCIM user again (should raise 404 not found)
    delete_not_found = client.delete(f"/api/v1/scim/v2/Users/{user_id}", headers=headers)
    assert delete_not_found.status_code == 404
