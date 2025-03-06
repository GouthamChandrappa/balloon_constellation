from flask import Flask, render_template, jsonify, request
from balloon_data_fetcher import BalloonDataFetcher
from llm_analyzer import BalloonAnalyzer
from datetime import datetime
import os
import json

app = Flask(__name__)

# Initialize the data fetcher
fetcher = BalloonDataFetcher()

# Store for LLM analyzers (keyed by API key to avoid recreating)
analyzers = {}

# Cache for analysis results to avoid redundant API calls
analysis_cache = {
    'general_insights': {'timestamp': None, 'data': None},
    'anomalies': {'timestamp': None, 'data': None},
    'launch_recommendations': {'timestamp': None, 'data': None}
}

def get_analyzer(api_key):
    """Get or create an analyzer for the given API key"""
    if api_key not in analyzers:
        analyzers[api_key] = BalloonAnalyzer(api_key)
    return analyzers[api_key]

def cache_valid(cache_key, max_age_seconds=300):
    """Check if cached data is still valid"""
    cache_entry = analysis_cache.get(cache_key)
    if not cache_entry or not cache_entry['timestamp'] or not cache_entry['data']:
        return False
    
    age = (datetime.now() - cache_entry['timestamp']).total_seconds()
    return age <= max_age_seconds

@app.route('/')
def index():
    """Main page with the interactive map"""
    return render_template('index.html')

@app.route('/api/balloon-data')
def balloon_data():
    """API endpoint to get the current balloon data"""
    hours_ago = request.args.get('hours_ago', default=0, type=int)
    try:
        data = fetcher.fetch_data(hours_ago=hours_ago)
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'balloons': data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trajectory-data')
def trajectory_data():
    """API endpoint to get trajectory data for the balloons"""
    try:
        trajectories = fetcher.get_trajectories()
        # Convert to a format better suited for frontend visualization
        trajectory_list = []
        
        for balloon_id, positions in trajectories.items():
            if len(positions) > 1:
                points = [{'lat': p['latitude'], 'lng': p['longitude'], 'alt': p['altitude'], 
                           'time': p['timestamp']} for p in positions]
                
                trajectory_list.append({
                    'id': balloon_id,
                    'points': points,
                    'color': f'#{hash(str(balloon_id)) % 0xFFFFFF:06x}'  # Generate a color based on ID
                })
        
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'trajectories': trajectory_list
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_data():
    """API endpoint for LLM analysis of the balloon data"""
    api_key = request.json.get('api_key')
    question = request.json.get('question')
    
    if not api_key or not question:
        return jsonify({'error': 'Missing API key or question'}), 400
    
    try:
        analyzer = get_analyzer(api_key)
        analysis = analyzer.analyze_question(question)
        return jsonify({
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': f"Analysis error: {str(e)}"}), 500

@app.route('/api/insights', methods=['POST'])
def get_insights():
    """API endpoint for getting general insights about the constellation"""
    api_key = request.json.get('api_key')
    
    if not api_key:
        return jsonify({'error': 'Missing API key'}), 400
    
    # Check if we have valid cached insights
    if cache_valid('general_insights'):
        return jsonify({
            'insights': analysis_cache['general_insights']['data'],
            'timestamp': analysis_cache['general_insights']['timestamp'].isoformat(),
            'cached': True
        })
    
    try:
        analyzer = get_analyzer(api_key)
        insights = analyzer.analyze_question("Provide a general overview of the current balloon constellation status and any notable patterns or observations.")
        
        # Update cache
        analysis_cache['general_insights'] = {
            'timestamp': datetime.now(),
            'data': insights
        }
        
        return jsonify({
            'insights': insights,
            'timestamp': datetime.now().isoformat(),
            'cached': False
        })
    except Exception as e:
        return jsonify({'error': f"Analysis error: {str(e)}"}), 500

@app.route('/api/anomalies', methods=['POST'])
def get_anomalies():
    """API endpoint for detecting anomalies in the constellation"""
    api_key = request.json.get('api_key')
    
    if not api_key:
        return jsonify({'error': 'Missing API key'}), 400
    
    # Check if we have valid cached anomalies
    if cache_valid('anomalies'):
        return jsonify({
            'anomalies': analysis_cache['anomalies']['data'],
            'timestamp': analysis_cache['anomalies']['timestamp'].isoformat(),
            'cached': True
        })
    
    try:
        analyzer = get_analyzer(api_key)
        anomalies = analyzer.identify_anomalies()
        
        # Update cache
        analysis_cache['anomalies'] = {
            'timestamp': datetime.now(),
            'data': anomalies
        }
        
        return jsonify({
            'anomalies': anomalies,
            'timestamp': datetime.now().isoformat(),
            'cached': False
        })
    except Exception as e:
        return jsonify({'error': f"Analysis error: {str(e)}"}), 500

@app.route('/api/launch-recommendations', methods=['POST'])
def get_launch_recommendations():
    """API endpoint for getting launch recommendations"""
    api_key = request.json.get('api_key')
    
    if not api_key:
        return jsonify({'error': 'Missing API key'}), 400
    
    # Check if we have valid cached recommendations
    if cache_valid('launch_recommendations'):
        return jsonify({
            'recommendations': analysis_cache['launch_recommendations']['data'],
            'timestamp': analysis_cache['launch_recommendations']['timestamp'].isoformat(),
            'cached': True
        })
    
    try:
        analyzer = get_analyzer(api_key)
        recommendations = analyzer.get_launch_recommendations()
        
        # Update cache
        analysis_cache['launch_recommendations'] = {
            'timestamp': datetime.now(),
            'data': recommendations
        }
        
        return jsonify({
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat(),
            'cached': False
        })
    except Exception as e:
        return jsonify({'error': f"Analysis error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)