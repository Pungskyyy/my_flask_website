import os
from flask import Flask, render_template, redirect, url_for, flash, session, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secretkey"  # Ganti dengan secret key aman

# Upload config
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # max 2MB

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

users_db = {}

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=3, max=20)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6, max=30)])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Log In')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data.lower()
        password = form.password.data

        if username in users_db:
            flash('Username already taken, please choose another.', 'error')
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(password)
        users_db[username] = hashed_pw

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data.lower()
        password = form.password.data

        user_pw_hash = users_db.get(username)
        if not user_pw_hash or not check_password_hash(user_pw_hash, password):
            flash('Invalid username or password.', 'error')
            return redirect(url_for('login'))

        session['user'] = username
        # Default profile pic kosong saat login pertama
        if 'profile_pic' not in session:
            session['profile_pic'] = None
        flash('Login successful!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('login.html', form=form)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'profile_pic' not in request.files:
            flash('No file part in the form.', 'error')
            return redirect(url_for('dashboard'))

        file = request.files['profile_pic']
        if file.filename == '':
            flash('No file selected.', 'error')
            return redirect(url_for('dashboard'))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Buat nama file unik dengan username supaya tidak bentrok
            filename = f"{session['user']}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Simpan nama file di session
            session['profile_pic'] = filename
            flash('Foto profil berhasil diupload.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('File tidak diperbolehkan. Gunakan file gambar (png, jpg, jpeg, gif).', 'error')
            return redirect(url_for('dashboard'))

    # Contoh data dummy statistik, pesan, dan quote harian
    stats = {
        'total_logins': 5,
        'tasks_pending': 3,
        'unread_messages': 2,
    }

    messages = [
        {'title': 'Meeting Reminder', 'body': 'Jangan lupa meeting jam 10 pagi.'},
        {'title': 'Update Project', 'body': 'Project sudah mencapai milestone kedua.'},
    ]

    daily_quote = "Success is not final, failure is not fatal: it is the courage to continue that counts."

    return render_template('dashboard.html',
                        username=session['user'],
                        profile_pic=session.get('profile_pic'),
                        stats=stats,
                        messages=messages,
                        daily_quote=daily_quote)

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('profile_pic', None)
    flash('Logged out.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)