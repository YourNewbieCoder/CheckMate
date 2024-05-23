from flask import Flask, render_template, url_for

app = Flask(__name__)

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

@app.route('/check-exam')
def checkExam():
    return render_template('check-exam.html')

if __name__ == "__main__":
    app.run(debug=True, port=5000)