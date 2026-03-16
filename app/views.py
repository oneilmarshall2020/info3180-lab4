import os
from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from app.models import UserProfile
from app.forms import UploadForm


# ── Helper function (Exercise 6 Step 1) ──────────────────────────────────────
def get_uploaded_images():
    rootdir = os.getcwd()
    images = []
    upload_folder = os.path.join(rootdir, app.config['UPLOAD_FOLDER'])
    for subdir, dirs, files in os.walk(upload_folder):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                images.append(file)
    return images


# ── Flask-Login user loader ───────────────────────────────────────────────────
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(UserProfile, int(user_id))


# ── Home ──────────────────────────────────────────────────────────────────────
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')


# ── Login (Exercise 4) ────────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    from app.forms import LoginForm
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = UserProfile.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('upload'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html', form=form)


# ── Upload (Exercise 5) ───────────────────────────────────────────────────────
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()

    if form.validate_on_submit():
        f = form.file.data
        filename = secure_filename(f.filename)
        f.save(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'], filename))
        flash('File uploaded successfully!', 'success')
        return redirect(url_for('upload'))

    return render_template('upload.html', form=form)


# ── Serve uploaded image (Exercise 6 Step 2) ─────────────────────────────────
@app.route('/uploads/<filename>')
@login_required
def get_image(filename):
    return send_from_directory(
        os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER']),
        filename
    )


# ── Files list (Exercise 6 Step 3) ───────────────────────────────────────────
@app.route('/files')
@login_required
def files():
    images = get_uploaded_images()
    return render_template('files.html', images=images)


# ── Logout (Exercise 7) ───────────────────────────────────────────────────────
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))