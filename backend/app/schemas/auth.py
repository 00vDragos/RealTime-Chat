from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional

class UserRegister(BaseModel):
    """Schema for user registration (email + password)"""
    email: EmailStr = Field(max_length=255, description="User email address")
    password: str = Field(min_length=8, max_length=128, description="User password")
    display_name: Optional[str] = Field(None, max_length=100, description="Display name for the user")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isalpha() for char in v):
            raise ValueError('Password must contain at least one letter')
        if not any(char in "!@#$%^&*()_+-=[]{}|;:,.<>?" for char in v):
            raise ValueError('Password must contain at least one special character')
        return v
    
class UserLogin(BaseModel):
    """Schema for user login (email + password)"""
    email: EmailStr = Field(max_length=255, description="User email address")
    password: str = Field(min_length=8, max_length=128, description="User password")

class GoogleAuthRequest(BaseModel):
    """Schema for Google OAuth authentication"""
    code : str = Field(description="Authorization code received from Google")
    
class GoogleAuthResponse(BaseModel):
    """Response with Google OAuth URL and state"""
    url: str = Field(description="Google OAuth authorization URL")
    state: str = Field(description="State parameter for OAuth flow")
    
class RefreshTokenRequest(BaseModel):
    """Schema for refreshing authentication tokens"""
    refresh_token: str = Field(description="Refresh token to obtain new access token")
    
class LogoutRequest(BaseModel):
    """Schema for logging out a user"""
    refresh_token: str = Field(description="Refresh token to invalidate on logout")
    
class UserResponse(BaseModel):
    """Schema for user data in responses"""
    id: str = Field(description="User ID")
    email: EmailStr = Field(description="User email")
    display_name: Optional[str] = Field(None, description="Display name for the user")
    avatar_url: Optional[str] = Field(None, description="URL of the user's avatar")
    provider: Optional[str] = Field(None, description="Auth provider (local, google)")
    provider_id: Optional[str] = Field(None, description="Provider-specific user ID (for OAuth)")
    created_at: Optional[str] = Field(None, description="Timestamp when the user was created")
    updated_at: Optional[str] = Field(None, description="Timestamp when the user was last updated")
    last_seen: Optional[str] = Field(None, description="Timestamp when the user was last online")

class TokenResponse(BaseModel):
    """Schema for authentication response with tokens"""
    access_token: str = Field(description="JWT access token")
    refresh_token: str = Field(description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    user: UserResponse = Field(description="Authenticated user information")

class AccessTokenResponse(BaseModel):
    """Schema for refresh token response"""
    access_token: str = Field(description="New JWT access token")
    token_type: str = Field(default="bearer", description="Token type")

class MessageResponse(BaseModel):
    """Generic message response"""
    message: str = Field(description="Response message")
    
    