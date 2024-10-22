// app.js
const socket = io();

// Video elements
const videoStream = document.getElementById('video-stream');
const surfaceImaging = document.getElementById('surface-imaging');
const underwaterImaging = document.getElementById('underwater-imaging');

// Telemetry elements
const trajectoryCanvas = document.getElementById('trajectoryChart');
const batteryLevel = document.getElementById('battery-level');
const sogFill = document.getElementById('sog-fill');
const sogValue = document.getElementById('sog-value');
const cogLine = document.getElementById('cog-line');
const cogValue = document.getElementById('cog-value');
const surfaceCoordinate = document.getElementById('surface-coordinate');
const underwaterCoordinate = document.getElementById('underwater-coordinate');
const timeElements = document.querySelectorAll('[id$="time"]');
const dateElements = document.querySelectorAll('[id$="date"]');

// Initialize Chart.js trajectory
let trajectoryChart;

function initTrajectoryChart() {
    const ctx = trajectoryCanvas.getContext('2d');
    trajectoryChart = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Vehicle Path',
                data: [],
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 2,
                showLine: true,
                fill: false,
                pointRadius: 0
            }]
        },
        options: {
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    title: {
                        display: true,
                        text: 'Longitude Offset (m)'
                    }
                },
                y: {
                    type: 'linear',
                    title: {
                        display: true,
                        text: 'Latitude Offset (m)'
                    }
                }
            },
            animation: false,
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

function updateVideoElements(videoData) {
    if (videoData.main) {
        videoStream.src = `data:image/jpeg;base64,${videoData.main}`;
    }
    if (videoData.surface) {
        surfaceImaging.style.backgroundImage = `url(data:image/jpeg;base64,${videoData.surface})`;
    }
    if (videoData.underwater) {
        underwaterImaging.style.backgroundImage = `url(data:image/jpeg;base64,${videoData.underwater})`;
    }
}

function updateTelemetry(telemetry) {
    // Update battery
    const battery = telemetry.battery || 0;
    batteryLevel.style.width = `${battery}%`;
    batteryLevel.textContent = `${battery}%`;
    batteryLevel.style.backgroundColor = battery > 50 ? '#4caf50' : battery > 20 ? '#ffeb3b' : '#f44336';

    // Update SOG
    const speed = telemetry.speed || 0;
    const maxSpeed = 30; // Maximum expected speed in knots
    const sogPercentage = Math.min((speed / maxSpeed) * 100, 100);
    sogFill.style.width = `${sogPercentage}%`;
    sogValue.textContent = `${speed.toFixed(2)} knots`;

    // Update COG
    const heading = telemetry.heading || 0;
    cogLine.style.transform = `rotate(${heading}deg)`;
    cogValue.textContent = `${heading.toFixed(1)}°`;

    // Update coordinates
    const coordText = `[S ${telemetry.latitude.toFixed(5)} E ${telemetry.longitude.toFixed(5)}]`;
    surfaceCoordinate.textContent = coordText;
    underwaterCoordinate.textContent = coordText;

    // Update trajectory
    if (telemetry.trajectory && trajectoryChart) {
        trajectoryChart.data.datasets[0].data = telemetry.trajectory.map(point => ({
            x: point[0],
            y: point[1]
        }));
        trajectoryChart.update('none'); // Update without animation
    }
}

function updateDateTime(timestamp) {
    const date = new Date(timestamp);
    const dateStr = date.toLocaleDateString();
    const timeStr = date.toLocaleTimeString();

    dateElements.forEach(el => el.textContent = dateStr);
    timeElements.forEach(el => el.textContent = timeStr);
}

// Socket.IO event handlers
socket.on('connect', () => {
    console.log('Connected to server');
    initTrajectoryChart();
});

socket.on('data_update', (data) => {
    updateVideoElements(data.video);
    updateTelemetry(data.telemetry);
    updateDateTime(data.timestamp);
});

// Fallback polling for data updates
function pollData() {
    fetch('/data')
        .then(response => response.json())
        .then(data => {
            updateTelemetry(data);
            updateDateTime(data.timestamp);
        })
        .catch(error => console.error('Polling error:', error));
}

// Start polling as fallback (will be less frequent than WebSocket updates)
setInterval(pollData, 1000);

// Handle window resize
window.addEventListener('resize', () => {
    if (trajectoryChart) {
        trajectoryChart.resize();
    }
});

// Initial setup
document.addEventListener('DOMContentLoaded', () => {
    initTrajectoryChart();
});
