// LLM Analysis Logic for Balloon Constellation Mission Planner

// Function to check if API key is available
function checkApiKey() {
    const apiKey = document.getElementById('apiKey').value;
    if (!apiKey) {
        showNotification('Please enter an OpenAI API Key', true);
        return false;
    }
    return true;
}

// Save API key to local storage
document.getElementById('saveApiKey').addEventListener('click', function() {
    const apiKey = document.getElementById('apiKey').value;
    if (apiKey) {
        localStorage.setItem('openai_api_key', apiKey);
        showNotification('API key saved successfully!');
    } else {
        showNotification('Please enter an API key', true);
    }
});

// Load API key from local storage
document.addEventListener('DOMContentLoaded', function() {
    const savedApiKey = localStorage.getItem('openai_api_key');
    if (savedApiKey) {
        document.getElementById('apiKey').value = savedApiKey;
    }
});

// Function to analyze data with LLM
async function analyzeWithLLM(question) {
    if (!checkApiKey()) return;
    
    const apiKey = document.getElementById('apiKey').value;
    const resultElement = document.getElementById('analysisResult');
    
    try {
        resultElement.innerHTML = '<div class="loading"></div><p>Analyzing...</p>';
        resultElement.style.display = 'block';
        
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
        
        if (response.ok) {
            resultElement.innerHTML = `<p>${data.analysis.replace(/\n/g, '<br>')}</p>`;
            showNotification('Analysis completed successfully!');
        } else {
            resultElement.innerHTML = `<p>Error: ${data.error}</p>`;
            showNotification('Error during analysis', true);
        }
    } catch (error) {
        console.error('Error analyzing data:', error);
        resultElement.innerHTML = `<p>Error: ${error.message}</p>`;
        showNotification('Error during analysis', true);
    }
}

// Function to get general insights
async function getInsights() {
    if (!checkApiKey()) return;
    
    const apiKey = document.getElementById('apiKey').value;
    const resultElement = document.getElementById('insightsResult');
    
    try {
        resultElement.innerHTML = '<div class="loading"></div><p>Generating insights...</p>';
        resultElement.style.display = 'block';
        
        const response = await fetch('/api/insights', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                api_key: apiKey
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            resultElement.innerHTML = `<p>${data.insights.replace(/\n/g, '<br>')}</p>`;
            if (data.cached) {
                resultElement.innerHTML += `<p><small>Note: This analysis is cached from ${new Date(data.timestamp).toLocaleString()}</small></p>`;
            }
            showNotification('Insights generated successfully!');
        } else {
            resultElement.innerHTML = `<p>Error: ${data.error}</p>`;
            showNotification('Error generating insights', true);
        }
    } catch (error) {
        console.error('Error getting insights:', error);
        resultElement.innerHTML = `<p>Error: ${error.message}</p>`;
        showNotification('Error generating insights', true);
    }
}

// Function to get anomalies
async function getAnomalies() {
    if (!checkApiKey()) return;
    
    const apiKey = document.getElementById('apiKey').value;
    const resultElement = document.getElementById('anomaliesResult');
    
    try {
        resultElement.innerHTML = '<div class="loading"></div><p>Detecting anomalies...</p>';
        resultElement.style.display = 'block';
        
        const response = await fetch('/api/anomalies', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                api_key: apiKey
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            resultElement.innerHTML = `<p>${data.anomalies.replace(/\n/g, '<br>')}</p>`;
            if (data.cached) {
                resultElement.innerHTML += `<p><small>Note: This analysis is cached from ${new Date(data.timestamp).toLocaleString()}</small></p>`;
            }
            showNotification('Anomalies detected successfully!');
        } else {
            resultElement.innerHTML = `<p>Error: ${data.error}</p>`;
            showNotification('Error detecting anomalies', true);
        }
    } catch (error) {
        console.error('Error detecting anomalies:', error);
        resultElement.innerHTML = `<p>Error: ${error.message}</p>`;
        showNotification('Error detecting anomalies', true);
    }
}

// Function to get launch recommendations
async function getLaunchRecommendations() {
    if (!checkApiKey()) return;
    
    const apiKey = document.getElementById('apiKey').value;
    const resultElement = document.getElementById('launchResult');
    
    try {
        resultElement.innerHTML = '<div class="loading"></div><p>Generating launch recommendations...</p>';
        resultElement.style.display = 'block';
        
        const response = await fetch('/api/launch-recommendations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                api_key: apiKey
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            resultElement.innerHTML = `<p>${data.recommendations.replace(/\n/g, '<br>')}</p>`;
            if (data.cached) {
                resultElement.innerHTML += `<p><small>Note: This analysis is cached from ${new Date(data.timestamp).toLocaleString()}</small></p>`;
            }
            showNotification('Launch recommendations generated successfully!');
        } else {
            resultElement.innerHTML = `<p>Error: ${data.error}</p>`;
            showNotification('Error generating recommendations', true);
        }
    } catch (error) {
        console.error('Error getting recommendations:', error);
        resultElement.innerHTML = `<p>Error: ${error.message}</p>`;
        showNotification('Error generating recommendations', true);
    }
}

// Tab functionality
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', function() {
        // Remove active class from all tabs
        document.querySelectorAll('.tab').forEach(t => {
            t.classList.remove('active');
        });
        // Add active class to clicked tab
        this.classList.add('active');
        
        // Hide all tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        
        // Show the selected tab content
        const tabId = this.getAttribute('data-tab') + 'Tab';
        document.getElementById(tabId).classList.add('active');
    });
});

// Event listeners for analysis buttons
document.getElementById('analyzeButton').addEventListener('click', function() {
    const question = document.getElementById('question').value;
    if (question) {
        analyzeWithLLM(question);
    } else {
        showNotification('Please enter a question', true);
    }
});

document.getElementById('getInsightsButton').addEventListener('click', function() {
    getInsights();
});

document.getElementById('getAnomaliesButton').addEventListener('click', function() {
    getAnomalies();
});

document.getElementById('getLaunchRecsButton').addEventListener('click', function() {
    getLaunchRecommendations();
});