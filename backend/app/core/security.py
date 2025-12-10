from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
import secrets
import hashlib

from app.core.config import settings
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_TOKEN_AVAILABILITY_MIN)
        
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode a JWT access token"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None

def generate_refresh_token() -> str:
    """Generate a secure random refresh token"""
    return secrets.token_hex(32)

def hash_refresh_token(token: str) -> str:
    """Hash a refresh token using SHA-256"""
    return hashlib.sha256(token.encode()).hexdigest()

def verify_refresh_token(plain_token: str, hashed_token: str) -> bool:
    """Verify a plain refresh token against a hashed refresh token"""
    return hash_refresh_token(plain_token) == hashed_token

def create_refresh_token_expiry() -> datetime:
    """Create an expiry datetime for a refresh token"""
    return datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_TOKEN_AVAILABILITY_MIN + settings.REFRESH_TOKEN_AVAILABILITY_MIN)

def is_token_expired(expires_at: datetime) -> bool:
    """Check if a token is expired"""
    return datetime.now(timezone.utc) > expires_at

def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """Validate password strength (at least 8 characters, including letters and numbers)"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if len(password) > 100:
        return False, "Password must not exceed 100 characters"
    
    if not any(char.isdigit() for char in password):
        return False, "Password must include at least one number"
    
    if not any(char.isalpha() for char in password):
        return False, "Password must include at least one letter"
    
    if not any(char in "!@#$%^&*()_+-=[]{}|;:,.<>?" for char in password):
        return False, "Password must contain at least one special character, e.g., !@#$%^&*()_+-=[]{}|;:,.<>?"
    
    return True, None
