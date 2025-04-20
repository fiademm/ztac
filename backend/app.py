from flask import Flask, request, jsonify
from prometheus_client import start_http_server, Gauge
import time

app = Flask(__name__)
trust_scores = {}  # Stores user trust scores

# Prometheus metric
trust_metric = Gauge('user_trust_score', 'Trust score per user', ['user_id'])

def calculate_trust(user_id, device_change=False, mfa_used=False):
    """Simple trust scoring logic (0-100)"""
    score = 70  # Base score
    
    # Penalize for device changes
    if device_change:
        score -= 20
    
    # Reward for MFA
    if mfa_used:
        score += 15
    
    # Ensure score stays between 0-100
    return max(0, min(100, score))

@app.route('/update_trust', methods=['POST'])
def update_trust():
    data = request.json
    user_id = data['user_id']
    new_score = calculate_trust(
        user_id,
        device_change=data.get('device_change', False),
        mfa_used=data.get('mfa_used', False)
    )
    
    trust_scores[user_id] = new_score
    trust_metric.labels(user_id=user_id).set(new_score)
    
    return jsonify({"trust_score": new_score})

@app.route('/check_access', methods=['GET'])
def check_access():
    user_id = request.args.get('user_id')
    required_trust = 70  # Threshold
    
    if trust_scores.get(user_id, 0) >= required_trust:
        return jsonify({"access": "granted"})
    else:
        return jsonify({"access": "denied"})

if __name__ == '__main__':
    start_http_server(8000)  # Prometheus metrics on port 8000
    app.run(host='0.0.0.0', port=5000, debug=True)