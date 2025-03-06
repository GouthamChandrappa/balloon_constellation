// Map Visualization Logic for Balloon Constellation Mission Planner

// Initialize the map
const map = L.map('map').setView([0, 0], 2);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Variables to track state
let markers = [];
let trajectoryLines = [];
let balloonColors = {};

// Utility function to generate a consistent color for a balloon ID
function getBalloonColor(balloonId) {
    if (!balloonColors[balloonId]) {
        // Generate a color based on the ID to ensure consistency
        const hue = (parseInt(balloonId) * 137.5) % 360;
        balloonColors[balloonId] = `hsl(${hue}, 70%, 50%)`;
    }
    return balloonColors[balloonId];
}

// Function to load balloon data
async function loadBalloonData(hoursAgo = 0) {
    try {
        showNotification('Loading balloon data...');
        
        const response = await fetch(`/api/balloon-data?hours_ago=${hoursAgo}`);
        const data = await response.json();
        
        // Clear existing markers
        markers.forEach(marker => map.removeLayer(marker));
        markers = [];
        
        // Add new markers
        data.balloons.forEach(balloon => {
            const color = getBalloonColor(balloon.balloon_id);
            
            // Create custom icon with the balloon's color
            const icon = L.divIcon({
                className: 'custom-div-icon',
                html: `<div style="background-color: ${color}; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white;"></div>`,
                iconSize: [16, 16],
                iconAnchor: [8, 8]
            });
            
            const marker = L.marker([balloon.latitude, balloon.longitude], {icon: icon})
                .addTo(map)
                .bindPopup(`<b>Balloon ID:</b> ${balloon.balloon_id}<br>
                           <b>Latitude:</b> ${balloon.latitude.toFixed(4)}<br>
                           <b>Longitude:</b> ${balloon.longitude.toFixed(4)}<br>
                           <b>Altitude:</b> ${balloon.altitude.toFixed(2)} km`);
            markers.push(marker);
        });
        
        // Update stats
        updateStats(data.balloons);
        
        // Update legend
        updateLegend(data.balloons);
        
        showNotification('Balloon data loaded successfully!');
        return data.balloons;
    } catch (error) {
        console.error('Error loading balloon data:', error);
        showNotification('Error loading balloon data', true);
        return [];
    }
}

// Function to load and display trajectories
async function loadTrajectories() {
    try {
        showNotification('Loading trajectory data...');
        
        const response = await fetch('/api/trajectory-data');
        const data = await response.json();
        
        // Clear existing trajectory lines
        trajectoryLines.forEach(line => map.removeLayer(line));
        trajectoryLines = [];
        
        // Draw trajectories for each balloon
        data.trajectories.forEach(trajectory => {
            if (trajectory.points.length > 1) {
                const points = trajectory.points.map(p => [p.lat, p.lng]);
                const color = getBalloonColor(trajectory.id);
                
                const line = L.polyline(points, {
                    color: color,
                    weight: 3,
                    opacity: 0.7,
                    dashArray: '5, 5'  // Make line dashed
                }).addTo(map);
                
                line.bindPopup(`<b>Balloon ID:</b> ${trajectory.id}<br>
                              <b>Points:</b> ${trajectory.points.length}<br>
                              <b>Time span:</b> ${trajectory.points.length} hours`);
                
                trajectoryLines.push(line);
            }
        });
        
        showNotification('Trajectories loaded successfully!');
    } catch (error) {
        console.error('Error loading trajectories:', error);
        showNotification('Error loading trajectories', true);
    }
}

// Function to hide trajectories
function hideTrajectories() {
    trajectoryLines.forEach(line => map.removeLayer(line));
    trajectoryLines = [];
    showNotification('Trajectories hidden');
}

// Function to update the map legend
function updateLegend(balloons) {
    const legend = document.getElementById('mapLegend');
    legend.innerHTML = '<h4>Balloon Legend</h4>';
    
    // Get unique balloon IDs
    const uniqueIds = [...new Set(balloons.map(b => b.balloon_id))];
    
    // Create legend items for a subset of balloons (to avoid overcrowding)
    const displayCount = Math.min(uniqueIds.length, 10);
    for (let i = 0; i < displayCount; i++) {
        const id = uniqueIds[i];
        const color = getBalloonColor(id);
        
        const legendItem = document.createElement('div');
        legendItem.className = 'legend-item';
        legendItem.innerHTML = `
            <div class="legend-color" style="background-color: ${color}"></div>
            <span>Balloon ID: ${id}</span>
        `;
        legend.appendChild(legendItem);
    }
    
    // Add note if there are more balloons
    if (uniqueIds.length > displayCount) {
        const note = document.createElement('div');
        note.innerHTML = `<small>+ ${uniqueIds.length - displayCount} more balloons</small>`;
        legend.appendChild(note);
    }
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
    const maxAlt = Math.max(...altitudes);
    const minAlt = Math.min(...altitudes);
    
    // Count balloons by hemisphere
    const northCount = balloons.filter(b => b.latitude > 0).length;
    const southCount = balloons.filter(b => b.latitude < 0).length;
    const eastCount = balloons.filter(b => b.longitude > 0).length;
    const westCount = balloons.filter(b => b.longitude < 0).length;
    
    // Group balloons by altitude ranges
    const lowAlt = balloons.filter(b => b.altitude < 5).length;
    const midAlt = balloons.filter(b => b.altitude >= 5 && b.altitude < 15).length;
    const highAlt = balloons.filter(b => b.altitude >= 15).length;
    
    document.getElementById('stats').innerHTML = `
        <div class="balloon-stat"><span>Total balloons:</span> <span>${count}</span></div>
        <div class="balloon-stat"><span>Average altitude:</span> <span>${avgAlt.toFixed(2)} km</span></div>
        <div class="balloon-stat"><span>Altitude range:</span> <span>${minAlt.toFixed(2)} - ${maxAlt.toFixed(2)} km</span></div>
        <div class="balloon-stat"><span>Low altitude (< 5km):</span> <span>${lowAlt} balloons</span></div>
        <div class="balloon-stat"><span>Mid altitude (5-15km):</span> <span>${midAlt} balloons</span></div>
        <div class="balloon-stat"><span>High altitude (> 15km):</span> <span>${highAlt} balloons</span></div>
        <div class="balloon-stat"><span>Northern Hemisphere:</span> <span>${northCount} balloons</span></div>
        <div class="balloon-stat"><span>Southern Hemisphere:</span> <span>${southCount} balloons</span></div>
        <div class="balloon-stat"><span>Eastern Hemisphere:</span> <span>${eastCount} balloons</span></div>
        <div class="balloon-stat"><span>Western Hemisphere:</span> <span>${westCount} balloons</span></div>
    `;
}

// Function to show notifications
function showNotification(message, isError = false) {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.style.borderLeftColor = isError ? '#dc3545' : '#1a73e8';
    notification.classList.add('show');
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

// Event listeners for map controls
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

// Load initial data when the page loads
document.addEventListener('DOMContentLoaded', function() {
    loadBalloonData();
});