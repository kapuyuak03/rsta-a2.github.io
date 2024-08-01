function updateTime() {
    const now = new Date();
    const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
    const day = dayNames[now.getDay()];
    const date = now.toLocaleDateString();
    const time = now.toLocaleTimeString();

    document.getElementById('day').textContent = day;
    document.getElementById('date').textContent = date;
    document.getElementById('time').textContent = time;
}

function updateBatteryLevel(level) {
    const batteryLevel = document.getElementById('battery-level');
    batteryLevel.textContent = `${level}%`;
    batteryLevel.style.width = `${level}%`;
    if (level > 50) {
        batteryLevel.style.backgroundColor = '#4caf50';
    } else if (level > 20) {
        batteryLevel.style.backgroundColor = '#ffeb3b';
    } else {
        batteryLevel.style.backgroundColor = '#f44336';
    }
}

// Example of how to update video stream, surface imaging, and other components
function updateVideoStream(stream) {
    const videoStream = document.getElementById('video-stream');
    videoStream.style.backgroundImage = `url(${stream})`;
}

function updateSurfaceImaging(image) {
    const surfaceImaging = document.getElementById('surface-imaging');
    surfaceImaging.style.backgroundImage = `url(${image})`;
}

function updateUnderwaterImaging(image) {
    const underwaterImaging = document.getElementById('underwater-imaging');
    underwaterImaging.style.backgroundImage = `url(${image})`;
}

function updateTrajectoryGraph(graph) {
    const trajectory = document.getElementById('trajectory');
    trajectory.style.backgroundImage = `url(${graph})`;
}

function updateSOG(sog) {
    const sogElement = document.getElementById('sog');
    sogElement.textContent = `SOG: ${sog} knots`;
}

function updateCOG(cog) {
    const cogElement = document.getElementById('cog');
    cogElement.textContent = `COG: ${cog}°`;
}

// Update the time every second
setInterval(updateTime, 1000);

// Simulate battery level updates every 5 seconds
setInterval(() => {
    const level = Math.floor(Math.random() * 100) + 1;
    updateBatteryLevel(level);
}, 5000);

// Example usage of other update functions (replace with real data)
updateVideoStream('path/to/video/stream.jpg');
updateSurfaceImaging('path/to/surface/imaging.jpg');
updateUnderwaterImaging('path/to/underwater/imaging.jpg');
updateTrajectoryGraph('path/to/trajectory/graph.jpg');
updateSOG(10);
updateCOG(45);