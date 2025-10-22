"""Tests for shared.responses module."""

import json
from shared.responses import ok, bad_request, unauthorized, server_error


def test_ok_default():
    """Test ok() with default 200 status."""
    response = ok({"result": "success"})
    
    assert response["statusCode"] == 200
    assert "Access-Control-Allow-Origin" in response["headers"]
    assert response["headers"]["Access-Control-Allow-Origin"] == "*"
    assert response["headers"]["Content-Type"] == "application/json"
    
    body = json.loads(response["body"])
    assert body["result"] == "success"


def test_ok_custom_status():
    """Test ok() with custom status code."""
    response = ok({"created": True}, status_code=201)
    assert response["statusCode"] == 201


def test_bad_request():
    """Test bad_request() response."""
    response = bad_request("Invalid input", details={"field": "email"})
    
    assert response["statusCode"] == 400
    assert "Access-Control-Allow-Origin" in response["headers"]
    
    body = json.loads(response["body"])
    assert body["error"] == "Invalid input"
    assert body["details"]["field"] == "email"


def test_unauthorized():
    """Test unauthorized() response."""
    response = unauthorized("Token expired")
    
    assert response["statusCode"] == 401
    assert "Access-Control-Allow-Origin" in response["headers"]
    
    body = json.loads(response["body"])
    assert body["error"] == "Token expired"


def test_server_error():
    """Test server_error() response."""
    response = server_error("Database connection failed")
    
    assert response["statusCode"] == 500
    assert "Access-Control-Allow-Origin" in response["headers"]
    
    body = json.loads(response["body"])
    assert body["error"] == "Database connection failed"


def test_cors_headers_consistency():
    """Verify all response helpers include consistent CORS headers."""
    responses = [
        ok({}),
        bad_request(),
        unauthorized(),
        server_error(),
    ]
    
    for resp in responses:
        headers = resp["headers"]
        assert "Access-Control-Allow-Origin" in headers
        assert "Access-Control-Allow-Methods" in headers
        assert "Access-Control-Allow-Headers" in headers
