from flask import Flask, render_template, url_for, request, redirect, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
import os
import base64
import pytesseract
from PIL import Image

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER_ANSWER'] = 'static/test_bank/'
app.config['UPLOAD_FOLDER_STUDENT'] = 'static/student_papers/'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
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
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError("That username already exists. Please choose a different one.")

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Models for AnswerKey and StudentPaper
class AnswerKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Add name field
    file_path = db.Column(db.String(200), nullable=False)
    answers = db.Column(db.PickleType, nullable=False)

class StudentPaper(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    student_section = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(200), nullable=False)
    answers = db.Column(db.PickleType, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    item_analysis = db.Column(db.PickleType, nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('answer_key.id'), nullable=False)
    exam = db.relationship('AnswerKey', backref=db.backref('student_papers', lazy=True))

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

@app.route('/create-key', methods=['GET', 'POST'])
@login_required
def createKey():
    if request.method == 'POST':
        name = request.form['name']  # Get the name from the form
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER_ANSWER'], filename)
            file.save(filepath)
            extracted_answers = extract_answers(filepath)
            new_answer_key = AnswerKey(name=name, file_path=filepath, answers=extracted_answers)
            db.session.add(new_answer_key)
            db.session.commit()
            flash('Answer key uploaded and processed successfully!')
            return redirect(url_for('home'))
    return render_template('create-key.html')

@app.route('/upload_student_paper', methods=['GET', 'POST'])
@login_required
def upload_student_paper():
    if request.method == 'POST':
        exam_id = request.form['exam']
        student_name = request.form['student_name']
        student_section = request.form['student_section']
        file = request.files['file']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER_STUDENT'], filename)
            file.save(filepath)

            # Assuming you have a function to process the student paper
            extracted_answers = extract_answers(filepath)
            # Assuming you have a function to grade the student paper
            score, item_analysis = grade_student_paper(exam_id, extracted_answers)

            # Save the student paper result in the database
            new_student_paper = StudentPaper(
                student_name=student_name,
                student_section=student_section,
                file_path=filepath,
                answers=extracted_answers,
                score=score,
                item_analysis=item_analysis,
                exam_id=exam_id
            )
            db.session.add(new_student_paper)
            db.session.commit()

            flash('Student paper uploaded and processed successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid file type', 'danger')

    exams = AnswerKey.query.all()  # Assuming you have exams stored in the AnswerKey table
    return render_template('upload_student_paper.html', exams=exams)


# @app.route('/check-exam', methods=["POST", "GET"])
# @login_required
# def checkExam():
#     if request.method == "POST":
#         exam = request.form["selectedExam"]
#         session["exam"] = exam
#         return redirect(url_for("scanTest"))
#     return render_template('check-exam.html')

# @app.route('/scan-test', methods=['GET', 'POST'])
# @login_required
# def scanTest():
#     if "exam" in session:
#         exam = session["exam"]
#         if request.method == 'POST':
#             if 'file' not in request.files:
#                 flash('No file part')
#                 return redirect(request.url)
#             file = request.files['file']
#             if file.filename == '':
#                 flash('No selected file')
#                 return redirect(request.url)
#             if file and allowed_file(file.filename):
#                 filename = secure_filename(file.filename)
#                 filepath = os.path.join(app.config['UPLOAD_FOLDER_STUDENT'], filename)
#                 file.save(filepath)
#                 student_answers = extract_answers(filepath)
#                 score, item_analysis = grade_student_paper(student_answers)
#                 new_student_paper = StudentPaper(file_path=filepath, answers=student_answers, score=score, item_analysis=item_analysis)
#                 db.session.add(new_student_paper)
#                 db.session.commit()
#                 flash('Student paper uploaded and graded successfully!')
#                 return redirect(url_for('results'))
#         return render_template('scan-test.html', exam=exam)
#     return redirect(url_for("checkExam"))

@app.route('/view_results', methods=['GET'])
@login_required
def view_results():
    selected_exam_id = request.args.get('exam')
    exams = AnswerKey.query.all()

    if selected_exam_id:
        student_papers = StudentPaper.query.filter_by(exam_id=selected_exam_id).all()
    else:
        student_papers = StudentPaper.query.all()

    return render_template('view_results.html', student_papers=student_papers, exams=exams, selected_exam=selected_exam_id)

@app.route('/delete_all_student_papers', methods=['POST'])
def delete_all_student_papers():
    try:
        # Delete all records from the StudentPaper table
        db.session.query(StudentPaper).delete()
        db.session.commit()
        flash('All student papers deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting student papers: {str(e)}', 'danger')
    
    return redirect(url_for('view_results'))

@app.route('/view_item_analysis/<int:paper_id>')
@login_required
def view_item_analysis(paper_id):
    student_paper = StudentPaper.query.get_or_404(paper_id)
    return render_template('view_item_analysis.html', student_paper=student_paper)


# @app.route('/save_image', methods=['POST'])
# def save_image():
#     data = request.json
#     image_data = data.get('image_data')

#     if not os.path.exists(IMAGE_DIR):
#         os.makedirs(IMAGE_DIR)

#     image_path = os.path.join(IMAGE_DIR, 'captured_image.png')
#     with open(image_path, 'wb') as f:
#         f.write(base64.b64decode(image_data.split(',')[1]))

#     session['captured_image_path'] = image_path
#     return jsonify({'success': True}), 200

# @app.route('/view-record')
# @login_required
# def viewRecord():
#     return render_template('view-record.html')

# @app.route('/upload', methods=['GET', 'POST'])
# @login_required
# def upload_form():
#     if request.method == 'POST':
#         if 'file' not in request.files:
#             return redirect(request.url)
#         file = request.files['file']
#         if file.filename == '':
#             return redirect(request.url)
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             return redirect(url_for('display_file', filename=filename))
#     return render_template('upload.html')

# @app.route('/display/<filename>')
# @login_required
# def display_file(filename):
#     return render_template('display.html', filename=filename)

# @app.route('/display-captured')
# @login_required
# def display_captured():
#     image_path = session.get('captured_image_path')
#     if image_path:
#         image_url = url_for('static', filename=f'captured_images/{os.path.basename(image_path)}')
#         return render_template('display-captured.html', image_url=image_url)
#     return redirect(url_for('scanTest'))

@app.route('/manage_test_bank')
@login_required
def manage_test_bank():
    answer_keys = AnswerKey.query.all()
    return render_template('manage_test_bank.html', answer_keys=answer_keys)

@app.route('/edit_answer_key/<int:key_id>', methods=['GET', 'POST'])
@login_required
def edit_answer_key(key_id):
    answer_key = AnswerKey.query.get_or_404(key_id)
    if request.method == 'POST':
        try:
            answer_key.name = request.form['name']
            if 'image' in request.files and request.files['image'].filename != '':
                image = request.files['image']
                if allowed_file(image.filename):
                    filename = secure_filename(image.filename)
                    image_path = os.path.join(app.config['UPLOAD_FOLDER_ANSWER'], filename)
                    image.save(image_path)
                    # OCR Processing
                    answer_key.answers = extract_answers(image_path)
                    answer_key.file_path = image_path
            db.session.commit()
            flash('Answer key updated successfully', 'success')
            return redirect(url_for('manage_test_bank'))
        except Exception as e:
            print("Error:", e)
            flash('Failed to update answer key', 'danger')
            return str(e), 500
    return render_template('edit_answer_key.html', answer_key=answer_key)

@app.route('/delete_answer_key/<int:key_id>', methods=['POST'])
@login_required
def delete_answer_key(key_id):
    answer_key = AnswerKey.query.get_or_404(key_id)
    try:
        db.session.delete(answer_key)
        db.session.commit()
        flash('Answer key deleted successfully', 'success')
    except Exception as e:
        print("Error:", e)
        flash('Failed to delete answer key', 'danger')
    return redirect(url_for('manage_test_bank'))

def extract_answers(filepath):
    text = pytesseract.image_to_string(Image.open(filepath))
    answers = text.split('\n')
    return [answer.strip() for answer in answers if answer.strip()]

def grade_student_paper(exam_id, student_answers):
    answer_key = AnswerKey.query.get(exam_id)
    if not answer_key:
        return 0, []

    correct_answers = answer_key.answers
    score = sum(1 for s, c in zip(student_answers, correct_answers) if s == c)
    total_questions = len(correct_answers)
    item_analysis = [{'question': i + 1, 'correct': s == c} for i, (s, c) in enumerate(zip(student_answers, correct_answers))]
    return score, item_analysis

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)