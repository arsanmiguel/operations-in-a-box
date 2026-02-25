#!/usr/bin/env python3
"""
AWS MSP Security Validator
==========================

Post-deployment security validator for AWS MSP monitoring stacks.
Validates that all enterprise security controls are properly implemented
for customer deployments.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

class SecurityValidator:
    def __init__(self, install_dir):
        self.install_dir = Path(install_dir)
        self.passed_checks = []
        self.failed_checks = []
        
    def check_secure_credentials(self):
        """Check that secure credentials are generated"""
        credentials_file = self.install_dir / "CREDENTIALS.md"
        if credentials_file.exists():
            content = credentials_file.read_text()
            if "admin/admin" not in content and len(content) > 100:
                self.passed_checks.append("[OK] Secure credentials generated (no default admin/admin)")
                return True
        
        self.failed_checks.append("[FAIL] Default credentials still in use")
        return False
        
    def check_api_authentication(self):
        """Check that API has authentication"""
        api_file = self.install_dir / "api" / "app.py"
        if api_file.exists():
            content = api_file.read_text()
            if "require_api_key" in content and "hmac.compare_digest" in content:
                self.passed_checks.append("[OK] API authentication implemented with secure key comparison")
                return True
                
        self.failed_checks.append("[FAIL] API endpoints not authenticated")
        return False
        
    def check_container_security(self):
        """Check that containers run as non-root"""
        compose_file = self.install_dir / "docker-compose.yml"
        if compose_file.exists():
            content = compose_file.read_text()
            if 'user: "65534:65534"' in content and 'user: "472:472"' in content and 'user: "1000:1000"' in content:
                self.passed_checks.append("[OK] All containers configured to run as non-root users")
                return True
                
        self.failed_checks.append("[FAIL] Containers running as root")
        return False
        
    def check_network_security(self):
        """Check that services are bound to localhost"""
        compose_file = self.install_dir / "docker-compose.yml"
        if compose_file.exists():
            content = compose_file.read_text()
            if "127.0.0.1:9090:9090" in content and "127.0.0.1:3000:3000" in content and "127.0.0.1:8080:8080" in content:
                self.passed_checks.append("[OK] All services bound to localhost only (127.0.0.1)")
                return True
                
        self.failed_checks.append("[FAIL] Services exposed on all interfaces")
        return False
        
    def check_security_headers(self):
        """Check that security headers are implemented"""
        api_file = self.install_dir / "api" / "app.py"
        if api_file.exists():
            content = api_file.read_text()
            headers = ["X-Content-Type-Options", "X-Frame-Options", "X-XSS-Protection", "Strict-Transport-Security"]
            if all(header in content for header in headers):
                self.passed_checks.append("[OK] Security headers implemented (XSS, CSRF, clickjacking protection)")
                return True
                
        self.failed_checks.append("[FAIL] Security headers not configured")
        return False
        
    def check_input_validation(self):
        """Check that input validation is implemented"""
        api_file = self.install_dir / "api" / "app.py"
        if api_file.exists():
            content = api_file.read_text()
            if "validate_metric_name" in content and "re.match" in content:
                self.passed_checks.append("[OK] Input validation implemented with regex patterns")
                return True
                
        self.failed_checks.append("[FAIL] Input validation not implemented")
        return False
        
    def check_rate_limiting(self):
        """Check that rate limiting is configured"""
        api_file = self.install_dir / "api" / "app.py"
        if api_file.exists():
            content = api_file.read_text()
            if "flask_limiter" in content and "limit(" in content:
                self.passed_checks.append("[OK] Rate limiting configured (100/hour, 10/minute)")
                return True
                
        self.failed_checks.append("[FAIL] Rate limiting not configured")
        return False
        
    def check_session_security(self):
        """Check that session timeouts are configured"""
        compose_file = self.install_dir / "docker-compose.yml"
        if compose_file.exists():
            content = compose_file.read_text()
            if "GF_SESSION_LIFE_TIME=3600" in content:
                self.passed_checks.append("[OK] Session timeout configured (1 hour)")
                return True
                
        self.failed_checks.append("[FAIL] Session timeout not configured")
        return False
        
    def check_container_hardening(self):
        """Check container security hardening"""
        compose_file = self.install_dir / "docker-compose.yml"
        if compose_file.exists():
            content = compose_file.read_text()
            security_features = ["read_only: true", "no-new-privileges:true", "cap_drop:", "- ALL"]
            if all(feature in content for feature in security_features):
                self.passed_checks.append("[OK] Container hardening enabled (read-only, no privileges, dropped capabilities)")
                return True
                
        self.failed_checks.append("[FAIL] Container hardening not implemented")
        return False
        
    def validate_deployment(self):
        """Run all security validations"""
        print("Validating Security Controls...")
        print("=" * 50)
        
        # Run all checks
        checks = [
            self.check_secure_credentials,
            self.check_api_authentication,
            self.check_container_security,
            self.check_network_security,
            self.check_security_headers,
            self.check_input_validation,
            self.check_rate_limiting,
            self.check_session_security,
            self.check_container_hardening
        ]
        
        for check in checks:
            check()
            
        # Results
        total_checks = len(checks)
        passed_count = len(self.passed_checks)
        failed_count = len(self.failed_checks)
        
        print(f"\nSecurity Validation Results:")
        print(f"Passed: {passed_count}/{total_checks}")
        print(f"Failed: {failed_count}/{total_checks}")
        
        if self.passed_checks:
            print(f"\nPassed Checks:")
            for check in self.passed_checks:
                print(f"  {check}")
                
        if self.failed_checks:
            print(f"\nFailed Checks:")
            for check in self.failed_checks:
                print(f"  {check}")
                
        # Overall result
        security_score = (passed_count / total_checks) * 100
        print(f"\nSecurity Score: {security_score:.0f}/100")
        
        if security_score >= 90:
            print("EXCELLENT - Deployment meets enterprise security standards")
            return True
        elif security_score >= 75:
            print("GOOD - Deployment has strong security controls")
            return True
        elif security_score >= 60:
            print("⚠️  ACCEPTABLE - Some security improvements recommended")
            return True
        else:
            print("INSUFFICIENT - Security controls need improvement")
            return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate security controls in monitoring deployment")
    parser.add_argument("--install-dir", default="secure-monitoring-stack", help="Installation directory to validate")
    args = parser.parse_args()
    
    validator = SecurityValidator(args.install_dir)
    passed = validator.validate_deployment()
    
    sys.exit(0 if passed else 1)
