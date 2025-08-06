#!/usr/bin/env python3
"""
Production credential encryption utility

This script helps encrypt API keys and credentials for secure production deployment.
"""

import os
import sys
import getpass
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.core.security import SecureKeyManager, APIKeyValidator
from src.core.exceptions import SecurityError, ConfigurationError

def main():
    print("🔐 InterviewAgent Production Credential Encryption")
    print("=" * 60)
    
    # Get master key
    master_key = os.getenv('INTERVIEW_AGENT_MASTER_KEY')
    if not master_key:
        print("❌ INTERVIEW_AGENT_MASTER_KEY environment variable not set")
        print("Generate one with: python -c \"import secrets, base64; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())\"")
        return 1
    
    try:
        key_manager = SecureKeyManager(master_key)
        validator = APIKeyValidator()
        
        print("✅ Security manager initialized successfully")
        print()
        
        # Available credentials to encrypt
        credentials = {
            'OPENAI_API_KEY': 'openai',
            'SUPABASE_KEY': 'supabase',
            'SUPABASE_SERVICE_ROLE_KEY': 'supabase',
            'GMAIL_APP_PASSWORD': None
        }
        
        print("Available credentials to encrypt:")
        for i, (key_name, key_type) in enumerate(credentials.items(), 1):
            print(f"{i}. {key_name}")
        print(f"{len(credentials) + 1}. Encrypt custom credential")
        print("0. Exit")
        print()
        
        while True:
            try:
                choice = input("Select credential to encrypt (0 to exit): ").strip()
                
                if choice == '0':
                    break
                
                if choice == str(len(credentials) + 1):
                    # Custom credential
                    key_name = input("Enter credential name: ").strip()
                    key_type = input("Enter credential type (or press Enter for none): ").strip() or None
                else:
                    # Predefined credential
                    try:
                        idx = int(choice) - 1
                        key_name, key_type = list(credentials.items())[idx]
                    except (ValueError, IndexError):
                        print("❌ Invalid choice. Please try again.")
                        continue
                
                # Get credential value
                credential = getpass.getpass(f"Enter {key_name}: ")
                
                if not credential:
                    print("❌ Empty credential. Skipping.")
                    continue
                
                # Validate credential if type is known
                if key_type and not validator.validate_api_key(credential, key_type):
                    masked = validator.mask_api_key(credential)
                    print(f"⚠️  Warning: Credential format validation failed for {key_name}: {masked}")
                    
                    if input("Continue anyway? (y/N): ").lower() != 'y':
                        continue
                
                # Encrypt credential
                encrypted = key_manager.encrypt_credential(credential)
                
                print(f"✅ Encrypted {key_name} successfully")
                print(f"Add to your .env.production file:")
                print(f"{key_name}_ENCRYPTED={encrypted}")
                print()
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                continue
        
        return 0
        
    except Exception as e:
        print(f"❌ Failed to initialize security manager: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())