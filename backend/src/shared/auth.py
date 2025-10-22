"""Authentication utilities for API Gateway Lambda handlers.

Note: API Gateway JWT Authorizer has already validated the token.
These utilities extract claims from the validated token and enforce scope requirements.
"""

from typing import Any, Callable, Dict, Optional
from functools import wraps
import json

from shared.responses import unauthorized


def get_claims_from_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """Extract JWT claims from API Gateway HTTP API event.
    
    API Gateway JWT Authorizer places validated claims in:
    - event["requestContext"]["authorizer"]["jwt"]["claims"]
    
    Args:
        event: API Gateway HTTP API event dict
        
    Returns:
        Dict of JWT claims (sub, scope, custom claims, etc.)
        
    Raises:
        KeyError: If claims are not present in the expected location
    """
    try:
        claims = event["requestContext"]["authorizer"]["jwt"]["claims"]
        return claims
    except KeyError as e:
        raise KeyError(
            f"JWT claims not found in event. Expected at requestContext.authorizer.jwt.claims. Error: {e}"
        ) from e


def require_scope(required_scope: str) -> Callable:
    """Decorator to enforce scope requirement on Lambda handler.
    
    Checks if the JWT 'scope' claim contains the required scope.
    Scope claim is expected to be a space-separated string (OAuth2 convention).
    
    Args:
        required_scope: The scope string to require (e.g., "agent:actions")
        
    Returns:
        Decorated handler function
        
    Example:
        @require_scope("agent:actions")
        def handler(event, context):
            # This handler requires "agent:actions" scope
            return {"statusCode": 200, "body": "OK"}
    """
    def decorator(handler: Callable) -> Callable:
        @wraps(handler)
        def wrapper(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
            try:
                claims = get_claims_from_event(event)
            except KeyError:
                return unauthorized("Missing or invalid JWT claims")
            
            # Extract scope claim (space-separated string)
            scope_claim = claims.get("scope", "")
            scopes = scope_claim.split() if isinstance(scope_claim, str) else []
            
            if required_scope not in scopes:
                return unauthorized(
                    f"Insufficient permissions. Required scope: {required_scope}"
                )
            
            # Scope check passed, invoke handler
            return handler(event, context)
        
        return wrapper
    return decorator
