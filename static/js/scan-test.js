// Get access to the webcam
navigator.mediaDevices.getUserMedia({ video: true })
    .then(function(stream) {
        var video = document.getElementById('video');
        video.srcObject = stream;
    })
    .catch(function(err) {
        console.log("An error occurred: " + err);
    });

// Capture image from the webcam
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
        } else {
            console.error('Failed to save image.');
        }
    }).catch(error => {
        console.error('Error:', error);
    });
});
