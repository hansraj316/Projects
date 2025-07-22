"""
Secure credential management system for InterviewAgent
"""

import os
import json
import base64
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path

try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives.hashes import SHA256
    from cryptography.hazmat.backends import default_backend
    import secrets
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_config

logger = logging.getLogger(__name__)

class CredentialManager:
    """Secure credential management for job site logins and API keys"""
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize credential manager
        
        Args:
            storage_path: Custom path for credential storage
        """
        self.config = get_config()
        
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            self.storage_path = self.config.DATA_DIR / "credentials"
        
        # Create storage directory
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize encryption
        self._init_encryption()
        
        logger.info(f"Credential manager initialized with storage: {self.storage_path}")
    
    def _init_encryption(self):
        """Initialize encryption system"""
        if not CRYPTO_AVAILABLE:
            logger.warning("Cryptography library not available. Credentials will be stored in plaintext!")
            self.encryption_enabled = False
            return
        
        # Get or create master key
        master_key = self._get_master_key()
        if not master_key:
            logger.error("Failed to get master key. Encryption disabled.")
            self.encryption_enabled = False
            return
        
        # Derive encryption key
        kdf = PBKDF2HMAC(
            algorithm=SHA256(),
            length=32,
            salt=b'interviewagent_salt',  # In production, use random salt
            iterations=100000,
            backend=default_backend()
        )
        
        self.encryption_key = kdf.derive(master_key.encode())
        self.encryption_enabled = True
        logger.info("Encryption initialized successfully")
    
    def _get_master_key(self) -> Optional[str]:
        """Get master encryption key from environment or config"""
        # Try environment variable first
        master_key = os.getenv('INTERVIEWAGENT_MASTER_KEY')
        if master_key:
            return master_key
        
        # Try config
        if hasattr(self.config, 'ENCRYPTION_KEY') and self.config.ENCRYPTION_KEY:
            return self.config.ENCRYPTION_KEY
        
        # Generate and save a new key (for development only)
        if self.config.DEBUG:
            logger.warning("Generating new master key for development. This is not secure for production!")
            new_key = secrets.token_urlsafe(32)
            
            # Try to save to .env file
            env_path = Path('.env')
            if env_path.exists():
                try:
                    with open(env_path, 'a') as f:
                        f.write(f"\nINTERVIEWAGENT_MASTER_KEY={new_key}\n")
                    logger.info("Master key saved to .env file")
                except Exception as e:
                    logger.warning(f"Could not save master key to .env: {e}")
            
            return new_key
        
        logger.error("No master key found. Set INTERVIEWAGENT_MASTER_KEY environment variable.")
        return None
    
    def _encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        if not self.encryption_enabled:
            return data
        
        try:
            # Generate random IV
            iv = secrets.token_bytes(16)
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(self.encryption_key),
                modes.CBC(iv),
                backend=default_backend()
            )
            
            encryptor = cipher.encryptor()
            
            # Pad data to block size
            padded_data = self._pad_data(data.encode('utf-8'))
            
            # Encrypt
            encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
            
            # Combine IV and encrypted data
            combined = iv + encrypted_data
            
            # Return base64 encoded
            return base64.b64encode(combined).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return data  # Return plaintext as fallback
    
    def _decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        if not self.encryption_enabled:
            return encrypted_data
        
        try:
            # Decode from base64
            combined = base64.b64decode(encrypted_data.encode('utf-8'))
            
            # Extract IV and encrypted data
            iv = combined[:16]
            encrypted = combined[16:]
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(self.encryption_key),
                modes.CBC(iv),
                backend=default_backend()
            )
            
            decryptor = cipher.decryptor()
            
            # Decrypt
            padded_data = decryptor.update(encrypted) + decryptor.finalize()
            
            # Remove padding
            data = self._unpad_data(padded_data)
            
            return data.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return encrypted_data  # Return as-is if decryption fails
    
    def _pad_data(self, data: bytes) -> bytes:
        """Add PKCS7 padding"""
        block_size = 16
        padding_length = block_size - (len(data) % block_size)
        padding = bytes([padding_length] * padding_length)
        return data + padding
    
    def _unpad_data(self, padded_data: bytes) -> bytes:
        """Remove PKCS7 padding"""
        padding_length = padded_data[-1]
        return padded_data[:-padding_length]
    
    def store_credential(self, 
                        service: str, 
                        username: str, 
                        password: str, 
                        additional_data: Optional[Dict[str, Any]] = None,
                        user_id: str = "default") -> Dict[str, Any]:
        """
        Store encrypted credentials for a service
        
        Args:
            service: Service name (e.g., 'linkedin', 'indeed')
            username: Username or email
            password: Password or API key
            additional_data: Additional service-specific data
            user_id: User identifier
            
        Returns:
            Dict with storage result
        """
        try:
            # Prepare credential data
            credential_data = {
                "service": service,
                "username": username,
                "password": self._encrypt_data(password),
                "additional_data": additional_data or {},
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "user_id": user_id
            }
            
            # Get user credential file
            cred_file = self._get_user_credential_file(user_id)
            
            # Load existing credentials
            existing_creds = self._load_credentials(cred_file)
            
            # Update or add credential
            existing_creds[service] = credential_data
            
            # Save credentials
            success = self._save_credentials(cred_file, existing_creds)
            
            if success:
                logger.info(f"Credential stored for service: {service}")
                return {
                    "success": True,
                    "message": f"Credential stored for {service}",
                    "service": service
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to save credentials"
                }
                
        except Exception as e:
            logger.error(f"Error storing credential: {e}")
            return {
                "success": False,
                "error": f"Failed to store credential: {str(e)}"
            }
    
    def get_credential(self, service: str, user_id: str = "default") -> Optional[Dict[str, Any]]:
        """
        Retrieve and decrypt credentials for a service
        
        Args:
            service: Service name
            user_id: User identifier
            
        Returns:
            Decrypted credential data or None
        """
        try:
            cred_file = self._get_user_credential_file(user_id)
            credentials = self._load_credentials(cred_file)
            
            if service not in credentials:
                return None
            
            cred_data = credentials[service].copy()
            
            # Decrypt password
            cred_data["password"] = self._decrypt_data(cred_data["password"])
            
            return cred_data
            
        except Exception as e:
            logger.error(f"Error retrieving credential: {e}")
            return None
    
    def list_credentials(self, user_id: str = "default") -> List[Dict[str, Any]]:
        """
        List all stored credentials (without sensitive data)
        
        Args:
            user_id: User identifier
            
        Returns:
            List of credential summaries
        """
        try:
            cred_file = self._get_user_credential_file(user_id)
            credentials = self._load_credentials(cred_file)
            
            summaries = []
            for service, cred_data in credentials.items():
                summaries.append({
                    "service": service,
                    "username": cred_data.get("username"),
                    "created_at": cred_data.get("created_at"),
                    "updated_at": cred_data.get("updated_at"),
                    "has_password": bool(cred_data.get("password")),
                    "additional_data_keys": list(cred_data.get("additional_data", {}).keys())
                })
            
            return sorted(summaries, key=lambda x: x["updated_at"], reverse=True)
            
        except Exception as e:
            logger.error(f"Error listing credentials: {e}")
            return []
    
    def update_credential(self, 
                         service: str,
                         username: Optional[str] = None,
                         password: Optional[str] = None,
                         additional_data: Optional[Dict[str, Any]] = None,
                         user_id: str = "default") -> Dict[str, Any]:
        """
        Update existing credential
        
        Args:
            service: Service name
            username: New username (optional)
            password: New password (optional)  
            additional_data: New additional data (optional)
            user_id: User identifier
            
        Returns:
            Dict with update result
        """
        try:
            cred_file = self._get_user_credential_file(user_id)
            credentials = self._load_credentials(cred_file)
            
            if service not in credentials:
                return {
                    "success": False,
                    "error": f"Credential for {service} not found"
                }
            
            # Update fields if provided
            if username is not None:
                credentials[service]["username"] = username
            
            if password is not None:
                credentials[service]["password"] = self._encrypt_data(password)
            
            if additional_data is not None:
                credentials[service]["additional_data"] = additional_data
            
            credentials[service]["updated_at"] = datetime.now().isoformat()
            
            # Save updated credentials
            success = self._save_credentials(cred_file, credentials)
            
            if success:
                logger.info(f"Credential updated for service: {service}")
                return {
                    "success": True,
                    "message": f"Credential updated for {service}",
                    "service": service
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to save updated credentials"
                }
                
        except Exception as e:
            logger.error(f"Error updating credential: {e}")
            return {
                "success": False,
                "error": f"Failed to update credential: {str(e)}"
            }
    
    def delete_credential(self, service: str, user_id: str = "default") -> Dict[str, Any]:
        """
        Delete credential for a service
        
        Args:
            service: Service name
            user_id: User identifier
            
        Returns:
            Dict with deletion result
        """
        try:
            cred_file = self._get_user_credential_file(user_id)
            credentials = self._load_credentials(cred_file)
            
            if service not in credentials:
                return {
                    "success": False,
                    "error": f"Credential for {service} not found"
                }
            
            # Remove credential
            del credentials[service]
            
            # Save updated credentials
            success = self._save_credentials(cred_file, credentials)
            
            if success:
                logger.info(f"Credential deleted for service: {service}")
                return {
                    "success": True,
                    "message": f"Credential deleted for {service}",
                    "service": service
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to save updated credentials"
                }
                
        except Exception as e:
            logger.error(f"Error deleting credential: {e}")
            return {
                "success": False,
                "error": f"Failed to delete credential: {str(e)}"
            }
    
    def test_credential(self, service: str, user_id: str = "default") -> Dict[str, Any]:
        """
        Test if credential is valid (basic validation)
        
        Args:
            service: Service name
            user_id: User identifier
            
        Returns:
            Dict with test result
        """
        try:
            credential = self.get_credential(service, user_id)
            
            if not credential:
                return {
                    "success": False,
                    "error": f"No credential found for {service}"
                }
            
            # Basic validation
            if not credential.get("username") or not credential.get("password"):
                return {
                    "success": False,
                    "error": "Credential is missing username or password"
                }
            
            # Check if credential is too old (optional warning)
            created_at = credential.get("created_at")
            if created_at:
                created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00').replace('+00:00', ''))
                age_days = (datetime.now() - created_date).days
                
                warning = None
                if age_days > 90:
                    warning = f"Credential is {age_days} days old. Consider updating."
                
                return {
                    "success": True,
                    "message": f"Credential for {service} is valid",
                    "age_days": age_days,
                    "warning": warning
                }
            
            return {
                "success": True,
                "message": f"Credential for {service} is valid"
            }
            
        except Exception as e:
            logger.error(f"Error testing credential: {e}")
            return {
                "success": False,
                "error": f"Failed to test credential: {str(e)}"
            }
    
    def _get_user_credential_file(self, user_id: str) -> Path:
        """Get credential file path for user"""
        filename = f"credentials_{user_id}.json"
        return self.storage_path / filename
    
    def _load_credentials(self, cred_file: Path) -> Dict[str, Any]:
        """Load credentials from file"""
        try:
            if not cred_file.exists():
                return {}
            
            with open(cred_file, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"Error loading credentials: {e}")
            return {}
    
    def _save_credentials(self, cred_file: Path, credentials: Dict[str, Any]) -> bool:
        """Save credentials to file"""
        try:
            # Create backup if file exists
            if cred_file.exists():
                backup_file = cred_file.with_suffix('.bak')
                cred_file.rename(backup_file)
            
            # Save new credentials
            with open(cred_file, 'w') as f:
                json.dump(credentials, f, indent=2)
            
            # Set restrictive permissions (Unix only)
            if hasattr(os, 'chmod'):
                os.chmod(cred_file, 0o600)
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving credentials: {e}")
            return False
    
    def export_credentials(self, user_id: str = "default", include_passwords: bool = False) -> Dict[str, Any]:
        """
        Export credentials for backup (passwords optionally excluded)
        
        Args:
            user_id: User identifier
            include_passwords: Whether to include encrypted passwords
            
        Returns:
            Exportable credential data
        """
        try:
            credentials = self.list_credentials(user_id)
            
            export_data = {
                "export_date": datetime.now().isoformat(),
                "user_id": user_id,
                "encryption_enabled": self.encryption_enabled,
                "credentials": []
            }
            
            if include_passwords:
                # Include full credential data
                cred_file = self._get_user_credential_file(user_id)
                full_credentials = self._load_credentials(cred_file)
                export_data["credentials"] = full_credentials
            else:
                # Include only metadata
                export_data["credentials"] = credentials
            
            return {
                "success": True,
                "data": export_data
            }
            
        except Exception as e:
            logger.error(f"Error exporting credentials: {e}")
            return {
                "success": False,
                "error": f"Failed to export credentials: {str(e)}"
            }