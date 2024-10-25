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
const videoElement = document.getElementById('video-stream');
const pc = new RTCPeerConnection({
    iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
});

// Ganti dengan IP address Jetson Orin Nano Anda
const signalingSocket = new WebSocket('ws://192.168.1.94:8080'); 

signalingSocket.onopen = () => {
    console.log('Connected to signaling server'); 
};

signalingSocket.onmessage = async (message) => {
    const data = JSON.parse(message.data);
    if (data.type === 'offer') {
        await pc.setRemoteDescription(new RTCSessionDescription(data));
        const answer = await pc.createAnswer();
        await pc.setLocalDescription(answer);
        signalingSocket.send(JSON.stringify({ sdp: pc.localDescription.sdp, type: 'answer' }));
    } else if (data.candidate) {
        await pc.addIceCandidate(data.candidate);
    }
};

pc.ontrack = (event) => {
    videoElement.srcObject = event.streams[0];
};

// Handle ICE candidates
pc.onicecandidate = (event) => {
    if (event.candidate) {
        signalingSocket.send(JSON.stringify({ candidate: event.candidate }));
    }
};

signalingSocket.onerror = (error) => {
    console.error('WebSocket error:', error);
};

signalingSocket.onclose = () => {
    console.log('Signaling server connection closed');
};
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



// Jalankan fungsi untuk memulai streaming video


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
//updateSOG(10);
//updateCOG(45);

function updateData() {
    fetch('/data')  // Memanggil API Flask yang sudah dibuat
        .then(response => response.json())
        .then(data => {
            // Update SOG (Speed)
            const speed = data.speed.toFixed(2);
            const sogFill = document.getElementById('sog-fill');
            const sogValue = document.getElementById('sog-value');

            // Set width sog bar berdasarkan speed
            const maxSpeed = 30;  // Misalnya max speed 30 knots
            const sogPercent = Math.min((speed / maxSpeed) * 100, 100);
            sogFill.style.width = sogPercent + '%';
            sogValue.textContent = speed + ' knots';

            // Update COG (Heading)
            const heading = data.heading.toFixed(2);
            const cogLine = document.getElementById('cog-line');
            const cogValue = document.getElementById('cog-value');

            // Rotasi garis berdasarkan heading
            cogLine.style.transform = 'rotate(' + heading + 'deg)';
            cogValue.textContent = heading + '°';
        })
        .catch(error => console.error('Error:', error));
}

// Refresh data setiap 1 detik
setInterval(updateData, 1000);