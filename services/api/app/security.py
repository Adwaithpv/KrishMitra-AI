"""
Security and rate limiting for the API
"""

import time
import hashlib
from typing import Dict, Optional
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security.api_key import APIKeyHeader
import logging

try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
except ImportError:
    Limiter = None
    _rate_limit_exceeded_handler = None
    get_remote_address = None
    RateLimitExceeded = None

logger = logging.getLogger(__name__)

# Rate limiting configuration
RATE_LIMITS = {
    "query": "10/minute",      # 10 queries per minute per IP
    "ingest": "5/hour",        # 5 ingestion requests per hour per IP
    "metrics": "30/minute",    # 30 metrics requests per minute per IP
    "cache": "20/minute"       # 20 cache operations per minute per IP
}

# Initialize rate limiter
if Limiter:
    limiter = Limiter(key_func=get_remote_address)
else:
    limiter = None

class SecurityManager:
    """Handles API security including authentication and authorization"""
    
    def __init__(self):
        self.api_keys = self._load_api_keys()
        self.blocked_ips = set()
        self.failed_attempts = {}  # IP -> (count, last_attempt_time)
        
    def _load_api_keys(self) -> Dict[str, Dict[str, str]]:
        """Load API keys from environment or config"""
        # In production, load from secure storage
        # For now, using environment variables
        import os
        
        api_keys = {}
        
        # Admin key for internal services
        admin_key = os.getenv("ADMIN_API_KEY")
        if admin_key:
            api_keys[admin_key] = {
                "name": "admin",
                "permissions": ["read", "write", "admin"],
                "rate_limit_multiplier": 10
            }
        
        # Public key for mobile clients (with restrictions)
        public_key = os.getenv("PUBLIC_API_KEY")
        if public_key:
            api_keys[public_key] = {
                "name": "public",
                "permissions": ["read"],
                "rate_limit_multiplier": 1
            }
        
        return api_keys
    
    def authenticate_api_key(self, api_key: str) -> Optional[Dict[str, str]]:
        """Authenticate API key and return user info"""
        return self.api_keys.get(api_key)
    
    def check_permissions(self, user_info: Dict[str, str], required_permission: str) -> bool:
        """Check if user has required permission"""
        if not user_info:
            return False
        
        user_permissions = user_info.get("permissions", [])
        return required_permission in user_permissions or "admin" in user_permissions
    
    def is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is blocked"""
        return ip in self.blocked_ips
    
    def record_failed_attempt(self, ip: str):
        """Record failed authentication attempt"""
        current_time = time.time()
        
        if ip in self.failed_attempts:
            count, _ = self.failed_attempts[ip]
            self.failed_attempts[ip] = (count + 1, current_time)
        else:
            self.failed_attempts[ip] = (1, current_time)
        
        # Block IP after 5 failed attempts in 15 minutes
        count, first_attempt = self.failed_attempts[ip]
        if count >= 5 and (current_time - first_attempt) < 900:  # 15 minutes
            self.blocked_ips.add(ip)
            logger.warning(f"Blocked IP {ip} after {count} failed attempts")
    
    def clean_failed_attempts(self):
        """Clean old failed attempts (older than 15 minutes)"""
        current_time = time.time()
        expired_ips = []
        
        for ip, (count, last_attempt) in self.failed_attempts.items():
            if (current_time - last_attempt) > 900:  # 15 minutes
                expired_ips.append(ip)
        
        for ip in expired_ips:
            del self.failed_attempts[ip]
            if ip in self.blocked_ips:
                self.blocked_ips.remove(ip)

# Security middleware functions
def get_client_ip(request: Request) -> str:
    """Get client IP address from request"""
    # Check for forwarded headers (when behind proxy)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return request.client.host if request.client else "unknown"

def security_headers_middleware(request: Request, call_next):
    """Add security headers to response"""
    response = call_next(request)
    
    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    return response

# API Key authentication
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_api_key_optional(api_key: str = None) -> Optional[str]:
    """Get API key from header (optional)"""
    return api_key

def get_api_key_required(api_key: str = None) -> str:
    """Get API key from header (required)"""
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API key required"
        )
    return api_key

# Rate limiting decorators
def apply_rate_limit(rate: str):
    """Apply rate limit to endpoint"""
    def decorator(func):
        if limiter:
            return limiter.limit(rate)(func)
        return func
    return decorator

# Global security manager
security_manager = SecurityManager()

# Rate limit exceeded handler
if limiter and _rate_limit_exceeded_handler:
    def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        response = _rate_limit_exceeded_handler(request, exc)
        logger.warning(f"Rate limit exceeded for {get_client_ip(request)}")
        return response
else:
    rate_limit_handler = None
