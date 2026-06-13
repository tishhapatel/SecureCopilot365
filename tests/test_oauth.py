import os
import sys
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Adjust path to import backend modules
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "apps", "backend"))

from auth.oauth import EntraIDAuth

def test_oauth_auth_url_mock():
    # Test when client_id or tenant_id is not set
    auth = EntraIDAuth()
    auth.client_id = None
    auth.tenant_id = None
    url = auth.get_authorization_url()
    assert "mock_sso=true" in url

def test_oauth_auth_url_real():
    auth = EntraIDAuth()
    auth.client_id = "real_client_id"
    auth.tenant_id = "real_tenant_id"
    url = auth.get_authorization_url()
    assert "https://login.microsoftonline.com/real_tenant_id/oauth2/v2.0/authorize" in url
    assert "client_id=real_client_id" in url

@pytest.mark.asyncio
async def test_exchange_code_for_user_mock():
    auth = EntraIDAuth()
    # Should fall back to mock user profile if code is "mock-code"
    profile = await auth.exchange_code_for_user("mock-code")
    assert profile is not None
    assert profile["email"] == "tisha.patel@enterprise.com"
    assert profile["tenant_id"] == "tenant-alpha"

@pytest.mark.asyncio
async def test_exchange_code_for_user_real_success():
    auth = EntraIDAuth()
    auth.client_id = "real_client_id"
    auth.client_secret = "real_client_secret"
    auth.tenant_id = "real_tenant_id"
    
    # Mock HTTP response for token exchange and /me graph call
    mock_token_res = MagicMock()
    mock_token_res.status_code = 200
    mock_token_res.json.return_value = {"access_token": "valid_token"}
    
    mock_graph_res = MagicMock()
    mock_graph_res.status_code = 200
    mock_graph_res.json.value = {
        "id": "graph-id-abc",
        "displayName": "Test OAuth User",
        "mail": "oauth_user@enterprise.com",
        "department": "IT Support",
        "jobTitle": "Support Technician"
    }
    mock_graph_res.json.return_value = mock_graph_res.json.value

    mock_post = AsyncMock(return_value=mock_token_res)
    mock_get = AsyncMock(return_value=mock_graph_res)

    with patch("httpx.AsyncClient.post", mock_post), \
         patch("httpx.AsyncClient.get", mock_get):
         
        profile = await auth.exchange_code_for_user("auth-code-123")
        assert profile is not None
        assert profile["entra_id"] == "graph-id-abc"
        assert profile["email"] == "oauth_user@enterprise.com"
        assert profile["job_title"] == "Support Technician"
        assert profile["tenant_id"] == "real_tenant_id"

@pytest.mark.asyncio
async def test_exchange_code_for_user_token_failure():
    auth = EntraIDAuth()
    auth.client_id = "real_client_id"
    auth.client_secret = "real_client_secret"
    auth.tenant_id = "real_tenant_id"
    
    mock_token_res = MagicMock()
    mock_token_res.status_code = 400
    mock_post = AsyncMock(return_value=mock_token_res)

    with patch("httpx.AsyncClient.post", mock_post):
        profile = await auth.exchange_code_for_user("invalid-code")
        assert profile is None

@pytest.mark.asyncio
async def test_exchange_code_for_user_graph_failure():
    auth = EntraIDAuth()
    auth.client_id = "real_client_id"
    auth.client_secret = "real_client_secret"
    auth.tenant_id = "real_tenant_id"
    
    mock_token_res = MagicMock()
    mock_token_res.status_code = 200
    mock_token_res.json.return_value = {"access_token": "valid_token"}
    
    mock_graph_res = MagicMock()
    mock_graph_res.status_code = 401
    
    mock_post = AsyncMock(return_value=mock_token_res)
    mock_get = AsyncMock(return_value=mock_graph_res)

    with patch("httpx.AsyncClient.post", mock_post), \
         patch("httpx.AsyncClient.get", mock_get):
         
        profile = await auth.exchange_code_for_user("auth-code-123")
        assert profile is None
