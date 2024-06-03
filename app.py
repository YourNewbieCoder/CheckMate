from flask import Flask, render_template, url_for, request, redirect, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, length, ValidationError
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import os
import base64

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.secret_key = "hello"

# Directory to save captured images
IMAGE_DIR = os.path.join(app.root_path, 'static/captured_images')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user_usename = User.query.filter_by(username=username.data).first()
        if existing_user_usename:
            raise ValidationError("That username already exists. Please choose a different one.")

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), length(
        min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), length(
        min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('home'))
        return 'Invalid username or password'
    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)

@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    return render_template('home.html')

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/create-key')
def createKey():
    return render_template('create-key.html')

@app.route('/check-exam', methods=["POST", "GET"])
def checkExam():
    if request.method == "POST":
        exam = request.form["selectedExam"]
        session["exam"] = exam
        return redirect(url_for("scanTest"))
    return render_template('check-exam.html')

@app.route('/scan-test')
def scanTest():
    if "exam" in session:
        exam = session["exam"]
        return render_template('scan-test.html', exam=exam)
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

@app.route('/view-record')
def viewRecord():
    return render_template('view-record.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_form():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('display_file', filename=filename))
    return render_template('upload.html')

@app.route('/display/<filename>')
def display_file(filename):
    return render_template('display.html', filename=filename)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)