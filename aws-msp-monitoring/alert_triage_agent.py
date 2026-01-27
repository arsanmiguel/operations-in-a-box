#!/usr/bin/env python3
"""
Alert Triage Agent - Bedrock-powered intelligent alert routing
Integrates with existing ops-in-a-box monitoring stack
"""

import boto3
import json
import requests
from datetime import datetime

class AlertTriageAgent:
    def __init__(self, bedrock_model="anthropic.claude-3-5-sonnet-20241022-v2:0"):
        self.bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.model = bedrock_model
        
    def analyze_alert(self, alert_data):
        """Use Bedrock to analyze alert and determine routing"""
        
        prompt = f"""You are an expert SRE analyzing a monitoring alert. Based on the alert details, determine:
1. Root cause analysis
2. Severity assessment
3. Which ticketing systems to notify (can be multiple)
4. Whether auto-remediation should be attempted
5. Suggested remediation steps

Alert Details:
{json.dumps(alert_data, indent=2)}

Available ticketing systems:
- aws-support (for AWS resource issues, critical severity)
- servicenow (enterprise ITSM)
- bmc-helix (enterprise ITSM)
- jira-service-mgmt (agile teams)
- zendesk (customer support)
- freshworks (customer support)
- linear (engineering teams)
- aws-config (compliance/configuration issues)

Respond in JSON format:
{{
  "root_cause": "brief explanation",
  "severity": "critical|high|medium|low",
  "targets": ["system1", "system2"],
  "auto_remediate": true|false,
  "remediation_steps": ["step1", "step2"],
  "ticket_summary": "concise summary for ticket",
  "ticket_description": "detailed description with context"
}}"""

        response = self.bedrock.invoke_model(
            modelId=self.model,
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2000,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            })
        )
        
        result = json.loads(response['body'].read())
        analysis = json.loads(result['content'][0]['text'])
        return analysis
    
    def route_alert(self, alert_data, analysis):
        """Route alert to appropriate systems based on agent analysis"""
        
        results = []
        
        for target in analysis['targets']:
            if target == 'aws-support':
                result = self._create_aws_support_case(alert_data, analysis)
            elif target == 'servicenow':
                result = self._create_servicenow_ticket(alert_data, analysis)
            elif target == 'bmc-helix':
                result = self._create_bmc_ticket(alert_data, analysis)
            elif target == 'jira-service-mgmt':
                result = self._create_jira_ticket(alert_data, analysis)
            elif target == 'zendesk':
                result = self._create_zendesk_ticket(alert_data, analysis)
            elif target == 'freshworks':
                result = self._create_freshworks_ticket(alert_data, analysis)
            elif target == 'linear':
                result = self._create_linear_ticket(alert_data, analysis)
            elif target == 'aws-config':
                result = self._log_to_aws_config(alert_data, analysis)
            else:
                result = {'target': target, 'status': 'unknown_target'}
            
            results.append(result)
        
        # Trigger auto-remediation if recommended
        if analysis.get('auto_remediate'):
            remediation_result = self._trigger_auto_remediation(alert_data, analysis)
            results.append(remediation_result)
        
        return results
    
    def _create_aws_support_case(self, alert_data, analysis):
        """Create AWS Support case via existing plugin"""
        try:
            # Call existing aws-support plugin API
            response = requests.post(
                'http://localhost:9217/api/create-case',
                json={
                    'subject': analysis['ticket_summary'],
                    'description': analysis['ticket_description'],
                    'severity': analysis['severity'],
                    'category': 'technical',
                    'alert_data': alert_data
                }
            )
            return {
                'target': 'aws-support',
                'status': 'success',
                'case_id': response.json().get('case_id')
            }
        except Exception as e:
            return {'target': 'aws-support', 'status': 'error', 'error': str(e)}
    
    def _create_servicenow_ticket(self, alert_data, analysis):
        """Create ServiceNow ticket via existing plugin"""
        try:
            response = requests.post(
                'http://localhost:9218/api/create-incident',
                json={
                    'short_description': analysis['ticket_summary'],
                    'description': analysis['ticket_description'],
                    'urgency': self._map_severity_to_urgency(analysis['severity']),
                    'alert_data': alert_data
                }
            )
            return {
                'target': 'servicenow',
                'status': 'success',
                'ticket_id': response.json().get('incident_number')
            }
        except Exception as e:
            return {'target': 'servicenow', 'status': 'error', 'error': str(e)}
    
    def _create_bmc_ticket(self, alert_data, analysis):
        """Create BMC Helix ticket via existing plugin"""
        try:
            response = requests.post(
                'http://localhost:9219/api/create-incident',
                json={
                    'summary': analysis['ticket_summary'],
                    'details': analysis['ticket_description'],
                    'priority': analysis['severity'],
                    'alert_data': alert_data
                }
            )
            return {
                'target': 'bmc-helix',
                'status': 'success',
                'ticket_id': response.json().get('incident_id')
            }
        except Exception as e:
            return {'target': 'bmc-helix', 'status': 'error', 'error': str(e)}
    
    def _create_jira_ticket(self, alert_data, analysis):
        """Create Jira Service Management ticket via existing plugin"""
        try:
            response = requests.post(
                'http://localhost:9220/api/create-issue',
                json={
                    'summary': analysis['ticket_summary'],
                    'description': analysis['ticket_description'],
                    'priority': analysis['severity'],
                    'alert_data': alert_data
                }
            )
            return {
                'target': 'jira-service-mgmt',
                'status': 'success',
                'ticket_id': response.json().get('issue_key')
            }
        except Exception as e:
            return {'target': 'jira-service-mgmt', 'status': 'error', 'error': str(e)}
    
    def _create_zendesk_ticket(self, alert_data, analysis):
        """Create Zendesk ticket via existing plugin"""
        try:
            response = requests.post(
                'http://localhost:9221/api/create-ticket',
                json={
                    'subject': analysis['ticket_summary'],
                    'description': analysis['ticket_description'],
                    'priority': analysis['severity'],
                    'alert_data': alert_data
                }
            )
            return {
                'target': 'zendesk',
                'status': 'success',
                'ticket_id': response.json().get('ticket_id')
            }
        except Exception as e:
            return {'target': 'zendesk', 'status': 'error', 'error': str(e)}
    
    def _create_freshworks_ticket(self, alert_data, analysis):
        """Create Freshworks ticket via existing plugin"""
        try:
            response = requests.post(
                'http://localhost:9222/api/create-ticket',
                json={
                    'subject': analysis['ticket_summary'],
                    'description': analysis['ticket_description'],
                    'priority': self._map_severity_to_priority(analysis['severity']),
                    'alert_data': alert_data
                }
            )
            return {
                'target': 'freshworks',
                'status': 'success',
                'ticket_id': response.json().get('ticket_id')
            }
        except Exception as e:
            return {'target': 'freshworks', 'status': 'error', 'error': str(e)}
    
    def _create_linear_ticket(self, alert_data, analysis):
        """Create Linear issue via existing plugin"""
        try:
            response = requests.post(
                'http://localhost:9223/api/create-issue',
                json={
                    'title': analysis['ticket_summary'],
                    'description': analysis['ticket_description'],
                    'priority': self._map_severity_to_linear_priority(analysis['severity']),
                    'alert_data': alert_data
                }
            )
            return {
                'target': 'linear',
                'status': 'success',
                'ticket_id': response.json().get('issue_id')
            }
        except Exception as e:
            return {'target': 'linear', 'status': 'error', 'error': str(e)}
    
    def _log_to_aws_config(self, alert_data, analysis):
        """Log to AWS Config via existing plugin"""
        try:
            response = requests.post(
                'http://localhost:9224/api/log-compliance-event',
                json={
                    'resource_id': alert_data.get('resource_id'),
                    'compliance_type': 'NON_COMPLIANT',
                    'annotation': analysis['ticket_description'],
                    'alert_data': alert_data
                }
            )
            return {
                'target': 'aws-config',
                'status': 'success',
                'event_id': response.json().get('event_id')
            }
        except Exception as e:
            return {'target': 'aws-config', 'status': 'error', 'error': str(e)}
    
    def _trigger_auto_remediation(self, alert_data, analysis):
        """Trigger auto-remediation via existing plugin"""
        try:
            response = requests.post(
                'http://localhost:9225/api/remediate',
                json={
                    'alert_name': alert_data.get('alert_name'),
                    'resource_id': alert_data.get('resource_id'),
                    'remediation_steps': analysis['remediation_steps'],
                    'alert_data': alert_data
                }
            )
            return {
                'target': 'auto-remediation',
                'status': 'success',
                'remediation_id': response.json().get('remediation_id')
            }
        except Exception as e:
            return {'target': 'auto-remediation', 'status': 'error', 'error': str(e)}
    
    def _map_severity_to_urgency(self, severity):
        """Map severity to ServiceNow urgency"""
        mapping = {
            'critical': '1',
            'high': '2',
            'medium': '3',
            'low': '4'
        }
        return mapping.get(severity, '3')
    
    def _map_severity_to_priority(self, severity):
        """Map severity to numeric priority"""
        mapping = {
            'critical': 1,
            'high': 2,
            'medium': 3,
            'low': 4
        }
        return mapping.get(severity, 3)
    
    def _map_severity_to_linear_priority(self, severity):
        """Map severity to Linear priority"""
        mapping = {
            'critical': 1,
            'high': 2,
            'medium': 3,
            'low': 4
        }
        return mapping.get(severity, 3)


def handle_prometheus_alert(alert_webhook_data):
    """Main handler for Prometheus AlertManager webhook"""
    
    agent = AlertTriageAgent()
    
    # Extract alert data
    alert_data = {
        'alert_name': alert_webhook_data['commonLabels'].get('alertname'),
        'severity': alert_webhook_data['commonLabels'].get('severity'),
        'instance': alert_webhook_data['commonLabels'].get('instance'),
        'resource_id': alert_webhook_data['commonLabels'].get('resource_id'),
        'description': alert_webhook_data['commonAnnotations'].get('description'),
        'summary': alert_webhook_data['commonAnnotations'].get('summary'),
        'timestamp': datetime.now().isoformat(),
        'raw_alert': alert_webhook_data
    }
    
    # Analyze with Bedrock
    print(f"🤖 Analyzing alert: {alert_data['alert_name']}")
    analysis = agent.analyze_alert(alert_data)
    
    print(f"📊 Analysis complete:")
    print(f"  Root cause: {analysis['root_cause']}")
    print(f"  Severity: {analysis['severity']}")
    print(f"  Targets: {', '.join(analysis['targets'])}")
    print(f"  Auto-remediate: {analysis['auto_remediate']}")
    
    # Route to appropriate systems
    print(f"🚀 Routing alert to {len(analysis['targets'])} system(s)...")
    results = agent.route_alert(alert_data, analysis)
    
    # Print results
    for result in results:
        status_emoji = "✅" if result['status'] == 'success' else "❌"
        print(f"{status_emoji} {result['target']}: {result['status']}")
        if result['status'] == 'success' and 'ticket_id' in result:
            print(f"   Ticket ID: {result.get('ticket_id') or result.get('case_id') or result.get('event_id')}")
    
    return {
        'analysis': analysis,
        'routing_results': results
    }


if __name__ == '__main__':
    # Example alert from Prometheus
    example_alert = {
        'commonLabels': {
            'alertname': 'HighCPUUsage',
            'severity': 'critical',
            'instance': 'i-1234567890abcdef0',
            'resource_id': 'arn:aws:ec2:us-east-1:123456789012:instance/i-1234567890abcdef0',
            'job': 'ec2-monitoring'
        },
        'commonAnnotations': {
            'summary': 'High CPU usage detected on production instance',
            'description': 'CPU usage has been above 95% for the last 10 minutes on instance i-1234567890abcdef0'
        }
    }
    
    result = handle_prometheus_alert(example_alert)
    print(f"\n✨ Alert triage complete!")
