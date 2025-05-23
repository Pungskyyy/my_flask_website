from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo
from datetime import datetime
import os
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# In-memory mock database
users = {}
login_activity = []
user_tasks = {}
user_messages = {}
user_notifications = {}

DAILY_QUOTES = [
    "Hidup adalah petualangan yang berani atau tidak sama sekali.",
    "Kerja keras mengalahkan bakat saat bakat tidak bekerja keras.",
    "Lakukan sesuatu hari ini yang akan membuat dirimu di masa depan berterima kasih."
]

# Flask-WTF Forms
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message='Password harus sama dengan konfirmasi.')
    ])
    submit = SubmitField('Register')

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        uname = form.username.data
        pwd = form.password.data
        if uname in users and users[uname]['password'] == pwd:
            session['username'] = uname
            login_activity.append({'user': uname, 'time': datetime.now()})
            flash('Login berhasil!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login gagal. Cek kembali username atau password.', 'error')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        uname = form.username.data
        pwd = form.password.data
        if uname not in users:
            users[uname] = {'password': pwd, 'profile_pic': None}
            user_tasks[uname] = []
            user_messages[uname] = []
            user_notifications[uname] = []
            flash('Registrasi berhasil! Silakan login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username sudah digunakan.', 'error')
    return render_template('register.html', form=form)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    uname = session['username']
    profile_pic = users[uname].get('profile_pic')

    # Handle profile pic upload
    if request.method == 'POST' and 'profile_pic' in request.files:
        file = request.files['profile_pic']
        if file.filename != '':
            filename = secure_filename(f"{uname}_{file.filename}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            users[uname]['profile_pic'] = filename
            flash('Foto profil berhasil diubah.', 'success')
            return redirect(url_for('dashboard'))

    # Stats
    stats = {
        'total_logins': len([log for log in login_activity if log['user'] == uname]),
        'tasks_pending': len([task for task in user_tasks.get(uname, []) if not task['done']]),
        'unread_messages': len(user_messages.get(uname, [])),
    }

    # Tasks
    if request.args.get('add_task'):
        task_text = request.args.get('add_task')
        if task_text:
            user_tasks[uname].append({'text': task_text, 'done': False})
            flash('Tugas ditambahkan.', 'success')
            return redirect(url_for('dashboard'))

    if request.args.get('toggle_task'):
        index = int(request.args.get('toggle_task'))
        if 0 <= index < len(user_tasks[uname]):
            user_tasks[uname][index]['done'] = not user_tasks[uname][index]['done']
            return redirect(url_for('dashboard'))

    # Messages, Notifications, Quote
    messages = user_messages.get(uname, [])
    notifications = user_notifications.get(uname, [])
    daily_quote = random.choice(DAILY_QUOTES)

    return render_template(
        'dashboard.html',
        username=uname,
        profile_pic=profile_pic,
        stats=stats,
        tasks=user_tasks[uname],
        messages=messages,
        notifications=notifications,
        daily_quote=daily_quote,
        login_activity=login_activity
    )

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Anda telah logout.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
