from flask import Flask, render_template, jsonify, request
from balloon_data_fetcher import BalloonDataFetcher
import os
from datetime import datetime
import json

app = Flask(__name__)
fetcher = BalloonDataFetcher()

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
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'trajectories': trajectories
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
    
    # Here you would implement the LLM agent to analyze the data
    # For now, just return a placeholder
    return jsonify({
        'analysis': f"Analysis of your question: '{question}' would go here. This would use the OpenAI API.",
        'timestamp': datetime.now().isoformat()
    })

# Create the templates folder and HTML file
os.makedirs('templates', exist_ok=True)
with open('templates/index.html', 'w') as f:
    f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Balloon Constellation Mission Planner</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <style>
        body {
            padding: 0;
            margin: 0;
            font-family: Arial, sans-serif;
        }
        #map {
            height: 70vh;
            width: 100%;
        }
        .container {
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }
        .controls {
            margin-bottom: 20px;
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        .panel {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .panel h3 {
            margin-top: 0;
        }
        .insights {
            margin-top: 20px;
        }
        button {
            padding: 8px 16px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background: #0069d9;
        }
        select, input {
            padding: 8px;
            border-radius: 4px;
            border: 1px solid #ced4da;
        }
        .api-key {
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Balloon Constellation Mission Planner</h1>
        
        <div class="panel">
            <h3>Map Visualization</h3>
            <div class="controls">
                <select id="timeSelector">
                    <option value="0">Current</option>
                    <option value="1">1 hour ago</option>
                    <option value="3">3 hours ago</option>
                    <option value="6">6 hours ago</option>
                    <option value="12">12 hours ago</option>
                    <option value="18">18 hours ago</option>
                    <option value="23">23 hours ago</option>
                </select>
                <button id="showTrajectories">Show Trajectories</button>
                <button id="hideTrajectories">Hide Trajectories</button>
                <button id="refreshData">Refresh Data</button>
            </div>
            <div id="map"></div>
        </div>
        
        <div class="panel">
            <h3>LLM-Powered Analysis</h3>
            <div class="api-key">
                <label for="apiKey">OpenAI API Key:</label>
                <input type="password" id="apiKey" placeholder="sk-..." style="width: 300px;">
            </div>
            <div class="insights">
                <p>Ask a question about the balloon constellation:</p>
                <input type="text" id="question" placeholder="e.g., What patterns do you see in balloon movements?" style="width: 70%;">
                <button id="analyzeButton">Analyze</button>
                <div id="analysisResult" class="panel" style="margin-top: 10px; display: none;"></div>
            </div>
        </div>
        
        <div class="panel">
            <h3>Constellation Stats</h3>
            <div id="stats">
                <p>Loading stats...</p>
            </div>
        </div>
    </div>

    <script>
        // Initialize the map
        const map = L.map('map').setView([0, 0], 2);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);
        
        // Variables to track state
        let markers = [];
        let trajectoryLines = [];
        
        // Function to load balloon data
        async function loadBalloonData(hoursAgo = 0) {
            try {
                const response = await fetch(`/api/balloon-data?hours_ago=${hoursAgo}`);
                const data = await response.json();
                
                // Clear existing markers
                markers.forEach(marker => map.removeLayer(marker));
                markers = [];
                
                // Add new markers
                data.balloons.forEach(balloon => {
                    const marker = L.marker([balloon.latitude, balloon.longitude])
                        .addTo(map)
                        .bindPopup(`Balloon ID: ${balloon.balloon_id}<br>
                                   Latitude: ${balloon.latitude.toFixed(4)}<br>
                                   Longitude: ${balloon.longitude.toFixed(4)}<br>
                                   Altitude: ${balloon.altitude.toFixed(2)} km`);
                    markers.push(marker);
                });
                
                // Update stats
                updateStats(data.balloons);
                
                return data.balloons;
            } catch (error) {
                console.error('Error loading balloon data:', error);
                return [];
            }
        }
        
        // Function to load and display trajectories
        async function loadTrajectories() {
            try {
                const response = await fetch('/api/trajectory-data');
                const data = await response.json();
                
                // Clear existing trajectory lines
                trajectoryLines.forEach(line => map.removeLayer(line));
                trajectoryLines = [];
                
                // Draw trajectories for each balloon
                Object.entries(data.trajectories).forEach(([balloonId, positions]) => {
                    if (positions.length > 1) {
                        const points = positions.map(p => [p.latitude, p.longitude]);
                        const line = L.polyline(points, {
                            color: getRandomColor(),
                            weight: 2,
                            opacity: 0.7
                        }).addTo(map);
                        trajectoryLines.push(line);
                    }
                });
            } catch (error) {
                console.error('Error loading trajectories:', error);
            }
        }
        
        // Function to hide trajectories
        function hideTrajectories() {
            trajectoryLines.forEach(line => map.removeLayer(line));
            trajectoryLines = [];
        }
        
        // Function to update stats
        function updateStats(balloons) {
            if (!balloons || balloons.length === 0) {
                document.getElementById('stats').innerHTML = '<p>No data available</p>';
                return;
            }
            
            // Calculate some basic stats
            const count = balloons.length;
            const altitudes = balloons.map(b => b.altitude);
            const avgAlt = altitudes.reduce((sum, alt) => sum + alt, 0) / count;
            
            // Count balloons by hemisphere
            const northCount = balloons.filter(b => b.latitude > 0).length;
            const southCount = balloons.filter(b => b.latitude < 0).length;
            const eastCount = balloons.filter(b => b.longitude > 0).length;
            const westCount = balloons.filter(b => b.longitude < 0).length;
            
            document.getElementById('stats').innerHTML = `
                <p><strong>Total balloons:</strong> ${count}</p>
                <p><strong>Average altitude:</strong> ${avgAlt.toFixed(2)} km</p>
                <p><strong>Northern Hemisphere:</strong> ${northCount} balloons</p>
                <p><strong>Southern Hemisphere:</strong> ${southCount} balloons</p>
                <p><strong>Eastern Hemisphere:</strong> ${eastCount} balloons</p>
                <p><strong>Western Hemisphere:</strong> ${westCount} balloons</p>
            `;
        }
        
        // Function to analyze data with LLM
        async function analyzeWithLLM(question) {
            const apiKey = document.getElementById('apiKey').value;
            if (!apiKey) {
                alert('Please enter an OpenAI API Key');
                return;
            }
            
            try {
                document.getElementById('analysisResult').innerHTML = '<p>Analyzing...</p>';
                document.getElementById('analysisResult').style.display = 'block';
                
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        api_key: apiKey,
                        question: question
                    })
                });
                
                const data = await response.json();
                document.getElementById('analysisResult').innerHTML = `<p>${data.analysis}</p>`;
            } catch (error) {
                console.error('Error analyzing data:', error);
                document.getElementById('analysisResult').innerHTML = `<p>Error: ${error.message}</p>`;
            }
        }
        
        // Utility function to generate random colors for trajectories
        function getRandomColor() {
            const letters = '0123456789ABCDEF';
            let color = '#';
            for (let i = 0; i < 6; i++) {
                color += letters[Math.floor(Math.random() * 16)];
            }
            return color;
        }
        
        // Event listeners
        document.getElementById('timeSelector').addEventListener('change', function(e) {
            loadBalloonData(parseInt(e.target.value));
        });
        
        document.getElementById('showTrajectories').addEventListener('click', function() {
            loadTrajectories();
        });
        
        document.getElementById('hideTrajectories').addEventListener('click', function() {
            hideTrajectories();
        });
        
        document.getElementById('refreshData').addEventListener('click', function() {
            const hoursAgo = parseInt(document.getElementById('timeSelector').value);
            loadBalloonData(hoursAgo);
        });
        
        document.getElementById('analyzeButton').addEventListener('click', function() {
            const question = document.getElementById('question').value;
            if (question) {
                analyzeWithLLM(question);
            } else {
                alert('Please enter a question');
            }
        });
        
        // Load initial data
        loadBalloonData();
    </script>
</body>
</html>
    ''')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)