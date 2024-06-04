let currentFacingMode = 'user'; // Default to front camera
let currentStream = null;

async function getStream() {
    // Stop any existing stream
    if (currentStream) {
        currentStream.getTracks().forEach(track => track.stop());
    }

    try {
        currentStream = await navigator.mediaDevices.getUserMedia({ 
            video: { facingMode: currentFacingMode } 
        });

        var video = document.getElementById('video');
        video.srcObject = currentStream;
        updateStatusMessage(`Switched to ${currentFacingMode === 'user' ? 'front' : 'back'} camera.`);
    } catch (err) {
        console.log("An error occurred: " + err);
        updateStatusMessage(`Failed to switch camera: ${err.message}`);
    }
}

function updateStatusMessage(message) {
    document.getElementById('status-msg').innerText = message;
}

document.getElementById('capture-btn').addEventListener('click', function() {
    var video = document.getElementById('video');
    var canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    var context = canvas.getContext('2d');

    // Draw the video frame onto the canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert canvas to data URL
    var dataURL = canvas.toDataURL('image/png');

    // Send the data URL to the server
    fetch('/save_image', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ image_data: dataURL })
    }).then(response => {
        if (response.ok) {
            console.log('Image saved successfully!');
            window.location.href = '/display-captured';
        } else {
            console.error('Failed to save image.');
        }
    }).catch(error => {
        console.error('Error:', error);
    });
});

document.getElementById('switch-btn').addEventListener('click', function() {
    currentFacingMode = (currentFacingMode === 'user') ? 'environment' : 'user';
    getStream();
});

// Initialize with the default camera
getStream();