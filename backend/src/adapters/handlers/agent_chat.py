"""Lambda handler: POST /agent/chat

Invokes Amazon Bedrock Agent Runtime for conversational AI interactions.
"""

import json
from typing import Any, Dict

from pydantic import BaseModel, Field
from loguru import logger
import boto3
from botocore.exceptions import ClientError

from shared.auth import get_claims_from_event
from shared.responses import ok, bad_request, server_error
from shared.settings import get_settings


class ChatRequest(BaseModel):
    """Request model for agent chat."""
    
    message: str = Field(description="User message to send to agent")
    session_id: str = Field(default="default", description="Session identifier for conversation continuity")


class ChatResponse(BaseModel):
    """Response model for agent chat."""
    
    response: str = Field(description="Agent response text")
    session_id: str = Field(description="Session identifier")
    trace: Dict[str, Any] = Field(default_factory=dict, description="Trace information (optional)")


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for Bedrock Agent chat.
    
    Invokes Bedrock Agent Runtime to process user messages and return responses.
    Requires AGENT_ID and AGENT_ALIAS_ID environment variables.
    
    Request Body:
        {
            "message": "What are the current KPIs?",
            "session_id": "user-123-session"  // optional
        }
        
    Returns:
        API Gateway response with agent's reply
    """
    try:
        # Extract claims
        try:
            claims = get_claims_from_event(event)
            user_id = claims.get("sub", "unknown")
            logger.info(f"Agent chat request from user: {user_id}")
        except KeyError:
            logger.warning("No JWT claims found in request")
            user_id = "anonymous"
        
        # Parse request body
        body = event.get("body", "{}")
        if isinstance(body, str):
            body = json.loads(body)
        
        # Validate request with Pydantic
        try:
            request_data = ChatRequest(**body)
        except Exception as e:
            return bad_request(f"Invalid request body: {e}")
        
        if not request_data.message.strip():
            return bad_request("Message cannot be empty")
        
        logger.debug(f"Processing chat message: {request_data.message[:50]}...")
        
        # Get agent configuration from environment
        settings = get_settings()
        agent_id = settings.agent_id or ""
        agent_alias_id = settings.agent_alias_id or ""
        
        # Note: For demo purposes, using placeholder values
        # In production, these should come from environment variables
        if not agent_id or not agent_alias_id:
            logger.warning("AGENT_ID or AGENT_ALIAS_ID not configured, returning mock response")
            # Return mock response for now
            response_data = ChatResponse(
                response=f"Mock response to: {request_data.message}",
                session_id=request_data.session_id,
                trace={"note": "Bedrock Agent not configured"},
            )
            return ok(response_data.model_dump())
        
        # Initialize Bedrock Agent Runtime client
        bedrock_agent_runtime = boto3.client(
            "bedrock-agent-runtime",
            region_name=settings.aws_region or "us-east-1"
        )
        
        # Invoke agent
        try:
            response = bedrock_agent_runtime.invoke_agent(
                agentId=agent_id,
                agentAliasId=agent_alias_id,
                sessionId=request_data.session_id,
                inputText=request_data.message,
            )
            
            # Parse streaming response
            agent_response_text = ""
            event_stream = response.get("completion", [])
            
            for event in event_stream:
                if "chunk" in event:
                    chunk = event["chunk"]
                    if "bytes" in chunk:
                        agent_response_text += chunk["bytes"].decode("utf-8")
            
            if not agent_response_text:
                agent_response_text = "No response from agent"
            
            response_data = ChatResponse(
                response=agent_response_text,
                session_id=request_data.session_id,
            )
            
            logger.info(f"Agent chat completed for session: {request_data.session_id}")
            return ok(response_data.model_dump())
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"Bedrock Agent error: {error_code} - {error_msg}")
            return server_error(f"Agent invocation failed: {error_code}")
        
    except json.JSONDecodeError as e:
        logger.warning(f"Invalid JSON in request body: {e}")
        return bad_request("Invalid JSON in request body")
    except Exception as e:
        logger.error(f"Error in agent chat: {e}", exc_info=True)
        return server_error("Failed to process chat message")
