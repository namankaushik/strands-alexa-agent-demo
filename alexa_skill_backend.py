import os
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Environment variables that must be set:
# OPENROUTER_API_KEY: Your OpenRouter API key
# PERPLEXITY_API_KEY: Your Perplexity API key
# OPENROUTER_MODEL_ID: Model ID to use (e.g., "anthropic/claude-3-haiku", "openai/gpt-4")

@app.post("/alexa")
async def alexa_webhook(request: Request):
    """Handle Alexa webhook requests."""
    try:
        # Receive Alexa JSON POST
        event = await request.json()
        user_input = event.get("request", {}).get("intent", {}).get("slots", {}).get("query", {}).get("value", "")
        
        if not user_input:
            return JSONResponse({"response": "I didn't understand your request. Please try again."})
        
        # Generate response using LLM or web search
        reply = await respond_to_user(user_input)
        
        return JSONResponse({"response": reply})
        
    except Exception as e:
        logger.error(f"Error processing Alexa request: {str(e)}")
        return JSONResponse({"response": "I'm sorry, I encountered an error processing your request."})

async def respond_to_user(prompt: str) -> str:
    """Decide whether to use LLM or web search based on the prompt."""
    try:
        # Check if prompt requires web search based on key phrases
        web_search_phrases = [
            'search', 'find on web', 'look up', 'web search', 'google',
            'latest', 'current', 'news', 'today', 'recent', 'happening now',
            'real time', 'live', 'breaking', 'update on', 'what\'s new'
        ]
        
        requires_web = any(phrase in prompt.lower() for phrase in web_search_phrases)
        
        if requires_web:
            # Use Perplexity API for web search
            return await call_perplexity_search(prompt)
        else:
            # Use OpenRouter API for direct LLM response
            return await call_openrouter_llm(prompt)
            
    except Exception as e:
        logger.error(f"Error in respond_to_user: {str(e)}")
        return "I'm sorry, I encountered an error generating a response."

async def call_openrouter_llm(prompt: str) -> str:
    """Make API call to OpenRouter for LLM completion using httpx."""
    try:
        # Get environment variables
        api_key = os.getenv('OPENROUTER_API_KEY')
        model_id = os.getenv('OPENROUTER_MODEL_ID', 'anthropic/claude-3-haiku')
        
        if not api_key:
            logger.error("OPENROUTER_API_KEY environment variable is not set")
            return "Configuration error: OpenRouter API key not found."
        
        # Prepare the API request
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/namankaushik/strands-alexa-agent-demo",
            "X-Title": "Strands Alexa Agent Demo"
        }
        
        data = {
            "model": model_id,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant integrated with Alexa. Provide concise, clear responses suitable for voice interaction. Keep responses under 200 words."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 300,
            "temperature": 0.7
        }
        
        # Make the API request using httpx
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()
        
        # Extract the response
        result = response.json()
        
        if 'choices' in result and len(result['choices']) > 0:
            return result['choices'][0]['message']['content'].strip()
        else:
            logger.error(f"Unexpected OpenRouter API response format: {result}")
            return "I received an unexpected response from the AI service."
            
    except httpx.HTTPError as e:
        logger.error(f"OpenRouter API request error: {str(e)}")
        return "I'm sorry, I'm having trouble connecting to the AI service right now."
    except Exception as e:
        logger.error(f"Error calling OpenRouter LLM: {str(e)}")
        return "I encountered an error while processing your request."

async def call_perplexity_search(query: str) -> str:
    """Make API call to Perplexity for web search using httpx."""
    try:
        # Get environment variable
        api_key = os.getenv('PERPLEXITY_API_KEY')
        
        if not api_key:
            logger.error("PERPLEXITY_API_KEY environment variable is not set")
            return "Configuration error: Perplexity API key not found."
        
        # Prepare the API request
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "llama-3.1-sonar-small-128k-online",  # Perplexity's web-search enabled model
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that can search the web for current information. Provide concise, accurate responses suitable for voice interaction. Keep responses under 200 words and cite sources when possible."
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            "max_tokens": 300,
            "temperature": 0.3,
            "return_citations": True,
            "search_domain_filter": ["perplexity.ai"],
            "return_images": False
        }
        
        # Make the API request using httpx
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()
        
        # Extract the response
        result = response.json()
        
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content'].strip()
            
            # Add citation information if available
            if 'citations' in result and result['citations']:
                content += " (Sources: " + ", ".join([f"{i+1}" for i in range(len(result['citations']))]) + ")"
            
            return content
        else:
            logger.error(f"Unexpected Perplexity API response format: {result}")
            return "I received an unexpected response from the web search service."
            
    except httpx.HTTPError as e:
        logger.error(f"Perplexity API request error: {str(e)}")
        return "I'm sorry, I'm having trouble connecting to the web search service right now."
    except Exception as e:
        logger.error(f"Error calling Perplexity search: {str(e)}")
        return "I encountered an error while searching the web."

# TODO: Add authentication for Alexa skill endpoint as required by Amazon.
# This should include request signature verification and timestamp validation.
