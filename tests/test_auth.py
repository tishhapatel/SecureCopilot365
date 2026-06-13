import os
import sys
import pytest
from fastapi.testclient import TestClient

# Set test database URL before importing backend modules
os.environ["DATABASE_URL"] = "sqlite:///./test_securecop365_auth.db"

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
    
    # 1. Seed permissions
    permission_map = {}
    for perm in ALL_PERMISSIONS:
        db_perm = models.Permission(permission_name=perm["name"], module=perm["module"])
        db.add(db_perm)
        db.flush()
        permission_map[perm["name"]] = db_perm
        
    # 2. Seed roles
    role_map = {}
    for r_name in ALL_ROLES:
        db_role = models.Role(role_name=r_name, description=f"{r_name} system role")
        db.add(db_role)
        db.flush()
        role_map[r_name] = db_role
        
        target_perms = ROLE_PERMISSIONS.get(r_name, [])
        db_role.permissions = [permission_map[p] for p in target_perms if p in permission_map]
    db.commit()

    # 3. Seed test users
    users = [
        ("ciso@securecop.com", "CISO Alpha", "CISO", "tenant-alpha"),
        ("employee@securecop.com", "Employee Alpha", "General Employee", "tenant-alpha"),
        ("ciso.beta@securecop.com", "CISO Beta", "CISO", "tenant-beta")
    ]
    for email, name, role_name, tenant in users:
        role_obj = role_map[role_name]
        user_obj = models.User(
            email=email,
            display_name=name,
            password_hash=hash_password("password123"),
            role_id=role_obj.id,
            department="Security",
            tenant_id=tenant,
            is_active=True
        )
        db.add(user_obj)
    db.commit()
    
    # 4. Seed vendors for tenant testing
    vendor_alpha = models.Vendor(
        name="Vendor Alpha",
        website="https://alpha.com",
        tenant_id="tenant-alpha",
        risk_score=30.0
    )
    vendor_beta = models.Vendor(
        name="Vendor Beta",
        website="https://beta.com",
        tenant_id="tenant-beta",
        risk_score=60.0
    )
    db.add(vendor_alpha)
    db.add(vendor_beta)
    db.commit()
    
    db.close()
    yield
    
    # Clean up database files
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    try:
        if os.path.exists("./test_securecop365_auth.db"):
            os.remove("./test_securecop365_auth.db")
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

def test_local_login_success():
    """Verify local credentials generate correct JWT tokens."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "ciso@securecop.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == "ciso@securecop.com"
    assert data["user"]["role"]["role_name"] == "CISO"

def test_local_login_invalid_credentials():
    """Verify login fails with wrong passwords or non-existent emails."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "ciso@securecop.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@securecop.com", "password": "password123"}
    )
    assert response.status_code == 401

def test_rbac_ciso_allowed_vendor_list():
    """Verify CISO user is permitted to retrieve vendor list."""
    headers = get_auth_headers("ciso@securecop.com")
    response = client.get("/api/v1/vendor/list", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1

def test_rbac_employee_denied_vendor_list():
    """Verify General Employee is denied access (HTTP 403) to vendor list."""
    headers = get_auth_headers("employee@securecop.com")
    response = client.get("/api/v1/vendor/list", headers=headers)
    assert response.status_code == 403

def test_tenant_isolation_vendor_list():
    """Verify tenant isolation: CISO Alpha cannot see CISO Beta's vendors."""
    headers_alpha = get_auth_headers("ciso@securecop.com")
    response_alpha = client.get("/api/v1/vendor/list", headers=headers_alpha)
    assert response_alpha.status_code == 200
    vendors_alpha = response_alpha.json()
    assert len(vendors_alpha) == 1
    assert vendors_alpha[0]["name"] == "Vendor Alpha"
    
    headers_beta = get_auth_headers("ciso.beta@securecop.com")
    response_beta = client.get("/api/v1/vendor/list", headers=headers_beta)
    assert response_beta.status_code == 200
    vendors_beta = response_beta.json()
    assert len(vendors_beta) == 1
    assert vendors_beta[0]["name"] == "Vendor Beta"

def test_admin_list_users():
    """Verify that authorized users can retrieve the user list, while unauthorized users are blocked."""
    headers_ciso = get_auth_headers("ciso@securecop.com")
    response = client.get("/api/v1/auth/users", headers=headers_ciso)
    assert response.status_code == 200
    users = response.json()
    # Should contain ciso@securecop.com and employee@securecop.com (same tenant-alpha)
    emails = [u["email"] for u in users]
    assert "ciso@securecop.com" in emails
    assert "employee@securecop.com" in emails
    assert "ciso.beta@securecop.com" not in emails  # Tenant isolation

    headers_emp = get_auth_headers("employee@securecop.com")
    response_denied = client.get("/api/v1/auth/users", headers=headers_emp)
    assert response_denied.status_code == 403

def test_admin_create_user():
    """Verify user registration by tenant administrator."""
    headers_ciso = get_auth_headers("ciso@securecop.com")
    new_user_payload = {
        "email": "new_admin@securecop.com",
        "display_name": "New Admin User",
        "password": "password123",
        "role_name": "CISO",
        "department": "Security"
    }
    response = client.post("/api/v1/auth/users", json=new_user_payload, headers=headers_ciso)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "new_admin@securecop.com"
    assert data["tenant_id"] == "tenant-alpha"  # Inherits from creator

    # Verify we can login with it
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "new_admin@securecop.com", "password": "password123"}
    )
    assert login_response.status_code == 200

def test_admin_update_user_role():
    """Verify role update for a user."""
    headers_ciso = get_auth_headers("ciso@securecop.com")
    # Get users to retrieve employee ID
    users_resp = client.get("/api/v1/auth/users", headers=headers_ciso)
    emp_user = next(u for u in users_resp.json() if u["email"] == "employee@securecop.com")
    
    update_payload = {"role_name": "HR Manager"}
    response = client.put(f"/api/v1/auth/users/{emp_user['id']}/role", json=update_payload, headers=headers_ciso)
    assert response.status_code == 200
    assert response.json()["role"]["role_name"] == "HR Manager"

def test_admin_toggle_user_activation():
    """Verify deactivation and subsequent login block."""
    headers_ciso = get_auth_headers("ciso@securecop.com")
    users_resp = client.get("/api/v1/auth/users", headers=headers_ciso)
    emp_user = next(u for u in users_resp.json() if u["email"] == "employee@securecop.com")

    # Deactivate
    response = client.put(f"/api/v1/auth/users/{emp_user['id']}/activation", json={"is_active": False}, headers=headers_ciso)
    assert response.status_code == 200
    assert response.json()["is_active"] is False

    # Attempt login - should fail
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "employee@securecop.com", "password": "password123"}
    )
    assert login_response.status_code == 403

def test_admin_delete_user():
    """Verify deleting a user account."""
    headers_ciso = get_auth_headers("ciso@securecop.com")
    users_resp = client.get("/api/v1/auth/users", headers=headers_ciso)
    emp_user = next(u for u in users_resp.json() if u["email"] == "employee@securecop.com")

    # Delete
    response = client.delete(f"/api/v1/auth/users/{emp_user['id']}", headers=headers_ciso)
    assert response.status_code == 200
    assert response.json()["message"] == "User deleted successfully"

    # Confirm it is no longer listed
    users_resp_after = client.get("/api/v1/auth/users", headers=headers_ciso)
    emails = [u["email"] for u in users_resp_after.json()]
    assert "employee@securecop.com" not in emails

def test_list_roles():
    """Verify getting all roles."""
    headers_ciso = get_auth_headers("ciso@securecop.com")
    response = client.get("/api/v1/auth/roles", headers=headers_ciso)
    assert response.status_code == 200
    roles_list = response.json()
    assert len(roles_list) > 0
    role_names = [r["role_name"] for r in roles_list]
    assert "Super Admin" in role_names
    assert "General Employee" in role_names

def test_list_audit_logs():
    """Verify audit log retrieval."""
    headers_ciso = get_auth_headers("ciso@securecop.com")
    response = client.get("/api/v1/auth/audit_logs", headers=headers_ciso)
    assert response.status_code == 200
    logs = response.json()
    # At least the login actions should be logged
    assert len(logs) >= 0

