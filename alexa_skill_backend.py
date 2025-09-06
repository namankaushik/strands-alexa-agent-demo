"""
Alexa Skill Backend Server

A FastAPI server that provides webhook endpoints for Alexa skills.
Handles incoming requests from Alexa, authenticates them, and provides
starting points for LLM integration via OpenRouter and web search via Perplexity.
"""

import json
import hashlib
import hmac
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse
import uvicorn


app = FastAPI(
    title="Alexa Skill Backend",
    description="Webhook server for Alexa skills with LLM and web search integration",
    version="1.0.0"
)


# TODO: Configure these from environment variables
ALEXA_SKILL_ID = "your-alexa-skill-id"
ALEXA_CERTIFICATE_URL = None  # Will be populated from request headers


async def verify_alexa_request(
    request: Request,
    signature: Optional[str] = Header(None, alias="signature"),
    cert_url: Optional[str] = Header(None, alias="signaturecertchainurl")
) -> bool:
    """
    Verify that the request is coming from Amazon Alexa.
    
    This is a basic implementation - in production, you should:
    1. Download and validate the certificate from cert_url
    2. Verify the certificate chain
    3. Check the signature using the certificate's public key
    4. Validate the timestamp to prevent replay attacks
    
    For now, this is a placeholder that returns True.
    """
    # TODO: Implement proper Alexa request verification
    # https://developer.amazon.com/en-US/docs/alexa/custom-skills/host-a-custom-skill-as-a-web-service.html#verify-the-request
    return True


async def extract_user_intent_and_text(alexa_request: Dict[str, Any]) -> tuple[str, str]:
    """
    Extract the user's intent and spoken text from the Alexa request.
    
    Args:
        alexa_request: The full Alexa request JSON
        
    Returns:
        tuple: (intent_name, user_text)
    """
    request_type = alexa_request.get("request", {}).get("type")
    
    if request_type == "LaunchRequest":
        return "LaunchRequest", "launch skill"
    
    elif request_type == "IntentRequest":
        intent = alexa_request.get("request", {}).get("intent", {})
        intent_name = intent.get("name", "Unknown")
        
        # Extract slot values or use a default text representation
        slots = intent.get("slots", {})
        if "query" in slots and slots["query"].get("value"):
            user_text = slots["query"]["value"]
        else:
            # Fallback to intent name if no query slot
            user_text = f"Intent: {intent_name}"
            
        return intent_name, user_text
    
    elif request_type == "SessionEndedRequest":
        return "SessionEndedRequest", "end session"
    
    else:
        return "Unknown", "unknown request"


async def respond_to_user(intent: str, user_text: str, session_attributes: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a response to the user's request.
    
    This function will be the main integration point for:
    1. OpenRouter API for LLM responses
    2. Perplexity API for web search
    3. Any other AI/ML services
    
    Args:
        intent: The Alexa intent name
        user_text: The user's spoken text
        session_attributes: Session data from Alexa
        
    Returns:
        Dict containing the Alexa response structure
    """
    
    # TODO: Integrate OpenRouter API for LLM responses
    # Example integration:
    # 1. Send user_text to OpenRouter with appropriate prompt
    # 2. Get LLM response
    # 3. If LLM indicates need for web search, call Perplexity API
    # 4. Combine results into final response
    
    # TODO: Integrate Perplexity API for web search
    # Example usage:
    # 1. Detect when user is asking for current information
    # 2. Use Perplexity API to get real-time web results
    # 3. Incorporate results into LLM prompt for final answer
    
    # Placeholder response logic
    if intent == "LaunchRequest":
        response_text = "Welcome to the Strands Alexa Agent! How can I help you today?"
        should_end_session = False
    elif intent == "SessionEndedRequest":
        response_text = "Goodbye!"
        should_end_session = True
    else:
        # Basic echo response - replace with LLM integration
        response_text = f"I heard you say: {user_text}. I'm still learning how to respond to that!"
        should_end_session = False
    
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": response_text
            },
            "shouldEndSession": should_end_session
        }
    }


@app.post("/alexa")
async def alexa_webhook(request: Request):
    """
    Main Alexa webhook endpoint.
    
    Handles incoming requests from Alexa, verifies them, extracts the user's
    intent and text, generates a response, and returns it in Alexa's expected format.
    """
    try:
        # Get the raw request body
        body = await request.body()
        
        # Parse the JSON request
        try:
            alexa_request = json.loads(body)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in request body")
        
        # Verify the request is from Alexa
        is_valid = await verify_alexa_request(request)
        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid Alexa request")
        
        # Validate that this request is for our skill
        application_id = alexa_request.get("session", {}).get("application", {}).get("applicationId")
        if ALEXA_SKILL_ID and application_id != ALEXA_SKILL_ID:
            raise HTTPException(status_code=401, detail="Request not for this skill")
        
        # Extract user intent and text
        intent, user_text = await extract_user_intent_and_text(alexa_request)
        
        # Get session attributes
        session_attributes = alexa_request.get("session", {}).get("attributes", {})
        
        # Generate response using LLM/search integration
        response = await respond_to_user(intent, user_text, session_attributes)
        
        return JSONResponse(content=response)
        
    except HTTPException:
        raise
    except Exception as e:
        # Log the error in production
        print(f"Error processing Alexa request: {str(e)}")
        
        # Return a generic error response
        error_response = {
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "Sorry, I'm having trouble right now. Please try again later."
                },
                "shouldEndSession": True
            }
        }
        return JSONResponse(content=error_response, status_code=500)


@app.get("/health")
async def health_check():
    """
    Simple health check endpoint.
    """
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/")
async def root():
    """
    Root endpoint with basic information.
    """
    return {
        "service": "Alexa Skill Backend",
        "version": "1.0.0",
        "description": "FastAPI server for Alexa skill webhooks with LLM and web search integration",
        "endpoints": {
            "/alexa": "Main Alexa webhook endpoint (POST)",
            "/health": "Health check endpoint (GET)",
            "/": "This information endpoint (GET)"
        },
        "todo": [
            "Integrate OpenRouter API for LLM responses",
            "Integrate Perplexity API for web search",
            "Implement proper Alexa request verification",
            "Add environment configuration",
            "Add logging and monitoring"
        ]
    }


if __name__ == "__main__":
    # For development - in production, use a proper ASGI server
    uvicorn.run(
        "alexa_skill_backend:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
