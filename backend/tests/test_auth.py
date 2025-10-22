"""Tests for shared.auth module."""

import pytest
from shared.auth import get_claims_from_event, require_scope


def test_get_claims_from_event_success():
    """Test extracting claims from a valid API Gateway event."""
    event = {
        "requestContext": {
            "authorizer": {
                "jwt": {
                    "claims": {
                        "sub": "user123",
                        "scope": "agent:read agent:actions",
                        "email": "user@example.com",
                    }
                }
            }
        }
    }
    
    claims = get_claims_from_event(event)
    assert claims["sub"] == "user123"
    assert claims["scope"] == "agent:read agent:actions"
    assert claims["email"] == "user@example.com"


def test_get_claims_from_event_missing():
    """Test that missing claims raises KeyError."""
    event = {"requestContext": {}}
    
    with pytest.raises(KeyError, match="JWT claims not found"):
        get_claims_from_event(event)


def test_require_scope_success():
    """Test require_scope decorator allows access when scope present."""
    @require_scope("agent:actions")
    def handler(event, context):
        return {"statusCode": 200, "body": "OK"}
    
    event = {
        "requestContext": {
            "authorizer": {
                "jwt": {
                    "claims": {
                        "sub": "user123",
                        "scope": "agent:read agent:actions",
                    }
                }
            }
        }
    }
    
    response = handler(event, None)
    assert response["statusCode"] == 200


def test_require_scope_denied():
    """Test require_scope decorator denies access when scope missing."""
    @require_scope("agent:actions")
    def handler(event, context):
        return {"statusCode": 200, "body": "OK"}
    
    event = {
        "requestContext": {
            "authorizer": {
                "jwt": {
                    "claims": {
                        "sub": "user123",
                        "scope": "agent:read",  # Missing agent:actions
                    }
                }
            }
        }
    }
    
    response = handler(event, None)
    assert response["statusCode"] == 401
    assert "Insufficient permissions" in response["body"]


def test_require_scope_no_claims():
    """Test require_scope decorator handles missing claims gracefully."""
    @require_scope("agent:actions")
    def handler(event, context):
        return {"statusCode": 200, "body": "OK"}
    
    event = {"requestContext": {}}
    
    response = handler(event, None)
    assert response["statusCode"] == 401
    assert "Missing or invalid JWT claims" in response["body"]


def test_require_scope_empty_scope():
    """Test require_scope decorator handles empty scope claim."""
    @require_scope("agent:actions")
    def handler(event, context):
        return {"statusCode": 200, "body": "OK"}
    
    event = {
        "requestContext": {
            "authorizer": {
                "jwt": {
                    "claims": {
                        "sub": "user123",
                        "scope": "",  # Empty scope
                    }
                }
            }
        }
    }
    
    response = handler(event, None)
    assert response["statusCode"] == 401
