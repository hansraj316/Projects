"""
Security utilities for InterviewAgent

Provides secure API key management, credential encryption, and security validation.
"""

import os
import base64
import secrets
import hashlib
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

from .exceptions import SecurityError, ConfigurationError

logger = logging.getLogger(__name__)

class SecureKeyManager:
    """
    Secure API key and credential management with encryption at rest
    """
    
    def __init__(self, master_password: Optional[str] = None):
        self._master_password = master_password or self._get_master_password()
        self._encryption_key = self._derive_encryption_key()
        self._cipher = Fernet(self._encryption_key)
    
    def _get_master_password(self) -> str:
        """Get master password from environment or generate one"""
        master_password = os.getenv('INTERVIEW_AGENT_MASTER_KEY')
        
        if not master_password:
            if os.getenv('ENVIRONMENT') == 'production':
                raise ConfigurationError(
                    "INTERVIEW_AGENT_MASTER_KEY environment variable is required in production"
                )
            
            # Generate a secure random master password for development
            master_password = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
            logger.warning("Generated temporary master password for development. Set INTERVIEW_AGENT_MASTER_KEY in production.")
        
        return master_password
    
    def _derive_encryption_key(self) -> bytes:
        """Derive encryption key from master password using PBKDF2"""
        # Use a fixed salt for key derivation (in production, store this securely)
        salt = os.getenv('INTERVIEW_AGENT_SALT', 'interview_agent_salt_2024').encode()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,  # Recommended minimum for 2024
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(self._master_password.encode()))
        return key
    
    def encrypt_credential(self, credential: str) -> str:
        """Encrypt a credential for secure storage"""
        try:
            encrypted_bytes = self._cipher.encrypt(credential.encode())
            return base64.urlsafe_b64encode(encrypted_bytes).decode()
        except Exception as e:
            raise SecurityError("Failed to encrypt credential") from e
    
    def decrypt_credential(self, encrypted_credential: str) -> str:
        """Decrypt a stored credential"""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_credential.encode())
            decrypted_bytes = self._cipher.decrypt(encrypted_bytes)
            return decrypted_bytes.decode()
        except Exception as e:
            raise SecurityError("Failed to decrypt credential") from e
    
    def hash_credential(self, credential: str) -> str:
        """Create a secure hash of a credential for comparison"""
        salt = secrets.token_bytes(32)
        pwdhash = hashlib.pbkdf2_hmac('sha256', credential.encode(), salt, 100000)
        return base64.urlsafe_b64encode(salt + pwdhash).decode()
    
    def verify_credential_hash(self, credential: str, stored_hash: str) -> bool:
        """Verify a credential against its stored hash"""
        try:
            decoded_hash = base64.urlsafe_b64decode(stored_hash.encode())
            salt = decoded_hash[:32]
            stored_pwdhash = decoded_hash[32:]
            
            pwdhash = hashlib.pbkdf2_hmac('sha256', credential.encode(), salt, 100000)
            return secrets.compare_digest(stored_pwdhash, pwdhash)
        except Exception:
            return False

class APIKeyValidator:
    """
    Validates and manages API keys with security checks
    """
    
    # API key patterns for validation
    API_KEY_PATTERNS = {
        'openai': r'^sk-[a-zA-Z0-9\-_]{20,}$|^sk-proj-[a-zA-Z0-9\-_]{20,}$',
        'supabase': r'^eyJ[a-zA-Z0-9\-_\.]{100,}$',  # JWT tokens start with eyJ
        'anthropic': r'^sk-ant-[a-zA-Z0-9\-_]{95,}$'
    }
    
    MIN_KEY_LENGTH = 20
    MAX_KEY_LENGTH = 500
    
    @classmethod
    def validate_api_key(cls, key: str, key_type: Optional[str] = None) -> bool:
        """
        Validate API key format and basic security requirements
        """
        if not key or not isinstance(key, str):
            return False
        
        # Basic length validation
        if len(key) < cls.MIN_KEY_LENGTH or len(key) > cls.MAX_KEY_LENGTH:
            return False
        
        # Check for common security issues
        if cls._has_security_issues(key):
            return False
        
        # Type-specific validation if provided
        if key_type and key_type in cls.API_KEY_PATTERNS:
            import re
            pattern = cls.API_KEY_PATTERNS[key_type]
            return bool(re.match(pattern, key))
        
        return True
    
    @classmethod
    def _has_security_issues(cls, key: str) -> bool:
        """Check for common security issues in API keys"""
        # Check for obviously fake or test keys
        suspicious_patterns = [
            'test', 'fake', 'dummy', 'example', 'placeholder',
            '123456', 'abcdef', 'xxxxxx', '000000'
        ]
        
        key_lower = key.lower()
        return any(pattern in key_lower for pattern in suspicious_patterns)
    
    @classmethod
    def mask_api_key(cls, key: str, visible_chars: int = 4) -> str:
        """
        Mask API key for logging (show only first and last few characters)
        """
        if not key or len(key) <= visible_chars * 2:
            return "*" * min(len(key) if key else 0, 20)
        
        return f"{key[:visible_chars]}{'*' * (len(key) - visible_chars * 2)}{key[-visible_chars:]}"

class SecureEnvironmentLoader:
    """
    Secure environment variable loading with validation
    """
    
    def __init__(self, key_manager: SecureKeyManager):
        self._key_manager = key_manager
        self._validator = APIKeyValidator()
    
    def get_api_key(self, key_name: str, key_type: Optional[str] = None, required: bool = True) -> Optional[str]:
        """
        Securely get and validate API key from environment
        """
        encrypted_key = os.getenv(f"{key_name}_ENCRYPTED")
        
        if encrypted_key:
            try:
                key = self._key_manager.decrypt_credential(encrypted_key)
            except SecurityError as e:
                logger.error(f"Failed to decrypt {key_name}: {e}")
                if required:
                    raise ConfigurationError(f"Failed to decrypt required API key: {key_name}")
                return None
        else:
            key = os.getenv(key_name)
        
        if not key:
            if required:
                raise ConfigurationError(f"Required API key not found: {key_name}")
            return None
        
        # Validate the key
        if not self._validator.validate_api_key(key, key_type):
            masked_key = self._validator.mask_api_key(key)
            logger.warning(f"Invalid API key format for {key_name}: {masked_key}")
            if required:
                raise SecurityError(f"Invalid API key format: {key_name}")
        
        return key
    
    def set_encrypted_credential(self, key_name: str, credential: str) -> str:
        """
        Encrypt and return credential for storage
        """
        return self._key_manager.encrypt_credential(credential)

class SecurityConfig:
    """
    Security configuration and validation
    """
    
    def __init__(self):
        self.key_manager = SecureKeyManager()
        self.env_loader = SecureEnvironmentLoader(self.key_manager)
    
    def validate_security_requirements(self) -> Dict[str, Any]:
        """
        Validate all security requirements
        """
        validation_results = {
            "master_key_set": bool(os.getenv('INTERVIEW_AGENT_MASTER_KEY')),
            "environment": os.getenv('ENVIRONMENT', 'development'),
            "api_keys": {},
            "security_warnings": []
        }
        
        # Check required API keys
        required_keys = {
            'OPENAI_API_KEY': 'openai',
            'SUPABASE_KEY': 'supabase'
        }
        
        for key_name, key_type in required_keys.items():
            try:
                key = self.env_loader.get_api_key(key_name, key_type, required=False)
                validation_results["api_keys"][key_name] = {
                    "present": bool(key),
                    "valid": bool(key and self.env_loader._validator.validate_api_key(key, key_type)),
                    "encrypted": bool(os.getenv(f"{key_name}_ENCRYPTED"))
                }
            except Exception as e:
                validation_results["api_keys"][key_name] = {
                    "present": False,
                    "valid": False,
                    "encrypted": False,
                    "error": str(e)
                }
        
        # Security warnings
        if not validation_results["master_key_set"] and validation_results["environment"] == "production":
            validation_results["security_warnings"].append("Master key not set in production environment")
        
        if not any(result["encrypted"] for result in validation_results["api_keys"].values()):
            validation_results["security_warnings"].append("No API keys are encrypted")
        
        return validation_results
    
    def get_secure_config(self) -> Dict[str, str]:
        """
        Get securely loaded configuration
        """
        config = {}
        
        # Load API keys securely
        try:
            config['openai_api_key'] = self.env_loader.get_api_key('OPENAI_API_KEY', 'openai')
        except (SecurityError, ConfigurationError) as e:
            logger.error(f"Failed to load OpenAI API key: {e}")
            config['openai_api_key'] = None
        
        try:
            config['supabase_key'] = self.env_loader.get_api_key('SUPABASE_KEY', 'supabase')
        except (SecurityError, ConfigurationError) as e:
            logger.error(f"Failed to load Supabase key: {e}")
            config['supabase_key'] = None
        
        return config

# Global security instance
_security_config: Optional[SecurityConfig] = None

def get_security_config() -> SecurityConfig:
    """Get global security configuration instance"""
    global _security_config
    if _security_config is None:
        _security_config = SecurityConfig()
    return _security_config