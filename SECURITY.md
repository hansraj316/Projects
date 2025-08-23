# Security Policy

## Supported Projects

This repository contains multiple projects. Security updates are actively maintained for:

| Project | Status | Last Updated |
| ------- | ------ | ------------ |
| InterviewAgent | :white_check_mark: Active | 2025 |
| CoachAI | :white_check_mark: Active | 2025 |
| ai_agent_project | :white_check_mark: Active | 2025 |
| Project Starlink | :construction: Development | 2025 |
| Azure DevOps MCP | :white_check_mark: Active | 2025 |
| Other projects | :warning: Limited support | - |

## Security Considerations

### High-Risk Components
- **Credential Management**: Multiple projects handle API keys and sensitive data
- **Web Automation**: Browser automation tools (Playwright) with potential security implications
- **Database Access**: Projects with database connections require secure configuration
- **File Operations**: Projects that read/write files need proper validation

### Known Security Features
- Environment variable usage for secrets (`.env` files)
- Input validation in database operations
- Secure credential storage patterns
- Logging without sensitive data exposure

## Reporting a Vulnerability

### How to Report
1. **DO NOT** create a public issue for security vulnerabilities
2. Email security concerns directly to the maintainer
3. Use encrypted communication when possible
4. Include detailed information about the vulnerability

### What to Include
- Clear description of the vulnerability
- Steps to reproduce the issue
- Affected projects/components
- Potential impact assessment
- Suggested remediation (if available)

### Response Timeline
- **Initial Response**: Within 48 hours of report
- **Assessment**: Within 7 days
- **Resolution**: Varies by severity (1-30 days)
- **Disclosure**: After fix is deployed

### Severity Classification
- **Critical**: Immediate access to sensitive data or systems
- **High**: Potential for significant data exposure
- **Medium**: Limited access or information disclosure
- **Low**: Minor security improvements

## Security Best Practices

### For Contributors
- Never commit secrets, API keys, or passwords
- Use environment variables for configuration
- Validate all user inputs
- Follow secure coding practices
- Keep dependencies updated

### For Users
- Use strong, unique credentials
- Keep software updated
- Review configuration files
- Monitor logs for suspicious activity
- Use HTTPS for web applications

## Dependencies and Updates

Regular security audits are performed on:
- Python packages (requirements.txt)
- Node.js packages (package.json)
- System dependencies
- Third-party services integration

## Contact Information

For security-related questions or concerns:
- Create a private issue in this repository
- Tag maintainers for urgent security matters
- Allow reasonable time for response and resolution
