from flask import Flask, request, jsonify, abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
import os
import time
import re
import hmac
from functools import wraps

app = Flask(__name__)
API_KEY = os.getenv('API_KEY', 'eSrEB85UONWS5ytxtXxT0G88BWFSh9ZVZM-AyhUgtyA')

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per hour", "10 per minute"]
)
limiter.init_app(app)

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        provided_key = request.headers.get('X-API-Key')
        if not provided_key or not hmac.compare_digest(provided_key, API_KEY):
            abort(401, description="Invalid API key")
        return f(*args, **kwargs)
    return decorated_function

def validate_metric_name(name):
    return bool(re.match(r'^[a-zA-Z_:][a-zA-Z0-9_:]*$', name)) and len(name) <= 100

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000'
    return response

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': time.time()})

@app.route('/api/metrics', methods=['POST'])
@require_api_key
@limiter.limit("50 per minute")
def push_metrics():
    try:
        data = request.json
        app_name = data.get('app_name', '').strip()
        metric_name = data.get('metric_name', '').strip()
        metric_value = data.get('value')
        
        if not app_name or not validate_metric_name(metric_name):
            abort(400, description="Invalid input")
            
        if not isinstance(metric_value, (int, float)):
            abort(400, description="Invalid metric value")
        
        gateway_data = f'{metric_name} {metric_value}\n'
        
        response = requests.post(
            'http://pushgateway:9091/metrics/job/{app_name}',
            data=gateway_data,
            headers={'Content-Type': 'text/plain'},
            timeout=5
        )
        
        if response.status_code == 200:
            return jsonify({'status': 'success'})
        else:
            return jsonify({'error': 'Gateway error'}), 502
            
    except Exception:
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)