from flask import Flask, render_template, url_for, request, redirect, session, jsonify
import os
import base64

app = Flask(__name__)
app.secret_key = "hello"

# # Directory to save captured images
IMAGE_DIR = os.path.join(app.root_path, 'static/captured_images')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/create-key')
def createKey():
    return render_template('create-key.html')

@app.route('/check-exam', methods=["POST", "GET"])
def checkExam():
    if request.method == "POST":
        exam = request.form["selectedExam"]
        session["exam"] = exam
        return redirect(url_for("scanTest"))
    else:    
        return render_template('check-exam.html')

@app.route('/scan-test')
def scanTest():
    if "exam" in session:
        exam = session["exam"]
        return render_template('scan-test.html', exam=exam)
    else:
        return redirect(url_for("checkExam"))

@app.route('/save_image', methods=['POST'])
def save_image():
    # Get the image data from the request
    data = request.json
    image_data = data.get('image_data')

    # Create the directory if it doesn't exist
    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)

    # Save the image to the directory
    image_path = os.path.join(IMAGE_DIR, 'captured_image.png')
    with open(image_path, 'wb') as f:
        f.write(base64.b64decode(image_data.split(',')[1]))

    # Return the URL of the saved image
    image_url = '/static/captured_images/captured_image.png'
    return jsonify({'success': True, 'image_url': image_url}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)