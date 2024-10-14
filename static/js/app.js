function updateTime() {
    const now = new Date();
    const date = now.toLocaleDateString();
    const time = now.toLocaleTimeString();

    document.getElementById('date').textContent = date;
    document.getElementById('time').textContent = time;
    document.getElementById('underwater-date').textContent = date;
    document.getElementById('underwater-time').textContent = time;
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
window.onload = function() {
    // Set the coordinates for the red and green markers (2m apart)
    // We assume that the whole canvas represents 25x25 meters.
    const redPoints = [
        {x: 22, y: 9}, // Example positions based on the grid layout
        {x: 20.5, y: 12},
        {x: 23.5, y: 15},
        {x:16, y:21},
        {x: 13, y: 21},
        {x: 11, y: 21},
        {x: 3, y: 17},
        {x: 2, y: 13.5},
        {x: 2, y: 10}
    ];

    const greenPoints = [
        {x: 24, y: 9},
        {x: 22.5, y: 12},
        {x: 24.5, y: 15},
        {x: 16, y: 23},
        {x: 13, y: 23},
        {x: 11, y: 23},
        {x: 5, y: 17},
        {x: 4, y: 13.5},
        {x: 4, y: 10}
    ];

    const ctx = document.getElementById('trajectoryChart').getContext('2d');
    const trajectoryChart = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [
                {
                    label: 'Red Points',
                    data: redPoints,
                    backgroundColor: 'red',
                    borderColor: 'red',
                    pointRadius: 5
                },
                {
                    label: 'Green Points',
                    data: greenPoints,
                    backgroundColor: 'green',
                    borderColor: 'green',
                    pointRadius: 5
                },
                {
                    label: 'Trajectory Path',
                    data: redPoints.concat(greenPoints),
                    borderColor: 'black',
                    showLine: true,
                    pointRadius: 0 // Hide points for the line
                }
            ]
        },
        options: {
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    title: {
                        display: true,
                        text: 'X Axis (meters)'
                    },
                    min: 0,
                    max: 25
                },
                y: {
                    type: 'linear',
                    title: {
                        display: true,
                        text: 'Y Axis (meters)'
                    },
                    min: 0,
                    max: 25
                }
            }
        }
    });
};


function updateData() {
    fetch('/data')
        .then(response => response.json())
        .then(data => {
            // Update SOG (Speed Over Ground)
            const speed = data.speed.toFixed(2);
            const sogFill = document.getElementById('sog-fill');
            const sogValue = document.getElementById('sog-value');

            const maxSpeed = 30;  // Maksimum kecepatan yang diharapkan (dalam knot)
            const sogPercent = Math.min((speed / maxSpeed) * 100, 100);
            sogFill.style.width = sogPercent + '%';
            sogValue.textContent = speed + ' knots';

            // Update COG (Course Over Ground)
            const heading = data.heading.toFixed(2);
            const cogLine = document.getElementById('cog-line');
            const cogValue = document.getElementById('cog-value');

            cogLine.style.transform = `rotate(${heading}deg)`;
            cogValue.textContent = heading + '°';

            // Update koordinat
            document.getElementById('surface-coordinate').textContent = `[S ${data.latitude.toFixed(5)} E ${data.longitude.toFixed(5)}]`;
            document.getElementById('underwater-coordinate').textContent = `[S ${data.latitude.toFixed(5)} E ${data.longitude.toFixed(5)}]`;

            // Update trajectory
            if (data.trajectory && data.trajectory.length > 0) {
                drawTrajectory(data.trajectory);
            }

            // Update waktu
            updateTime();
        })
        .catch(error => console.error('Error:', error));
}

// Update waktu setiap detik
setInterval(updateTime, 500);

// Simulasi update level baterai setiap 5 detik
setInterval(() => {
    const level = Math.floor(Math.random() * 100) + 1;
    updateBatteryLevel(level);
}, 5000);

// Refresh data setiap 1 detik
setInterval(updateData, 500);

// Panggil updateData() segera untuk mengisi data awal
updateData();

// Resize trajectory canvas when window is resized
window.addEventListener('resize', () => {
    const canvas = document.getElementById('trajectory-canvas');
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
    updateData();
});