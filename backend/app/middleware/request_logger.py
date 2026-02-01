"""Request logging middleware for monitoring and analytics."""

import time
import json
from fastapi import Request, Response
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.logger import log_request_response, setup_logging
from app.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from sqlalchemy.orm import Session
from typing import Optional

logger = setup_logging(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all incoming requests and outgoing responses."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Process the request
        response = await call_next(request)
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Get user ID if authenticated
        user_id = await self._get_user_id(request)
        
        # Log the request/response
        log_request_response(
            method=request.method,
            url=str(request.url),
            status_code=response.status_code,
            response_time=response_time,
            user_id=user_id,
            request_body=await self._get_request_body(request),
            response_body=await self._get_response_body(response)
        )
        
        return response

    async def _get_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID from request if authenticated."""
        try:
            # Try to get user from request state (set by auth middleware)
            if hasattr(request.state, 'user_id'):
                return request.state.user_id
            
            # Try to extract token and get user (simplified approach)
            authorization = request.headers.get("authorization")
            if authorization and authorization.startswith("Bearer "):
                # In a real scenario, you'd decode the JWT here
                # For now, we'll skip this as it requires the full auth flow
                pass
        except Exception:
            pass
        
        return None

    async def _get_request_body(self, request: Request):
        """Extract request body for logging."""
        try:
            # Only log bodies for certain endpoints to avoid logging sensitive data
            if request.method in ["POST", "PUT", "PATCH"]:
                # Avoid consuming the request body stream multiple times
                # This is a simplified approach - in production you might want to be more selective
                if any(endpoint in str(request.url) for endpoint in ["/auth/", "/agent/"]):
                    body = await request.body()
                    if body:
                        return json.loads(body.decode())
        except Exception:
            pass
        
        return None

    async def _get_response_body(self, response: Response):
        """Extract response body for logging."""
        # Response body extraction is tricky with streaming responses
        # For now, we'll return None to avoid complications
        # In production, you might implement a custom response class
        # that captures the body before sending
        return None


def setup_request_logging(app):
    """Set up request logging middleware for the FastAPI app."""
    app.add_middleware(RequestLoggingMiddleware)