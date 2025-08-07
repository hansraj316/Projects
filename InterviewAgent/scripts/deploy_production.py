#!/usr/bin/env python3
"""
Production deployment validation and setup script

This script validates the production environment and ensures all security requirements are met.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Tuple

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.core.security import get_security_config
from src.core.exceptions import SecurityError, ConfigurationError
from src.config import AppConfig

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class ProductionValidator:
    """Production deployment validator"""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def validate_environment(self) -> bool:
        """Validate production environment requirements"""
        logger.info("🔍 Validating production environment...")
        
        # Check environment marker
        env = os.getenv('ENVIRONMENT')
        if env != 'production':
            self.errors.append(f"ENVIRONMENT must be 'production', got: {env}")
        
        # Validate security configuration
        try:
            security_config = get_security_config()
            validation_results = security_config.validate_security_requirements()
            
            # Check master key
            if not validation_results['master_key_set']:
                self.errors.append("INTERVIEW_AGENT_MASTER_KEY is required in production")
            
            # Check API keys
            for key_name, key_info in validation_results['api_keys'].items():
                if not key_info['present']:
                    self.errors.append(f"Required API key missing: {key_name}")
                elif not key_info['valid']:
                    self.errors.append(f"Invalid API key format: {key_name}")
                
                if not key_info['encrypted']:
                    self.warnings.append(f"API key {key_name} is not encrypted (consider using {key_name}_ENCRYPTED)")
            
            # Add security warnings
            self.warnings.extend(validation_results['security_warnings'])
            
        except Exception as e:
            self.errors.append(f"Security validation failed: {e}")
        
        return len(self.errors) == 0
    
    def validate_application_config(self) -> bool:
        """Validate application configuration"""
        logger.info("🔧 Validating application configuration...")
        
        try:
            config = AppConfig.from_env()
            config.validate()
            
            # Production-specific validations
            if config.debug:
                self.warnings.append("DEBUG is enabled in production")
            
            if config.openai.temperature > 1.0:
                self.warnings.append(f"High OpenAI temperature ({config.openai.temperature}) may affect consistency")
            
            # Check required directories
            paths = config.get_paths()
            for path_name, path in paths.items():
                if not path.exists() and path_name != 'project_root':
                    logger.info(f"Creating missing directory: {path}")
                    path.mkdir(parents=True, exist_ok=True)
            
            return True
            
        except Exception as e:
            self.errors.append(f"Application config validation failed: {e}")
            return False
    
    def check_mock_dependencies(self) -> bool:
        """Check for mock dependencies that shouldn't be in production"""
        logger.info("🧪 Checking for development-only code...")
        
        project_root = Path(__file__).parent.parent
        mock_patterns = [
            "MOCK_MODE",
            "mock_data",
            "development_only",
            "# TODO: Remove in production"
        ]
        
        python_files = list(project_root.rglob("*.py"))
        issues_found = []
        
        for file_path in python_files:
            if 'test' in str(file_path) or '__pycache__' in str(file_path):
                continue
                
            try:
                content = file_path.read_text()
                for pattern in mock_patterns:
                    if pattern.lower() in content.lower():
                        issues_found.append(f"{file_path.relative_to(project_root)}: {pattern}")
            except Exception:
                continue
        
        if issues_found:
            self.warnings.extend([f"Mock/development code found: {issue}" for issue in issues_found])
        
        return True
    
    def validate_dependencies(self) -> bool:
        """Validate production dependencies"""
        logger.info("📦 Validating dependencies...")
        
        try:
            # Check critical imports
            import openai
            import supabase
            import streamlit
            import cryptography
            
            logger.info("✅ Critical dependencies available")
            return True
            
        except ImportError as e:
            self.errors.append(f"Missing critical dependency: {e}")
            return False
    
    def generate_report(self) -> Tuple[bool, str]:
        """Generate validation report"""
        success = len(self.errors) == 0
        
        report = ["=" * 60]
        report.append("🚀 PRODUCTION DEPLOYMENT VALIDATION REPORT")
        report.append("=" * 60)
        
        if success:
            report.append("✅ VALIDATION PASSED - Ready for production deployment!")
        else:
            report.append("❌ VALIDATION FAILED - Fix errors before deployment")
        
        if self.errors:
            report.append("\n🚨 ERRORS (MUST FIX):")
            for error in self.errors:
                report.append(f"   ❌ {error}")
        
        if self.warnings:
            report.append("\n⚠️  WARNINGS (CONSIDER FIXING):")
            for warning in self.warnings:
                report.append(f"   ⚠️  {warning}")
        
        if success:
            report.append("\n🔧 DEPLOYMENT INSTRUCTIONS:")
            report.append("   1. Ensure all environment variables are set")
            report.append("   2. Run: streamlit run streamlit_app.py --server.port 8501")
            report.append("   3. Monitor logs for any startup issues")
            report.append("   4. Verify all endpoints respond correctly")
            report.append("   5. Set up monitoring and alerting")
        
        report.append("=" * 60)
        
        return success, "\n".join(report)

def main():
    """Main deployment validation"""
    print("🚀 InterviewAgent Production Deployment Validator")
    print("=" * 60)
    
    validator = ProductionValidator()
    
    # Run all validations
    validations = [
        ("Environment", validator.validate_environment),
        ("Application Config", validator.validate_application_config),
        ("Dependencies", validator.validate_dependencies),
        ("Development Code", validator.check_mock_dependencies),
    ]
    
    for validation_name, validation_func in validations:
        try:
            result = validation_func()
            status = "✅" if result else "❌"
            logger.info(f"{status} {validation_name} validation complete")
        except Exception as e:
            validator.errors.append(f"{validation_name} validation crashed: {e}")
            logger.error(f"❌ {validation_name} validation failed: {e}")
    
    # Generate and display report
    success, report = validator.generate_report()
    print(report)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())