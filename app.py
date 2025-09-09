from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placement.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}
db = SQLAlchemy(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'student' or 'admin'

class StudentProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(15))
    resume = db.Column(db.String(200))  # Path to resume file
    user = db.relationship('User', backref=db.backref('profile', uselist=False))

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    posted_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    poster = db.relationship('User', backref='jobs_posted')

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='Pending')
    
    # Define relationships with specific backref names to avoid conflicts
    job = db.relationship('Job', backref='job_applications')
    applicant = db.relationship('User', backref='user_applications')

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Create database
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
        else:
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, password=hashed_password, role=role)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful. Please login.')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    jobs = Job.query.all()
    # Fixed: Use proper query to get applications with relationships
    applications = Application.query.options(
        db.joinedload(Application.job),
        db.joinedload(Application.applicant)
    ).all()
    return render_template('admin_dashboard.html', jobs=jobs, applications=applications)

@app.route('/admin/add_job', methods=['GET', 'POST'])
def add_job():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        company = request.form['company']
        description = request.form['description']
        new_job = Job(title=title, company=company, description=description, posted_by=session['user_id'])
        db.session.add(new_job)
        db.session.commit()
        flash('Job posted successfully')
        return redirect(url_for('admin_dashboard'))
    return render_template('add_job.html')

@app.route('/admin/update_status/<int:app_id>', methods=['POST'])
def update_status(app_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    application = Application.query.get_or_404(app_id)
    status = request.form['status']
    if status in ['Pending', 'Accepted', 'Rejected']:
        application.status = status
        db.session.commit()
        flash('Application status updated')
    else:
        flash('Invalid status')
    return redirect(url_for('admin_dashboard'))

@app.route('/student/dashboard')
def student_dashboard():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    jobs = Job.query.all()
    applications = Application.query.filter_by(student_id=session['user_id']).options(
        db.joinedload(Application.job)
    ).all()
    profile = StudentProfile.query.filter_by(user_id=session['user_id']).first()
    return render_template('student_dashboard.html', jobs=jobs, applications=applications, profile=profile)

@app.route('/student/apply/<int:job_id>')
def apply_job(job_id):
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    profile = StudentProfile.query.filter_by(user_id=session['user_id']).first()
    if not profile or not profile.resume:
        flash('Please upload your profile and resume before applying')
        return redirect(url_for('student_dashboard'))
    existing_application = Application.query.filter_by(job_id=job_id, student_id=session['user_id']).first()
    if existing_application:
        flash('You have already applied for this job')
    else:
        new_application = Application(job_id=job_id, student_id=session['user_id'])
        db.session.add(new_application)
        db.session.commit()
        flash('Application submitted successfully')
    return redirect(url_for('student_dashboard'))

@app.route('/student/profile', methods=['GET', 'POST'])
def student_profile():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    profile = StudentProfile.query.filter_by(user_id=session['user_id']).first()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        file = request.files.get('resume')
        resume_path = profile.resume if profile else None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            resume_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if profile:
            profile.name = name
            profile.email = email
            profile.phone = phone
            if resume_path:
                profile.resume = resume_path
        else:
            new_profile = StudentProfile(user_id=session['user_id'], name=name, email=email, phone=phone, resume=resume_path)
            db.session.add(new_profile)
        db.session.commit()
        flash('Profile updated successfully')
        return redirect(url_for('student_dashboard'))
    return render_template('student_profile.html', profile=profile)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)